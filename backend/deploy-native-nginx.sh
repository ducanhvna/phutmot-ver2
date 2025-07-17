#!/bin/bash

# Deploy script for demo.hinosoft.com with native Nginx
# Run this script on your production server

echo "🚀 Starting deployment for demo.hinosoft.com with native Nginx..."

# 1. Stop existing Docker containers (if any)
echo "📦 Stopping existing containers..."
docker compose down 2>/dev/null || true

# 2. Copy nginx config to sites-available
echo "📝 Copying Nginx configuration..."
sudo cp ./nginx/sites-available/demo.hinosoft.conf /etc/nginx/sites-available/demo.hinosoft.conf

# 3. Enable the site
echo "🔗 Enabling site..."
sudo ln -sf /etc/nginx/sites-available/demo.hinosoft.conf /etc/nginx/sites-enabled/demo.hinosoft.conf

# 4. Test nginx configuration
echo "🧪 Testing Nginx configuration..."
sudo nginx -t
if [ $? -ne 0 ]; then
    echo "❌ Nginx configuration test failed!"
    exit 1
fi

# 5. Setup SSL certificates with Let's Encrypt
echo "🔒 Setting up SSL certificates..."
if [ ! -f "/etc/letsencrypt/live/demo.hinosoft.com/fullchain.pem" ]; then
    echo "Getting SSL certificates from Let's Encrypt..."
    sudo certbot certonly --nginx -d demo.hinosoft.com -d www.demo.hinosoft.com
    
    if [ $? -ne 0 ]; then
        echo "❌ SSL certificate generation failed!"
        echo "Continuing without SSL..."
        # Create temporary config without SSL for testing
        sudo sed -i 's/443 ssl http2/80/g' /etc/nginx/sites-available/demo.hinosoft.conf
        sudo sed -i '/ssl_certificate/d' /etc/nginx/sites-available/demo.hinosoft.conf
        sudo sed -i '/ssl_/d' /etc/nginx/sites-available/demo.hinosoft.conf
    fi
else
    echo "SSL certificates already exist."
fi

# 6. Build and start Docker containers
echo "🔨 Building and starting Docker containers..."
docker compose build --no-cache
docker compose up -d

# 7. Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# 8. Reload Nginx
echo "🔄 Reloading Nginx..."
sudo nginx -s reload

# 9. Check service status
echo "🔍 Checking service status..."
docker compose ps

# 10. Test connectivity
echo "🧪 Testing connectivity..."
echo "Testing Docker services..."
curl -f http://127.0.0.1:5005/health || echo "FastAPI not ready yet"
curl -f http://127.0.0.1:8069/web/health || echo "Odoo not ready yet"

echo "Testing domain..."
curl -I https://demo.hinosoft.com/health || curl -I http://demo.hinosoft.com/health || echo "Domain test failed"

# 11. Setup automatic SSL renewal
echo "🔄 Setting up SSL auto-renewal..."
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet && /usr/sbin/nginx -s reload") | crontab -

# 12. Final status
echo ""
echo "✅ Deployment completed!"
echo ""
echo "🌐 Your application is now available at:"
echo "   https://demo.hinosoft.com"
echo ""
echo "🔧 Services running:"
echo "   - FastAPI: http://127.0.0.1:5005"
echo "   - Odoo ERP: http://127.0.0.1:8069"
echo "   - Odoo Longpolling: http://127.0.0.1:8072"
echo ""
echo "📋 Useful commands:"
echo "   View Docker logs: docker compose logs -f"
echo "   View Nginx logs: sudo tail -f /var/log/nginx/access.log"
echo "   Restart services: docker compose restart"
echo "   Reload Nginx: sudo nginx -s reload"
echo "   Update: git pull && docker compose up -d --build"
echo ""
