This directory contains scripts and resources used mostly by CI scripts for
deployment to live website.


## How it works

When a CI build passes all test jobs and is on a specific branch (`develop` for staging, `master` for production), the [deploy.sh](./deploy.sh) script is run to deploy the code on the live server.

The script uses ssh connection to launch script stored on the remote machine (see [update.sh](../server-config/home/zielbruks/update.sh)). This is secured by two factors:
- the ssh private key for this connection is stored in an encrypted file. It's decryption requires private key known only by travis-ci
- on the server there is `~/.ssh/authorized_keys` file specifing that ssh connection authenticated with this key are allowed, but will always trigger one specific command - the `update.sh` script.

The update script takes care of fetching newest commit on the current branch, updating all dependencies, performing bd migrations and restarting the server.