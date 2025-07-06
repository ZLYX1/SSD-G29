# SSL/TLS Configuration

This directory contains SSL/TLS configuration scripts and documentation for the SafeCompanion project.

## Quick Start

### Development Environment
```bash
# Generate self-signed certificates for development
./ssl/generate-dev-cert.sh

# Test the configuration
./ssl/test-ssl-config.sh
```

### Production Environment
```bash
# Deploy Let's Encrypt certificates (requires root)
sudo ./ssl/deploy-ssl.sh

# Test the configuration
./ssl/test-ssl-config.sh

# Monitor certificates
./ssl/manage-certificates.sh monitor
```

## Files Overview

| File | Purpose |
|------|---------|
| `deploy-ssl.sh` | Deploy production SSL certificates using Let's Encrypt |
| `generate-dev-cert.sh` | Generate self-signed certificates for development |
| `test-ssl-config.sh` | Test SSL/TLS configuration and certificates |
| `manage-certificates.sh` | Comprehensive certificate management |
| `generate-dhparam.sh` | Generate Diffie-Hellman parameters for PFS |
| `SSL-TLS-DOCUMENTATION.md` | Complete SSL/TLS documentation |

## Security Features

✅ **Strong Encryption**: TLS 1.2 and 1.3 with modern cipher suites  
✅ **Perfect Forward Secrecy**: ECDHE key exchange with DH parameters  
✅ **Security Headers**: HSTS, X-Frame-Options, CSP, and more  
✅ **Certificate Management**: Automated renewal and monitoring  
✅ **HTTP to HTTPS Redirects**: Automatic upgrade to secure connections  

## Certificate Management

### Check Certificate Status
```bash
./ssl/manage-certificates.sh check
```

### Renew Certificates
```bash
./ssl/manage-certificates.sh renew
```

### Backup Certificates
```bash
./ssl/manage-certificates.sh backup
```

### View Certificate Information
```bash
./ssl/manage-certificates.sh info
```

## Docker Integration

The SSL configuration is fully integrated with Docker Compose:

```yaml
nginx:
  volumes:
    - /etc/letsencrypt:/etc/letsencrypt:ro
    - certbot-var:/var/lib/letsencrypt

certbot:
  image: certbot/certbot
  volumes:
    - /etc/letsencrypt:/etc/letsencrypt
    - certbot-var:/var/lib/letsencrypt
```

## Troubleshooting

### Common Issues

1. **Certificate not found**: Run `./ssl/deploy-ssl.sh` (production) or `./ssl/generate-dev-cert.sh` (development)
2. **Nginx configuration errors**: Check with `nginx -t`
3. **SSL test failures**: Ensure services are running and certificates are valid

### Getting Help

- Check the comprehensive documentation in `SSL-TLS-DOCUMENTATION.md`
- Test your configuration with `./ssl/test-ssl-config.sh`
- Use SSL Labs test: https://www.ssllabs.com/ssltest/

## Security Compliance

Our SSL/TLS implementation meets:
- **NIST SP 800-52 Rev. 2** guidelines
- **PCI DSS** requirements
- **OWASP** Transport Layer Security recommendations
- **Mozilla** modern security configuration

## License

This SSL/TLS configuration is part of the SafeCompanion project and follows the same license terms.
