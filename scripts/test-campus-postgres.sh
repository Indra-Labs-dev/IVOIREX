#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")/.."
cleanup() {
  docker compose --profile test stop postgres-campus-test >/dev/null 2>&1 || true
  docker compose --profile test rm -f postgres-campus-test >/dev/null 2>&1 || true
}
trap cleanup EXIT INT TERM
docker compose --profile test run --build --rm campus-integration
