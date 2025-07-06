#!/bin/bash

# Generate Diffie-Hellman parameters for enhanced SSL security
# This script generates strong DH parameters for Perfect Forward Secrecy

set -e

DH_SIZE=2048
DH_FILE="/etc/letsencrypt/ssl-dhparams.pem"

echo "🔐 Generating Diffie-Hellman parameters..."
echo "📏 Key size: ${DH_SIZE} bits"
echo "📁 Output file: ${DH_FILE}"
echo "⏳ This process may take several minutes..."

# Create directory if it doesn't exist
mkdir -p "$(dirname "$DH_FILE")"

# Generate DH parameters
openssl dhparam -out "$DH_FILE" $DH_SIZE

# Set appropriate permissions
chmod 644 "$DH_FILE"

echo "✅ Diffie-Hellman parameters generated successfully!"
echo "📁 File location: $DH_FILE"
echo "📏 Key size: ${DH_SIZE} bits"
echo ""
echo "💡 These parameters enhance Perfect Forward Secrecy (PFS)"
echo "   and should be used in your SSL/TLS configuration."
