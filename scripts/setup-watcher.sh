#!/bin/sh
# Copy script to host
cp /tmp/secret-reload.sh /usr/local/bin/secret-reload.sh
chmod +x /usr/local/bin/secret-reload.sh

# Create systemd service
cat >/etc/systemd/system/secret-reload.service <<EOF
[Unit]
Description=Vault Secret Reload Watcher
After=docker.service

[Service]
ExecStart=/usr/local/bin/secret-reload.sh
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Copy script to host
cp /tmp/cert-reload.sh /usr/local/bin/cert-reload.sh
chmod +x /usr/local/bin/cert-reload.sh

# Create systemd service
cat >/etc/systemd/system/cert-reload.service <<EOF
[Unit]
Description=Vault Cert Reload Watcher
After=docker.service

[Service]
ExecStart=/usr/local/bin/cert-reload.sh
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start via host systemctl
nsenter -t 1 -m -u -n -i /bin/systemctl daemon-reload
nsenter -t 1 -m -u -n -i /bin/systemctl enable --now secret-reload.service
nsenter -t 1 -m -u -n -i /bin/systemctl enable --now cert-reload.service
