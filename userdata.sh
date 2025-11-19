#!/bin/bash

yum install -y git
git clone https://github.com/cs298f25/Jamell-Aidan-Caden-Britan.git
cd /Jamell-Aidan-Caden-Britan
chmod +x redeploy.sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp image_hosting.service /etc/systemd/system
systemctl enable image_hosting.service
systemctl start image_hosting.service
