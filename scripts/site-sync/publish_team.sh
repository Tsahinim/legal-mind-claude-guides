#!/usr/bin/env bash
# Publishes the current team/ series to legalmind.co.il (as legalmind-il) and verifies it live.
# Usage: bash scripts/site-sync/publish_team.sh
set -euo pipefail
GUIDES="$(cd "$(dirname "$0")/../.." && pwd)"
SITE="$(dirname "$GUIDES")/LEGAL-MIND-AI"
[ -d "$SITE/.git" ] || git clone -q https://github.com/Inbal2025/LEGAL-MIND-AI.git "$SITE"
git -C "$SITE" config core.autocrlf false
git -C "$SITE" pull -q --ff-only
PYTHONIOENCODING=utf-8 py -3 "$GUIDES/scripts/site-sync/team_usage.py" "$SITE"
cd "$SITE"
git add guides/claude-team-usage.html guides/claude-team-usage-guide-1.html guides/claude-team-usage-guide-2.html guides/claude-team-usage-practice.html guides/tu
if git diff --cached --quiet; then echo "site already up to date"; exit 0; fi
SHA=$(git -C "$GUIDES" rev-parse --short HEAD)
git -c user.name=legalmind-il -c user.email=info@legalmind.co.il commit -qm "guides: sync 'מדריך על מנוי Team ב-Claude' from legal-mind-claude-guides@$SHA"
TOKEN=$(gh auth token --user legalmind-il)
git -c credential.helper= -c "credential.helper=!f() { echo username=x-access-token; echo password=$TOKEN; }; f" push -q origin main
for f in claude-team-usage.html claude-team-usage-guide-1.html claude-team-usage-guide-2.html claude-team-usage-practice.html; do
  want=$(git show HEAD:guides/$f | md5sum | cut -c1-32)
  for i in $(seq 1 30); do
    got=$(curl -s "https://www.legalmind.co.il/guides/$f?x=$RANDOM" | md5sum | cut -c1-32)
    [ "$got" = "$want" ] && break; sleep 6
  done
  [ "$got" = "$want" ] && echo "live OK  $f" || echo "NOT LIVE $f"
done
