# Point Claude Code at Argo. Base URL has no /v1.
#
# Source this file, do not execute it:
#
#   export ARGO_USER=ac.yourname
#   source claude-code.sh
#   claude
#
# Note: ANTHROPIC_AUTH_TOKEN is named like a secret but holds your
# username. Keep this in a per-project file you source, not in ~/.bashrc, and don't
# commit it -- the same variable is where a real vendor API key would go later.
# Coding agents run commands and edit files with your permissions, and act on text
# they read from the repo. Use a codeathon workspace, not a privileged checkout.

: "${ARGO_USER:?Set ARGO_USER to your Argonne collaborator username, e.g. ac.jdoe}"

export ANTHROPIC_BASE_URL=https://apps.inside.anl.gov/argoapi
export ANTHROPIC_AUTH_TOKEN=$ARGO_USER
export ANTHROPIC_MODEL=claudeopus5
export ANTHROPIC_SMALL_FAST_MODEL=claudehaiku45

# ANTHROPIC_SMALL_FAST_MODEL handles background tasks; Haiku keeps those cheap.
