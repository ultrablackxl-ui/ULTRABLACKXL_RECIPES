#!/usr/bin/env bash
set -euo pipefail
rm -rf _site
mkdir -p _site
for p in index.html assets data recipes robots.txt sitemap.txt; do
  if [ -e "$p" ]; then
    cp -R "$p" _site/
  fi
done
printf "Cloudflare package ready\n"
