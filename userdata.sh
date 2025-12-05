#!/bin/bash
yum install -y git
git clone https://github.com/AJamell/Jamell-Aidan-Caden-Britan.git
cd /Jamell-Aidan-Caden-Britan
chmod +x redeploy.sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cat << 'EOF' > .env
REGION=us-east-1
BUCKET_NAME=<bucket-name>
EOF

cp image_hosting.service /etc/systemd/system
systemctl daemon-reload
systemctl enable image_hosting.service
systemctl start image_hosting.service