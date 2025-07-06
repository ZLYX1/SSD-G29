#!/bin/bash

# Deploy SSL certificates using Let's Encrypt for production
# This script sets up SSL certificates for production deployment

set -e

# Configuration
DOMAIN="safecompanion.ddns.net"
EMAIL="admin@${DOMAIN}"  # Replace with your actual email
WEBROOT="/var/www/certbot"

echo "🚀 Deploying SSL certificates for production..."

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "❌ This script must be run as root for Let's Encrypt certificate generation"
   exit 1
fi

# Create webroot directory for ACME challenges
mkdir -p "${WEBROOT}"

# Install certbot if not already installed
if ! command -v certbot &> /dev/null; then
    echo "📦 Installing certbot..."
    if command -v apt-get &> /dev/null; then
        apt-get update
        apt-get install -y certbot
    elif command -v yum &> /dev/null; then
        yum install -y certbot
    else
        echo "❌ Please install certbot manually"
        exit 1
    fi
fi

# Stop nginx if running to avoid port conflicts
if systemctl is-active --quiet nginx; then
    echo "🛑 Stopping nginx temporarily..."
    systemctl stop nginx
    RESTART_NGINX=true
else
    RESTART_NGINX=false
fi

# Stop docker nginx if running
if docker ps --format "table {{.Names}}" | grep -q "nginx-proxy"; then
    echo "🛑 Stopping docker nginx container..."
    docker stop nginx-proxy || true
    RESTART_DOCKER=true
else
    RESTART_DOCKER=false
fi

# Generate certificates using certbot
echo "🔐 Generating Let's Encrypt SSL certificates..."
certbot certonly \
    --standalone \
    --email "${EMAIL}" \
    --agree-tos \
    --no-eff-email \
    --domains "${DOMAIN}" \
    --rsa-key-size 4096 \
    --keep-until-expiring \
    --non-interactive

# Set up automatic renewal
echo "⏰ Setting up automatic certificate renewal..."
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -

# Restart services
if [ "$RESTART_NGINX" = true ]; then
    echo "🔄 Restarting nginx..."
    systemctl start nginx
fi

if [ "$RESTART_DOCKER" = true ]; then
    echo "🔄 Restarting docker services..."
    cd "$(dirname "$0")/.."
    docker-compose up -d nginx
fi

echo "✅ SSL certificates deployed successfully!"
echo "📁 Certificates location: /etc/letsencrypt/live/${DOMAIN}/"
echo "🔄 Automatic renewal configured"
echo ""
echo "📋 Next steps:"
echo "1. Update your DNS records to point to this server"
echo "2. Test the SSL configuration"
echo "3. Enable HSTS preload (optional)"
