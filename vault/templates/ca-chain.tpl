{{- $role := env "PKI_ROLE" -}}
{{- with secret (printf "pki/issue/%s" $role) (printf "common_name=%s.internal" (env "HOSTNAME")) "ttl=24h" (printf "ip_sans=127.0.0.1,%s" (env "HOST_IP")) "alt_names=postgres,postgres.internal"}}
{{ range .Data.ca_chain }}{{ . }}
{{ end }}
{{- end }}
