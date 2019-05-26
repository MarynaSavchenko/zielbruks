#!/bin/bash

set -e

ssh -i deployment/deployment-push.key $DEPLOYMENT_HOST $1
