#!/bin/bash
# Script to verify production environment variables

# Colors for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Safe Companion Production Environment Verification ===${NC}"
echo

# Check if container is running
if ! docker ps | grep -q "flask-app"; then
  echo -e "${RED}❌ Flask app container is not running!${NC}"
  echo "Please start the container with: docker compose up -d"
  exit 1
fi

echo -e "${YELLOW}Checking environment variables...${NC}"

# Function to check if a variable is set in the container environment
check_var() {
  local var_name=$1
  local var_value=$(docker exec flask-app bash -c "echo \${$var_name}")
  
  if [ -z "$var_value" ]; then
    echo -e "${RED}❌ $var_name is not set!${NC}"
    return 1
  else
    # Mask sensitive information
    if [[ "$var_name" == *"SECRET"* || "$var_name" == *"KEY"* || "$var_name" == *"PASSWORD"* ]]; then
      echo -e "${GREEN}✅ $var_name is set: ${var_value:0:4}****${NC}"
    else
      echo -e "${GREEN}✅ $var_name is set: $var_value${NC}"
    fi
    return 0
  fi
}

# Check critical environment variables
echo -e "\n${YELLOW}Critical environment variables:${NC}"
critical_vars=("FLASK_SECRET_KEY" "CSRF_SECRET_KEY" "DATABASE_PASSWORD")
critical_failures=0

for var in "${critical_vars[@]}"; do
  check_var "$var" || ((critical_failures++))
done

# Check AWS credentials for email functionality
echo -e "\n${YELLOW}AWS environment variables (for email functionality):${NC}"
aws_vars=("AWS_ACCESS_KEY_ID" "AWS_SECRET_ACCESS_KEY" "AWS_REGION" "SES_SENDER_EMAIL")
aws_failures=0

for var in "${aws_vars[@]}"; do
  check_var "$var" || ((aws_failures++))
done

# Check database configuration
echo -e "\n${YELLOW}Database configuration:${NC}"
db_vars=("DATABASE_URL" "DATABASE_USERNAME" "DATABASE_NAME" "DATABASE_HOST" "DATABASE_PORT")
db_failures=0

for var in "${db_vars[@]}"; do
  check_var "$var" || ((db_failures++))
done

# Check reCAPTCHA configuration
echo -e "\n${YELLOW}reCAPTCHA configuration:${NC}"
recaptcha_vars=("SITEKEY" "RECAPTCHA_SECRET_KEY")
recaptcha_failures=0

for var in "${recaptcha_vars[@]}"; do
  check_var "$var" || ((recaptcha_failures++))
done

# Check persistence file
echo -e "\n${YELLOW}Environment persistence:${NC}"
if docker exec flask-app bash -c "[ -f /app/persistent/env.sh ]"; then
  echo -e "${GREEN}✅ Persistent environment file exists${NC}"
  echo -e "   Variables saved: $(docker exec flask-app bash -c "grep -c '^export' /app/persistent/env.sh")"
else
  echo -e "${RED}❌ Persistent environment file doesn't exist!${NC}"
  echo "   Run: docker exec flask-app ./scripts/persist_env.sh"
fi

# Summary
echo -e "\n${YELLOW}=== Summary ===${NC}"
total_failures=$((critical_failures + aws_failures + db_failures + recaptcha_failures))

if [ $total_failures -eq 0 ]; then
  echo -e "${GREEN}✅ All environment variables are correctly set!${NC}"
else
  echo -e "${RED}❌ $total_failures environment variables are missing or incorrect${NC}"
  
  if [ $critical_failures -gt 0 ]; then
    echo -e "${RED}   - $critical_failures critical variables${NC}"
  fi
  
  if [ $aws_failures -gt 0 ]; then
    echo -e "${YELLOW}   - $aws_failures AWS variables (email functionality might not work)${NC}"
  fi
  
  if [ $db_failures -gt 0 ]; then
    echo -e "${RED}   - $db_failures database variables${NC}"
  fi
  
  if [ $recaptcha_failures -gt 0 ]; then
    echo -e "${YELLOW}   - $recaptcha_failures reCAPTCHA variables (security features might be limited)${NC}"
  fi
  
  echo -e "\nTo fix missing variables:"
  echo "1. Update .env.production file"
  echo "2. Restart the application with: docker compose down && docker compose up -d"
  echo "3. Run: docker exec flask-app ./scripts/persist_env.sh"
fi

echo
echo -e "${YELLOW}=== Verification Complete ===${NC}"
