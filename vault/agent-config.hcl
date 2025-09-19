# Vault agent config
vault {
  ca_cert = "/etc/vault/ca.crt"
  retry {
    num_retries = 5
    backoff = "30s"
  }
}

auto_auth {
  method "approle" {
    mount_path = "auth/approle"
    config = {
      role_id_file_path   = "/etc/vault/role_id"
      secret_id_file_path = "/etc/vault/secret_id"
      remove_secret_id_file_after_reading = false
    }
  }

  sink "file" {
    config = {
      path = "/etc/vault/token"
      mode = 0600
    }
  }
}

template {
  source      = "/etc/vault/templates/secrets.tpl"
  destination = "/etc/vault/secrets/.env"          # Changed to .env
  perms       = 0644
  #command     = "systemctl reload myapp"
}

# Certificate templates
template {
  source      = "/etc/vault/templates/server-cert.tpl"
  destination = "/etc/vault/certs/server.crt"
  perms       = 0644
  #command     = "systemctl reload nginx || true"  # Reload web server if exists
}

template {
  source      = "/etc/vault/templates/server-key.tpl" 
  destination = "/etc/vault/certs/server.key"
  perms       = 0600
  #command     = "systemctl reload nginx || true"
}

template {
  source      = "/etc/vault/templates/ca-chain.tpl"
  destination = "/etc/vault/certs/ca-chain.crt"
  perms       = 0644
}

log_level = "info"
