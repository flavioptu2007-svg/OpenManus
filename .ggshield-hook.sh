#!/bin/bash
# GitGuardian ggshield pre-commit/pre-push hook.
#
# Usage: .ggshield-hook.sh <pre-commit|pre-push>
#   Scans staged changes (pre-commit) or commits being pushed (pre-push)
#   for leaked secrets, blocking the commit/push when one is found.
#
# Skips cleanly (exit 0) when GITGUARDIAN_API_KEY is unset, so it never
# blocks development before the user authenticates.
set -euo pipefail

if [ -z "${GITGUARDIAN_API_KEY:-}" ]; then
    echo "ggshield: GITGUARDIAN_API_KEY not set — skipping secret scan (run 'ggshield auth login' or export GITGUARDIAN_API_KEY)"
    exit 0
fi

COMMAND="${1:-pre-commit}"

# Locate ggshield (honor PATH, fall back to ~/.local/bin)
GG="$(command -v ggshield || true)"
if [ -z "$GG" ] && [ -x "$HOME/.local/bin/ggshield" ]; then
    GG="$HOME/.local/bin/ggshield"
fi
if [ -z "$GG" ]; then
    echo "ggshield: binary not found in PATH or ~/.local/bin — skipping secret scan" >&2
    exit 0
fi

exec "$GG" secret scan "$COMMAND"
