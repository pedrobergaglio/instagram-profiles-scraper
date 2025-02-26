#!/bin/bash

# Ensure script is run as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit 1
fi

# Set variables
PROJECT_DIR="/home/CODE/instagram-scraper"
SERVICE_NAME="message-generator"

echo "Deploying Message Personalization Tool..."

# Create directories if they don't exist
mkdir -p $PROJECT_DIR/message_personalization/.streamlit

# Copy configuration files
cp message_generator.service /etc/systemd/system/$SERVICE_NAME.service
mkdir -p $PROJECT_DIR/message_personalization/.streamlit/
cp message_personalization/.streamlit/config.toml $PROJECT_DIR/message_personalization/.streamlit/

# Update Apache configuration
cp -f saucotec.conf /etc/apache2/sites-available/
a2ensite saucotec.conf

# Install required packages
pip3 install -r $PROJECT_DIR/message_personalization/requirements.txt

# Set proper permissions
chown -R ubuntu:sharedgroup $PROJECT_DIR
chmod -R 755 $PROJECT_DIR

# Enable and start the service
systemctl daemon-reload
systemctl enable $SERVICE_NAME
systemctl restart $SERVICE_NAME
systemctl restart apache2

echo "Deployment completed!"
echo "Access the application at: https://saucotec.com/message_generator"
