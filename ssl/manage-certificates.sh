#!/bin/bash

# SSL Certificate Management Script
# Handles certificate renewal, backup, and monitoring

set -e

DOMAIN="safecompanion.ddns.net"
CERT_DIR="/etc/letsencrypt/live/${DOMAIN}"
BACKUP_DIR="/etc/letsencrypt/backup"
LOG_FILE="/var/log/ssl-management.log"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to check certificate expiry
check_expiry() {
    if [ ! -f "${CERT_DIR}/fullchain.pem" ]; then
        log "❌ Certificate file not found: ${CERT_DIR}/fullchain.pem"
        return 1
    fi
    
    local expiry_date=$(openssl x509 -in "${CERT_DIR}/fullchain.pem" -noout -enddate | cut -d= -f2)
    local expiry_epoch=$(date -d "${expiry_date}" +%s)
    local current_epoch=$(date +%s)
    local days_until_expiry=$(( (expiry_epoch - current_epoch) / 86400 ))
    
    log "📅 Certificate expires in ${days_until_expiry} days"
    
    if [ $days_until_expiry -le 30 ]; then
        log "⚠️  Certificate renewal recommended (expires in ${days_until_expiry} days)"
        return 2
    elif [ $days_until_expiry -le 0 ]; then
        log "❌ Certificate has expired!"
        return 3
    else
        log "✅ Certificate is valid (expires in ${days_until_expiry} days)"
        return 0
    fi
}

# Function to backup certificates
backup_certificates() {
    log "📦 Creating certificate backup..."
    
    mkdir -p "$BACKUP_DIR"
    local backup_file="${BACKUP_DIR}/ssl-backup-$(date '+%Y%m%d-%H%M%S').tar.gz"
    
    tar -czf "$backup_file" -C /etc/letsencrypt .
    
    log "✅ Certificate backup created: $backup_file"
    
    # Keep only last 10 backups
    ls -t "${BACKUP_DIR}"/ssl-backup-*.tar.gz | tail -n +11 | xargs rm -f 2>/dev/null || true
}

# Function to renew certificates
renew_certificates() {
    log "🔄 Attempting certificate renewal..."
    
    # Create backup before renewal
    backup_certificates
    
    # Stop nginx container to avoid port conflicts
    if docker ps --format "table {{.Names}}" | grep -q "nginx-proxy"; then
        log "🛑 Stopping nginx container for renewal..."
        docker stop nginx-proxy
        local restart_nginx=true
    else
        local restart_nginx=false
    fi
    
    # Attempt renewal
    if certbot renew --quiet; then
        log "✅ Certificate renewal successful"
        
        # Test nginx configuration
        if nginx -t 2>/dev/null; then
            log "✅ Nginx configuration test passed"
        else
            log "❌ Nginx configuration test failed"
        fi
        
        # Restart nginx container
        if [ "$restart_nginx" = true ]; then
            log "🔄 Restarting nginx container..."
            cd "$(dirname "$0")/.."
            docker-compose up -d nginx
        fi
        
        log "✅ Certificate renewal completed successfully"
    else
        log "❌ Certificate renewal failed"
        
        # Restart nginx container even if renewal failed
        if [ "$restart_nginx" = true ]; then
            log "🔄 Restarting nginx container..."
            cd "$(dirname "$0")/.."
            docker-compose up -d nginx
        fi
        
        return 1
    fi
}

# Function to generate DH parameters
generate_dhparam() {
    local dhparam_file="/etc/letsencrypt/ssl-dhparams.pem"
    
    if [ ! -f "$dhparam_file" ]; then
        log "🔐 Generating DH parameters (this may take a while)..."
        openssl dhparam -out "$dhparam_file" 2048
        log "✅ DH parameters generated: $dhparam_file"
    else
        log "✅ DH parameters already exist: $dhparam_file"
    fi
}

# Function to show certificate info
show_info() {
    if [ ! -f "${CERT_DIR}/fullchain.pem" ]; then
        log "❌ Certificate file not found: ${CERT_DIR}/fullchain.pem"
        return 1
    fi
    
    echo "📋 Certificate Information:"
    echo "=========================="
    openssl x509 -in "${CERT_DIR}/fullchain.pem" -noout -subject -issuer -dates
    echo ""
    
    echo "📋 Certificate Chain:"
    echo "===================="
    openssl x509 -in "${CERT_DIR}/fullchain.pem" -noout -text | grep -A 5 "X509v3 Subject Alternative Name"
    echo ""
    
    check_expiry
}

# Function to monitor certificate
monitor() {
    log "🔍 Starting certificate monitoring..."
    
    while true; do
        if check_expiry; then
            local status=$?
            if [ $status -eq 2 ] || [ $status -eq 3 ]; then
                log "🔄 Certificate needs renewal, attempting automatic renewal..."
                renew_certificates
            fi
        fi
        
        # Check every 12 hours
        sleep 43200
    done
}

# Main script logic
case "${1:-}" in
    "check")
        check_expiry
        ;;
    "backup")
        backup_certificates
        ;;
    "renew")
        renew_certificates
        ;;
    "info")
        show_info
        ;;
    "monitor")
        monitor
        ;;
    "dhparam")
        generate_dhparam
        ;;
    *)
        echo "SSL Certificate Management Script"
        echo "================================="
        echo ""
        echo "Usage: $0 {check|backup|renew|info|monitor|dhparam}"
        echo ""
        echo "Commands:"
        echo "  check    - Check certificate expiry"
        echo "  backup   - Create certificate backup"
        echo "  renew    - Renew certificates"
        echo "  info     - Show certificate information"
        echo "  monitor  - Start certificate monitoring daemon"
        echo "  dhparam  - Generate DH parameters"
        echo ""
        exit 1
        ;;
esac
