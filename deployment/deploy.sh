#!/bin/bash

set -e
PRIVKEY=deployment/deployment-push.key

# make deployment ssh identity known to ssh
ssh-keyscan -H $DEPLOYMENT_HOST 2>&1 | tee -a $HOME/.ssh/known_hosts

# decrypt private ssh key used for deployment
openssl aes-256-cbc -K $encrypted_cc51b64530dc_key -iv $encrypted_cc51b64530dc_iv -in deployment/deployment-push.enc -out "$PRIVKEY" -d
chmod 600 "$PRIVKEY"


ssh -i deployment/deployment-push.key $DEPLOYMENT_HOST $1
