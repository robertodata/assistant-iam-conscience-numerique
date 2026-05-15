#!/bin/bash

echo "=== Déploiement Assistant IAM ==="

cd /home/ec2-user/assistant-iam || exit

echo "=== Git pull ==="
git pull

echo "=== Backend ==="
cd backend || exit
source .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart assistant-iam-backend

echo "=== Frontend ==="
cd ../frontend || exit
npm install
npm run build
sudo systemctl restart assistant-iam-frontend

echo "=== Apache ==="
sudo systemctl reload httpd

echo "=== Déploiement terminé ==="
