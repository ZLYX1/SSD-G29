#!/bin/bash
# Script to update production environment variables after CI/CD deployment

# Check if running with sudo
if [ "$EUID" -ne 0 ]; then
  echo "❌ Please run this script with sudo"
  exit 1
fi

# Path to .env.production file
ENV_FILE=".env.production"

# Function to update an environment variable
update_env_var() {
  local var_name=$1
  local var_value=$2
  
  # Check if the variable exists in the file
  if grep -q "^${var_name}=" "$ENV_FILE"; then
    # Update existing variable
    sed -i "s|^${var_name}=.*|${var_name}=${var_value}|" "$ENV_FILE"
  else
    # Add new variable
    echo "${var_name}=${var_value}" >> "$ENV_FILE"
  fi
  
  echo "✅ Updated ${var_name} in $ENV_FILE"
}

# Make sure we're in the project directory
cd "$(dirname "$0")/.." || exit 1

# Check if .env.production exists
if [ ! -f "$ENV_FILE" ]; then
  echo "❌ $ENV_FILE not found in current directory"
  exit 1
fi

echo "🔧 Updating production environment variables..."

# Ask for each sensitive environment variable
read -p "Enter AWS Access Key ID: " aws_key_id
read -p "Enter AWS Secret Access Key: " aws_secret_key
read -p "Enter AWS Region [us-east-1]: " aws_region
aws_region=${aws_region:-us-east-1}
read -p "Enter S3 Bucket Name [sitssd]: " s3_bucket
s3_bucket=${s3_bucket:-sitssd}
read -p "Enter SES Sender Email: " ses_sender
read -p "Enter Database Password: " db_password
read -p "Generate new Flask Secret Key? [y/N]: " gen_flask_key
read -p "Generate new CSRF Secret Key? [y/N]: " gen_csrf_key
read -p "Enter reCAPTCHA Site Key: " recaptcha_site_key
read -p "Enter reCAPTCHA Secret Key: " recaptcha_secret_key

# Generate random keys if requested
if [[ "$gen_flask_key" =~ ^[Yy]$ ]]; then
  flask_key=$(openssl rand -hex 32)
else
  read -p "Enter Flask Secret Key: " flask_key
fi

if [[ "$gen_csrf_key" =~ ^[Yy]$ ]]; then
  csrf_key=$(openssl rand -hex 32)
else
  read -p "Enter CSRF Secret Key: " csrf_key
fi

# Update the environment file
if [ -n "$aws_key_id" ]; then
  update_env_var "AWS_ACCESS_KEY_ID" "$aws_key_id"
fi

if [ -n "$aws_secret_key" ]; then
  update_env_var "AWS_SECRET_ACCESS_KEY" "$aws_secret_key"
fi

update_env_var "AWS_REGION" "$aws_region"
update_env_var "S3_BUCKET_NAME" "$s3_bucket"

if [ -n "$ses_sender" ]; then
  update_env_var "SES_SENDER_EMAIL" "$ses_sender"
fi

if [ -n "$db_password" ]; then
  update_env_var "DATABASE_PASSWORD" "$db_password"
  # Also update DATABASE_URL to include password
  db_url=$(grep "^DATABASE_URL=" "$ENV_FILE" | cut -d= -f2)
  if [[ "$db_url" == *":@"* ]]; then
    new_db_url=${db_url/:@/:$db_password@}
    update_env_var "DATABASE_URL" "$new_db_url"
  fi
fi

if [ -n "$flask_key" ]; then
  update_env_var "FLASK_SECRET_KEY" "$flask_key"
fi

if [ -n "$csrf_key" ]; then
  update_env_var "CSRF_SECRET_KEY" "$csrf_key"
fi

if [ -n "$recaptcha_site_key" ]; then
  update_env_var "SITEKEY" "$recaptcha_site_key"
fi

if [ -n "$recaptcha_secret_key" ]; then
  update_env_var "RECAPTCHA_SECRET_KEY" "$recaptcha_secret_key"
fi

echo "✅ Environment variables updated successfully!"
echo "🔄 Restart the Docker containers for changes to take effect:"
echo "  $ docker-compose down && docker-compose up -d"
