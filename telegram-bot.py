#!/usr/bin/env python3
import os
import logging
import requests
from typing import Optional, Union, Dict, Any

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('telegram_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('TelegramBot')

class TelegramBot:
    def __init__(self):
        self.token = self._get_env_var('TELEGRAM_TOKEN')
        self.chat_id = self._get_env_var('TELEGRAM_CHAT_ID')
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        
        # Проверка минимальной конфигурации
        if not self.token or not self.chat_id:
            logger.error("Не заданы TELEGRAM_TOKEN и/или TELEGRAM_CHAT_ID")
            raise ValueError("Требуются TELEGRAM_TOKEN и TELEGRAM_CHAT_ID")

    def _get_env_var(self, var_name: str) -> Optional[str]:
        """Получение переменной окружения с проверкой"""
        value = os.getenv(var_name)
        if not value:
            logger.warning(f"Переменная окружения {var_name} не установлена")
        return value

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
        
        if parse_mode and parse_mode in ['Markdown', 'HTML']:
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

    def format_ci_message(
        self,
        project: str,
        status: str,
        commit_hash: str,
        commit_message: str,
        author: str,
        branch: str,
        url: str
    ) -> str:
        """Форматирование сообщения о CI/CD событии"""
        emoji = "✅" if status.lower() == "success" else "❌"
        return (
            f"{emoji} *{project.upper()} - {status.upper()}*\n\n"
            f"🔹 *Коммит*: [{commit_hash[:7]}]({url}/commit/{commit_hash})\n"
            f"🔹 *Сообщение*: {commit_message}\n"
            f"🔹 *Ветка*: `{branch}`\n"
            f"🔹 *Автор*: {author}\n\n"
            f"[Просмотреть логи]({url}/actions)"
        )

if __name__ == "__main__":
    # Пример использования
    bot = TelegramBot()
    
    # Тестовое сообщение
    bot.send_message("🔔 Бот успешно инициализирован!")
    
    # Пример CI-уведомления
    ci_message = bot.format_ci_message(
        project="Calculator CI",
        status="Success",
        commit_hash="a1b2c3d4e5",
        commit_message="Update calculator functions",
        author="Arabar",
        branch="main",
        url="https://github.com/user/repo"
    )
    
    bot.send_message(ci_message, parse_mode="Markdown")