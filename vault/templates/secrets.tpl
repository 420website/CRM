{{- $client := env "CLIENT_ID" -}}
{{- with secret (printf "secret/data/%s" $client) }}
{{- range $key, $value := .Data.data }}
{{ $key }}="{{ $value }}"
{{- end }}
{{- end }}

