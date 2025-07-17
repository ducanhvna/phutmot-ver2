#!/bin/bash

# Deploy script for demo.hinosoft.com
# Run this script on your production server

echo "🚀 Starting deployment for demo.hinosoft.com..."

# 1. Stop existing containers
echo "📦 Stopping existing containers..."
docker compose down

# 2. Update system and install dependencies
echo "📥 Installing dependencies..."
sudo apt update
sudo apt install -y nginx certbot python3-certbot-nginx

# 3. Setup SSL certificates with Let's Encrypt
echo "🔒 Setting up SSL certificates..."
if [ ! -f "./nginx/ssl/demo.hinosoft.com.crt" ]; then
    echo "Getting SSL certificates from Let's Encrypt..."
    sudo certbot certonly --standalone -d demo.hinosoft.com -d www.demo.hinosoft.com
    
    # Copy certificates to nginx directory
    sudo cp /etc/letsencrypt/live/demo.hinosoft.com/fullchain.pem ./nginx/ssl/demo.hinosoft.com.crt
    sudo cp /etc/letsencrypt/live/demo.hinosoft.com/privkey.pem ./nginx/ssl/demo.hinosoft.com.key
    
    # Set permissions
    sudo chown $USER:$USER ./nginx/ssl/*
    sudo chmod 644 ./nginx/ssl/*.crt
    sudo chmod 600 ./nginx/ssl/*.key
else
    echo "SSL certificates already exist."
fi

# 4. Build and start containers
echo "🔨 Building and starting containers..."
docker compose build --no-cache
docker compose up -d

# 5. Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# 6. Check service status
echo "🔍 Checking service status..."
docker compose ps

# 7. Test connectivity
echo "🧪 Testing connectivity..."
echo "Testing HTTP redirect..."
curl -I http://demo.hinosoft.com || echo "HTTP test failed"

echo "Testing HTTPS..."
curl -I https://demo.hinosoft.com || echo "HTTPS test failed"

# 8. Setup automatic SSL renewal
echo "🔄 Setting up SSL auto-renewal..."
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet && docker compose restart nginx") | crontab -

# 9. Final status
echo ""
echo "✅ Deployment completed!"
echo ""
echo "🌐 Your application is now available at:"
echo "   https://demo.hinosoft.com"
echo ""
echo "🔧 Admin access:"
echo "   Odoo ERP: https://demo.hinosoft.com/odoo"
echo "   Minio Console: https://demo.hinosoft.com/minio-console"
echo ""
echo "📋 Useful commands:"
echo "   View logs: docker compose logs -f"
echo "   Restart: docker compose restart"
echo "   Stop: docker compose down"
echo "   Update: git pull && docker compose up -d --build"
echo ""
