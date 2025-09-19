# Vault agent config

vault {
  address = env("VAULT_ADDR")
  ca_cert = "/vault/vault-agent/ca.crt"
  retry {
    num_retries = 5
    backoff = "30s"
  }
}

auto_auth {
  method "approle" {
    mount_path = "auth/approle"
    config = {
      role_id_file_path   = "/vault/vault-agent/role_id"
      secret_id_file_path = "/vault/vault-agent/secret_id"
      remove_secret_id_file_after_reading = false
    }
  }

  sink "file" {
    config = {
      path = "/vault/token"
      mode = 0600
    }
  }
}

# Secrets template
template {
  source      = "/vault/templates/secrets.tpl"
  destination = "/secrets/.env"      
  perms       = 0600
  #command     = "systemctl reload myapp"
}

# Certificate templates
template {
  source      = "/vault/templates/cert.tpl"
  destination = "/certs/server.crt"
  perms       = 0644
  #command     = "systemctl reload nginx || true"  # Reload web server if exists
}

template {
  source      = "/vault/templates/key.tpl" 
  destination = "/certs/server.key"
  perms       = 0600
  #command     = "systemctl reload nginx || true"
}

template {
  source      = "/vault/templates/ca-chain.tpl"
  destination = "/certs/ca-chain.crt"
  perms       = 0644
}

log_level = "info"
