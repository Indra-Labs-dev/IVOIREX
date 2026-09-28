#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")/.."
cleanup() {
  docker compose --profile e2e stop frontend-e2e backend-e2e postgres-e2e >/dev/null 2>&1 || true
  docker compose --profile e2e rm -f frontend-e2e backend-e2e postgres-e2e >/dev/null 2>&1 || true
}
trap cleanup EXIT INT TERM
browser=""
for candidate in chromium chromium-browser google-chrome; do
  if command -v "$candidate" >/dev/null 2>&1; then browser="$(command -v "$candidate")"; break; fi
done
if [ -n "$browser" ] && [ -x frontend/app/node_modules/.bin/playwright ]; then
  docker compose --profile e2e up -d frontend-e2e
  E2E_BASE_URL=http://localhost:43102 E2E_CHROMIUM_EXECUTABLE="$browser" npm --prefix frontend/app run e2e
else
  docker compose --profile e2e run --build --rm campus-e2e
fi
