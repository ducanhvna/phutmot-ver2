# Nginx Configuration Structure

## Directory Layout
```
nginx/
├── nginx.conf                    # Main Nginx configuration
├── sites-available/              # Available site configurations
│   └── demo.hinosoft.conf       # Demo site configuration
├── ssl/                         # SSL certificates
│   ├── demo.hinosoft.com.crt   # SSL certificate
│   └── demo.hinosoft.com.key   # SSL private key
└── static/                      # Static files served by Nginx
```

## How it works

### 1. Main Configuration (nginx.conf)
- Defines global Nginx settings
- Includes all `.conf` files from `/etc/nginx/sites-available/`
- Sets up security headers, gzip compression, rate limiting

### 2. Sites Available (sites-available/demo.hinosoft.conf)
- Contains virtual host configuration for demo.hinosoft.com
- Defines upstream servers (goldsun-app, odoo18, minio)
- Handles SSL, proxy pass, and location blocks

### 3. Benefits of this structure:
- **Modular**: Easy to add new domains
- **Standard**: Follows Nginx convention (sites-available/sites-enabled)
- **Scalable**: Can add multiple site configs without touching main config
- **Clean**: Separates global settings from site-specific settings

## Adding new sites

To add a new domain (e.g., api.hinosoft.com):

1. Create new file: `sites-available/api.hinosoft.conf`
2. Add your server configuration
3. Restart Nginx: `docker compose restart nginx`

No need to modify main `nginx.conf` file!

## Example site config structure:
```nginx
# Upstream definitions
upstream api_backend {
    server api_app:3000;
}

# HTTP redirect
server {
    listen 80;
    server_name api.hinosoft.com;
    return 301 https://api.hinosoft.com$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name api.hinosoft.com;
    
    ssl_certificate /etc/nginx/ssl/api.hinosoft.com.crt;
    ssl_certificate_key /etc/nginx/ssl/api.hinosoft.com.key;
    
    location / {
        proxy_pass http://api_backend;
        # ... proxy headers
    }
}
```
