#!/bin/bash

install_ssl_config_files() {
  CONF_DIR="/etc/letsencrypt"
  OPTIONS_FILE="$CONF_DIR/options-ssl-nginx.conf"
  DH_FILE="$CONF_DIR/ssl-dhparams.pem"

  # Check if files exist
  if [[ ! -f "$OPTIONS_FILE" || ! -f "$DH_FILE" ]]; then
    echo "Installing missing recommended Certbot SSL config files..."

    apk --no-cache add curl

    # Download directly inside container
    curl -sSfL https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf -o "$OPTIONS_FILE"
    curl -sSfL https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem -o "$DH_FILE"

    echo "SSL config files installed."
  else
    echo "Recommended Certbot SSL config files already present."
  fi
}

update_certificate_staging() {
  certbot certificates
  certbot certonly --staging --webroot -w /var/www/certbot \
    --email "$CERTBOT_EMAIL" \
    -d "$DOMAIN_ROOT" -d "$DOMAIN_NAME" \
    --agree-tos --no-eff-email \
    --force-renewal
  certbot certificates
}

update_certificate() {
  certbot certificates
  certbot certonly --webroot -w /var/www/certbot \
    --email "$CERTBOT_EMAIL" \
    -d "$DOMAIN_ROOT" -d "$DOMAIN_NAME" \
    --agree-tos --no-eff-email \
    --force-renewal
  certbot certificates
}

# Before renewing certificates, ensure proper certbot files present
install_ssl_config_files

# Pull the number of days remaining on cert with matchin domain name.
NUM_DAYS=$(certbot certificates 2>/dev/null | grep -A7 "Certificate Name: $DOMAIN_ROOT" | grep "Expiry Date" | sed -n 's/.*(\(.*\)).*/\1/p' | awk '{print $2}')

if [[ "$NUM_DAYS" =~ ^[0-9]+$ ]]; then
  # If it's a number — do numeric comparison
  if [ "$NUM_DAYS" -le 14 ]; then
    echo "Need to renew certificate"
    update_certificate
  else
    echo "Certificate is valid, not renewing ($NUM_DAYS days left)"
  fi
else
  # Not a number — probably a test cert, should update to ensure
  echo "Test certificate"
  update_certificate
fi
