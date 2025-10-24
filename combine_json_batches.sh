#!/usr/bin/env bash
# Automatically batch-merge JSON files named with numeric parts.
# Produces files like: blocks_0_99.json, blocks_100_199.json ...
# Usage:
#   ./combine_json_batches.sh [batch_size] [start_index] [end_index]
#
# Example:
#   ./combine_json_batches.sh 100         # Process all
#   ./combine_json_batches.sh 100 500 599 # Process files 500–599 only

set -euo pipefail

batch_size="${1:-100}"
start_index="${2:-}"
end_index="${3:-}"
output_prefix="blocks"

# Find all JSON files that contain "block_<number>_"
mapfile -t files < <(find . -maxdepth 1 -type f -name '*.json' \
  | grep -E 'block_[0-9]+_' \
  | sort -t'_' -k4,4n)

total_files="${#files[@]}"
if (( total_files == 0 )); then
  echo "❌ No JSON files matching '*block_<number>_*.json' found."
  exit 1
fi

echo "📦 Found $total_files JSON files. Batch size = $batch_size"

# Function to extract the numeric part from a filename
extract_num() {
  local f="$1"
  if [[ "$f" =~ block_([0-9]+)_ ]]; then
    echo "${BASH_REMATCH[1]}"
  else
    echo "-1"
  fi
}

# Loop through batches
batch_index=0
for (( i=0; i<total_files; i+=batch_size )); do
  batch_files=( "${files[@]:i:batch_size}" )
  nums=()

  for f in "${batch_files[@]}"; do
    nums+=( "$(extract_num "$f")" )
  done

  IFS=$'\n' sorted_nums=($(sort -n <<<"${nums[*]}"))
  unset IFS

  first_num="${sorted_nums[0]}"
  last_num="${sorted_nums[-1]}"

  # Skip batches outside user-specified range (if given)
  if [[ -n "$start_index" && "$last_num" -lt "$start_index" ]]; then
    continue
  fi
  if [[ -n "$end_index" && "$first_num" -gt "$end_index" ]]; then
    continue
  fi

  output_file="${output_prefix}_${first_num}_${last_num}.json"
  if [[ -f "$output_file" ]]; then
    echo "⚠️  Skipping existing $output_file (already done)"
    continue
  fi

  echo "➡️  Combining files $first_num–$last_num → $output_file"
  ./combine_json.sh "$output_file" "${batch_files[@]}"

  ((batch_index++))
done

echo "✅ Completed $batch_index batches."
