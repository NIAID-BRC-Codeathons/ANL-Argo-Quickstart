#!/usr/bin/env bash
# Proves network reachability and username auth in one call. Run this first.
#
#   export ARGO_USER=ac.yourname
#   ./00-smoke-test.sh
#
# Requires a connection to the Argonne-auth network.
set -euo pipefail
: "${ARGO_USER:?Set ARGO_USER to your Argonne collaborator username, e.g. ac.jdoe}"

curl -sS https://apps.inside.anl.gov/argoapi/v1/models \
  -H "Authorization: Bearer $ARGO_USER"
