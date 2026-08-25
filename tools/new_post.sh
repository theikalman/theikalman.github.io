#!/usr/bin/env bash
# Generate a new blog post template under _posts/ dated today.
#
# Usage:
#   tools/new_post.sh "My Post Title" [categories] [tags...]
#
# Examples:
#   tools/new_post.sh "TIL: Something Cool"
#   tools/new_post.sh "Deploying My Own Thing" "Dev Documentation" Development Documentation

set -euo pipefail

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 \"Post Title\" [categories] [tags...]" >&2
    exit 1
fi

title="$1"
categories="${2:-Dev Documentation}"
shift $(( $# >= 2 ? 2 : 1 ))
tags=("$@")

if [[ ${#tags[@]} -eq 0 ]]; then
    tags=(Development Documentation)
fi

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
posts_dir="$repo_root/_posts"

date_stamp="$(date +%Y-%m-%d)"
datetime_stamp="$(date +"%Y-%m-%d %H:%M:%S")"

slug="$(echo "$title" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+|-+$//g')"

filename="${date_stamp}-${slug}.md"
filepath="${posts_dir}/${filename}"

if [[ -e "$filepath" ]]; then
    echo "Post already exists: $filepath" >&2
    exit 1
fi

{
    echo "---"
    echo "layout: post"
    echo "title:  \"${title}\""
    echo "date:   ${datetime_stamp}"
    echo "categories: ${categories}"
    echo "tags:"
    for tag in "${tags[@]}"; do
        echo "    - ${tag}"
    done
    echo "---"
    echo
} > "$filepath"

echo "Created $filepath"
