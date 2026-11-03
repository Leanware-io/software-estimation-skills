#!/usr/bin/env bash
# Package each skill as its own zip for upload in Claude.ai (Settings > Capabilities > Skills).
# Each zip holds one folder named after the skill, with SKILL.md at its root.
set -euo pipefail
cd "$(dirname "$0")/.."
rm -rf dist && mkdir -p dist
for plugin in plugins/*/; do
  name=$(basename "$plugin")
  (cd "$plugin/skills" && zip -qr -X "../../../dist/$name.zip" "$name" -x '*/__pycache__/*' '*.pyc' '*/.DS_Store')
  echo "dist/$name.zip"
done
