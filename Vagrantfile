Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/focal64"
  
  config.vm.provision "shell", inline: <<-SHELL
  # Обновляем пакеты
  sudo apt-get update -y
  sudo apt-get install -y curl wget git
  
  # Устанавливаем Docker
  curl -fsSL https://get.docker.com -o get-docker.sh
  sudo sh get-docker.sh
  sudo usermod -aG docker vagrant
  
  # Устанавливаем kubectl (способ 1)
  sudo apt-get install -y apt-transport-https ca-certificates
  curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.28/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
  echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.28/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list
  sudo apt-get update
  sudo apt-get install -y kubectl
  
  # Устанавливаем Minikube
  curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
  sudo install minikube-linux-amd64 /usr/local/bin/minikube
  rm minikube-linux-amd64
  
  # Запускаем Minikube
  su - vagrant -c "minikube start --driver=docker"
  
  # Настраиваем доступ
  echo 'export KUBECONFIG=/home/vagrant/.kube/config' >> /home/vagrant/.bashrc
  echo 'alias k="kubectl"' >> /home/vagrant/.bashrc
SHELL
  
  config.vm.network "forwarded_port", guest: 3000, host: 3000 # Grafana
  config.vm.network "forwarded_port", guest: 9090, host: 9090 # Prometheus
end