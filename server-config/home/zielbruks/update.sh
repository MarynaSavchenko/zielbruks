#!/bin/bash

set -e

SITE=$1

if [[ "$SITE" != "staging" ]] && [[ "$SITE" != "production" ]]; then
	echo "First argument must specify environment: production | staging"
	exit 2
fi

echo "Updating the $SITE environment"

PIP="$HOME/venv/$SITE/bin/pip"
PYTHON="$HOME/venv/$SITE/bin/python"
CODEDIR="$HOME/$SITE/zielbruks"

cd "$CODEDIR";
git fetch && git reset --hard '@{u}';
"$PIP" install -r ./requirements.txt

"$PYTHON" ./manage.py migrate

# reload gunicorn
pkill -SIGHUP gunicorn;
