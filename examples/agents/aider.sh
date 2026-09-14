# Point aider at Argo.
#
# Source this file, do not execute it:
#
#   export ARGO_USER=ac.yourname
#   source aider.sh
#   aider --model openai/claudesonnet5
#
# Note: OPENAI_API_KEY is named like a secret but holds your
# username. Keep this in a per-project file you source, not in ~/.bashrc, and don't
# commit it -- the same variable is where a real vendor API key would go later.
# Coding agents run commands and edit files with your permissions, and act on text
# they read from the repo. Use a codeathon workspace, not a privileged checkout.

: "${ARGO_USER:?Set ARGO_USER to your Argonne collaborator username, e.g. ac.jdoe}"

export OPENAI_API_BASE=https://apps.inside.anl.gov/argoapi/v1
export OPENAI_API_KEY=$ARGO_USER
