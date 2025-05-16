#!/usr/bin/env python3
import os
import logging
import requests
from typing import Optional, Dict, Any, List
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('telegram_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('CICDTelegramBot')

class CICDTelegramBot:
    def __init__(self):
        self.token = self._get_env_var('TELEGRAM_TOKEN')
        self.chat_id = self._get_env_var('TELEGRAM_CHAT_ID')
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        
        # CI/CD переменные
        self.ci_vars = {
            'project': self._get_env_var('GITHUB_REPOSITORY', 'CI_PROJECT_NAME'),
            'status': self._get_env_var('CI_JOB_STATUS', 'GITHUB_WORKFLOW_STATUS'),
            'commit_hash': self._get_env_var('GITHUB_SHA', 'CI_COMMIT_SHA'),
            'commit_message': self._get_env_var('GITHUB_COMMIT_MESSAGE', 'CI_COMMIT_MESSAGE'),
            'author': self._get_env_var('GITHUB_ACTOR', 'CI_COMMIT_AUTHOR'),
            'branch': self._get_env_var('GITHUB_REF_NAME', 'CI_COMMIT_REF_NAME'),
            'run_id': self._get_env_var('GITHUB_RUN_ID', 'CI_PIPELINE_ID'),
            'event': self._get_env_var('GITHUB_EVENT_NAME', 'CI_PIPELINE_SOURCE'),
            'workflow': self._get_env_var('GITHUB_WORKFLOW', 'CI_JOB_NAME'),
            'repo_url': self._get_env_var('GITHUB_REPOSITORY_URL', 'CI_PROJECT_URL')
        }

        if not self.token or not self.chat_id:
            logger.error("Не заданы TELEGRAM_TOKEN и/или TELEGRAM_CHAT_ID")
            raise ValueError("Требуются TELEGRAM_TOKEN и TELEGRAM_CHAT_ID")

    def _get_env_var(self, *var_names: str) -> Optional[str]:
        """Получение переменной окружения с проверкой нескольких вариантов"""
        for var_name in var_names:
            value = os.getenv(var_name)
            if value:
                return value
        logger.warning(f"Не найдены переменные окружения: {var_names}")
        return None

    def _send_request(self, method: str, payload: Dict[str, Any]) -> bool:
        """Базовый метод отправки запроса к Telegram API"""
        try:
            response = requests.post(
                f"{self.base_url}/{method}",
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if not data.get('ok'):
                logger.error(f"Ошибка Telegram API: {data.get('description')}")
                return False
                
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при отправке сообщения: {str(e)}")
            return False

    def get_ci_data(self) -> Dict[str, str]:
        """Получение и форматирование CI/CD данных"""
        repo_url = self.ci_vars['repo_url'] or f"https://github.com/{self.ci_vars['project']}"
        
        # Форматирование commit message (первые 50 символов)
        commit_message = (self.ci_vars['commit_message'] or 'N/A').split('\n')[0][:50]
        
        return {
            'project': (self.ci_vars['project'] or 'Unknown Project').split('/')[-1],
            'status': (self.ci_vars['status'] or 'unknown').lower(),
            'commit_hash': (self.ci_vars['commit_hash'] or '0000000')[:7],
            'commit_message': commit_message,
            'author': self.ci_vars['author'] or 'Unknown',
            'branch': self.ci_vars['branch'] or 'Unknown',
            'run_url': f"{repo_url}/actions/runs/{self.ci_vars['run_id']}" if self.ci_vars['run_id'] else repo_url,
            'commit_url': f"{repo_url}/commit/{self.ci_vars['commit_hash']}" if self.ci_vars['commit_hash'] else repo_url,
            'event': self.ci_vars['event'] or 'push',
            'workflow': self.ci_vars['workflow'] or 'Unknown Workflow',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    def send_ci_notification(self, additional_info: str = "") -> bool:
        """Отправка CI/CD уведомления"""
        ci_data = self.get_ci_data()
        
        emoji = "✅" if ci_data['status'] == 'success' else "❌"
        status_text = "УСПЕШНО" if ci_data['status'] == 'success' else "НЕ УДАЛОСЬ"
        
        message = (
            f"{emoji} *{ci_data['project'].upper()} - {status_text}*\n"
            f"🔹 *Воркфлоу*: `{ci_data['workflow']}`\n"
            f"🔹 *Событие*: `{ci_data['event']}`\n"
            f"🔹 *Ветка*: `{ci_data['branch']}`\n"
            f"🔹 *Коммит*: [{ci_data['commit_hash']}]({ci_data['commit_url']})\n"
            f"🔹 *Сообщение*: {ci_data['commit_message']}\n"
            f"🔹 *Автор*: {ci_data['author']}\n"
            f"🔹 *Время*: {ci_data['timestamp']}\n\n"
            f"[Просмотреть лог]({ci_data['run_url']})"
        )
        
        if additional_info:
            message += f"\n\nℹ️ *Дополнительно:*\n{additional_info}"
            
        return self.send_message(message, parse_mode="Markdown")

    def send_message(
        self,
        text: str,
        parse_mode: Optional[str] = None,
        disable_web_page_preview: bool = True,
        silent: bool = False
    ) -> bool:
        """Отправка текстового сообщения"""
        payload = {
            'chat_id': self.chat_id,
            'text': text,
            'disable_web_page_preview': disable_web_page_preview,
            'disable_notification': silent
        }
        
        if parse_mode and parse_mode in ['MarkdownV2', 'HTML']:
            payload['parse_mode'] = parse_mode
            
        logger.info(f"Отправка сообщения: {text[:50]}...")
        return self._send_request('sendMessage', payload)

    def send_document(
        self,
        file_path: str,
        caption: Optional[str] = None,
        silent: bool = False
    ) -> bool:
        """Отправка файла"""
        try:
            with open(file_path, 'rb') as file:
                files = {'document': file}
                data = {
                    'chat_id': self.chat_id,
                    'disable_notification': silent
                }
                if caption:
                    data['caption'] = caption
                    
                response = requests.post(
                    f"{self.base_url}/sendDocument",
                    files=files,
                    data=data,
                    timeout=30
                )
                response.raise_for_status()
                return True
                
        except Exception as e:
            logger.error(f"Ошибка при отправке файла: {str(e)}")
            return False

if __name__ == "__main__":
    try:
        bot = CICDTelegramBot()
        
        # Основное CI/CD уведомление
        success = bot.send_ci_notification()
        
        # Дополнительное сообщение о результате
        if success:
            bot.send_message("🚀 CI/CD процесс завершен успешно!")
        else:
            bot.send_message("⚠️ Внимание! Обнаружены проблемы в CI/CD процессе!")
            
    except Exception as e:
        logger.error(f"Критическая ошибка: {str(e)}", exc_info=True)