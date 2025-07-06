@echo off
echo Generating SSL certificates for development (with proper key usage)...

rem Create certificate directory
if not exist "C:\letsencrypt\live\safecompanion.ddns.net" mkdir "C:\letsencrypt\live\safecompanion.ddns.net"

rem Generate private key
echo Generating private key...
docker run --rm -v "C:\letsencrypt\live\safecompanion.ddns.net:/certs" alpine/openssl genrsa -out /certs/privkey.pem 2048

rem Create certificate configuration with proper key usage
echo Creating certificate configuration...
echo [req] > "C:\letsencrypt\live\safecompanion.ddns.net\cert.conf"
echo distinguished_name = req_distinguished_name >> "C:\letsencrypt\live\safecompanion.ddns.net\cert.conf"
echo req_extensions = v3_req >> "C:\letsencrypt\live\safecompanion.ddns.net\cert.conf"
echo prompt = no >> "C:\letsencrypt\live\safecompanion.ddns.net\cert.conf"
echo. >> "C:\letsencrypt\live\safecompanion.ddns.net\cert.conf"
echo [req_distinguished_name] >> "C:\letsencrypt\live\safecompanion.ddns.net\cert.conf"
echo C = US >> "C:\letsencrypt\live\safecompanion.ddns.net\cert.conf"
echo ST = State >> "C:\letsencrypt\live\safecompanion.ddns.net\cert.conf"
echo L = City >> "C:\letsencrypt\live\safecompanion.ddns.net\cert.conf"
echo O = Development Organization >> "C:\letsencrypt\live\safecompanion.ddns.net\cert.conf"
echo CN = localhost >> "C:\letsencrypt\live\safecompanion.ddns.net\cert.conf"
echo. >> "C:\letsencrypt\live\safecompanion.ddns.net\cert.conf"
echo [v3_req] >> "C:\letsencrypt\live\safecompanion.ddns.net\cert.conf"
echo basicConstraints = CA:FALSE >> "C:\letsencrypt\live\safecompanion.ddns.net\cert.conf"
echo keyUsage = critical, digitalSignature, keyEncipherment >> "C:\letsencrypt\live\safecompanion.ddns.net\cert.conf"
echo extendedKeyUsage = serverAuth, clientAuth >> "C:\letsencrypt\live\safecompanion.ddns.net\cert.conf"
echo subjectAltName = @alt_names >> "C:\letsencrypt\live\safecompanion.ddns.net\cert.conf"
echo. >> "C:\letsencrypt\live\safecompanion.ddns.net\cert.conf"
echo [alt_names] >> "C:\letsencrypt\live\safecompanion.ddns.net\cert.conf"
echo DNS.1 = localhost >> "C:\letsencrypt\live\safecompanion.ddns.net\cert.conf"
echo DNS.2 = safecompanion.ddns.net >> "C:\letsencrypt\live\safecompanion.ddns.net\cert.conf"
echo DNS.3 = *.safecompanion.ddns.net >> "C:\letsencrypt\live\safecompanion.ddns.net\cert.conf"
echo IP.1 = 127.0.0.1 >> "C:\letsencrypt\live\safecompanion.ddns.net\cert.conf"
echo IP.2 = ::1 >> "C:\letsencrypt\live\safecompanion.ddns.net\cert.conf"

rem Generate certificate signing request
echo Generating certificate signing request...
docker run --rm -v "C:\letsencrypt\live\safecompanion.ddns.net:/certs" alpine/openssl req -new -key /certs/privkey.pem -out /certs/cert.csr -config /certs/cert.conf

rem Generate self-signed certificate
echo Generating self-signed certificate...
docker run --rm -v "C:\letsencrypt\live\safecompanion.ddns.net:/certs" alpine/openssl x509 -req -in /certs/cert.csr -signkey /certs/privkey.pem -out /certs/cert.pem -days 365 -extensions v3_req -extfile /certs/cert.conf

rem Create fullchain.pem
echo Creating fullchain.pem...
copy "C:\letsencrypt\live\safecompanion.ddns.net\cert.pem" "C:\letsencrypt\live\safecompanion.ddns.net\fullchain.pem"

rem Clean up
del "C:\letsencrypt\live\safecompanion.ddns.net\cert.csr"
del "C:\letsencrypt\live\safecompanion.ddns.net\cert.conf"

echo SSL certificates generated successfully with proper key usage!
echo Location: C:\letsencrypt\live\safecompanion.ddns.net\
echo.
echo Next steps:
echo 1. Restart Docker containers: docker restart nginx-proxy
echo 2. Access application: https://localhost or https://127.0.0.1
