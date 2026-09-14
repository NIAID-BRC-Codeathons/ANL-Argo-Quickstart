# Environment for LangChain and LlamaIndex against Argo.
#
# Source this file, do not execute it:
#
#   export ARGO_USER=ac.yourname
#   source env.sh

: "${ARGO_USER:?Set ARGO_USER to your Argonne collaborator username, e.g. ac.jdoe}"

export OPENAI_API_KEY=$ARGO_USER
export OPENAI_BASE_URL=https://apps.inside.anl.gov/argoapi/v1
