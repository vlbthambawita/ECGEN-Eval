#!/usr/bin/env bash
# Render every docs/diagrams/*.d2 diagram to light and dark SVGs in docs/assets/diagrams/.
#
# Requires D2 >= 0.7 (https://d2lang.com):  curl -fsSL https://d2lang.com/install.sh | sh -s --
# Usage:  bash docs/diagrams/render.sh
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
out="$here/../assets/diagrams"
mkdir -p "$out"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

for mode in light dark; do
  cp "$here"/*.d2 "$tmp"/
  cp "$here/palette-$mode.d2" "$tmp/_palette.d2"
  for src in "$here"/*.d2; do
    name="$(basename "$src" .d2)"
    [[ "$name" == palette-* ]] && continue
    d2 --layout=elk "$tmp/$name.d2" "$out/$name-$mode.svg"
  done
done
echo "Rendered diagrams to $out"
