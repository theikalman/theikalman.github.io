#!/usr/bin/env bash
# List all categories and/or tags used across _posts/ front matter.
#
# Usage:
#   tools/list_taxonomy.sh [categories|tags|all]
#
# With no argument (or "all"), prints both sections.

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
posts_dir="$repo_root/_posts"

mode="${1:-all}"

list_categories() {
    awk '
        FNR==1 { fm=0 }
        /^---$/ { fm++; next }
        fm==1 && /^categories:/ {
            sub(/^categories:[ \t]*/, "");
            if (length($0) > 0) print;
        }
    ' "$posts_dir"/*.md | sort -f -u
}

list_tags() {
    awk '
        FNR==1 { fm=0; in_tags=0 }
        /^---$/ { fm++; next }
        fm==1 && /^tags:/ { in_tags=1; next }
        fm==1 && in_tags && /^[^ \t-]/ { in_tags=0 }
        fm==1 && in_tags && /^[ \t]*-/ {
            sub(/^[ \t]*-[ \t]*/, "");
            print;
        }
    ' "$posts_dir"/*.md | sort -f -u
}

case "$mode" in
    categories)
        list_categories
        ;;
    tags)
        list_tags
        ;;
    all)
        echo "Categories:"
        list_categories | sed 's/^/  - /'
        echo
        echo "Tags:"
        list_tags | sed 's/^/  - /'
        ;;
    *)
        echo "Usage: $0 [categories|tags|all]" >&2
        exit 1
        ;;
esac
