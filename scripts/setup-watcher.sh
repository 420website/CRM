#!/bin/sh
# Copy scripts to host
cp /tmp/secret-reload.sh /host/usr/local/bin/secret-reload.sh
chmod +x /host/usr/local/bin/secret-reload.sh
cp /tmp/cert-reload.sh /host/usr/local/bin/cert-reload.sh
chmod +x /host/usr/local/bin/cert-reload.sh

# Create service files
cat >/host/etc/systemd/system/secret-reload.service <<EOF
[Unit]
Description=Vault Secret Reload Watcher
After=docker.service

[Service]
ExecStart=/usr/local/bin/secret-reload.sh
Restart=always

[Install]
WantedBy=multi-user.target
EOF

cat >/host/etc/systemd/system/cert-reload.service <<EOF
[Unit]
Description=Vault Cert Reload Watcher
After=docker.service

[Service]
ExecStart=/usr/local/bin/cert-reload.sh
Restart=always

[Install]
WantedBy=multi-user.target
EOF
