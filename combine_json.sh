#!/usr/bin/env bash
# Usage: ./combine_json.sh output.json file1.json file2.json ... fileN.json

set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 output.json input1.json input2.json ..."
  exit 1
fi

output="$1"
shift

# Ensure we start fresh
tmpfile=$(mktemp)
trap 'rm -f "$tmpfile"' EXIT

echo "[" > "$tmpfile"

first=true
for f in "$@"; do
  if [ ! -f "$f" ]; then
    echo "Warning: file '$f' not found, skipping." >&2
    continue
  fi
  if [ "$first" = true ]; then
    first=false
  else
    echo "," >> "$tmpfile"
  fi
  cat "$f" >> "$tmpfile"
done

echo "]" >> "$tmpfile"
mv "$tmpfile" "$output"
echo "✅ Combined $(( $# )) files into '$output'"
