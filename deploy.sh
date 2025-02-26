#!/bin/bash

# Ensure script is run as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit 1
fi

# Set variables
PROJECT_DIR="/home/CODE/instagram-scraper"
DOCKER_SERVICE="message_generator"

echo "Deploying Message Generator using Docker..."

# Install Docker if not installed
if ! [ -x "$(command -v docker)" ]; then
  echo "Installing Docker..."
  apt-get update
  apt-get install -y docker.io docker-compose
  systemctl enable --now docker
fi

# Copy Apache configuration
cp -f saucotec.conf /etc/apache2/sites-enabled/
a2ensite saucotec.conf
a2enmod proxy proxy_http proxy_wstunnel headers

# Navigate to project directory
cd $PROJECT_DIR

# Build and start Docker container
docker-compose down
docker-compose up --build -d

# Enable Docker to start on boot
systemctl enable docker

# Restart Apache
systemctl restart apache2

echo "Docker deployment completed!"
echo "Access the application at: https://saucotec.com/message_generator"