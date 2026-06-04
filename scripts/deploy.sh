#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="${REPO_DIR:-/opt/peakpick}"
BRANCH="${BRANCH:-main}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"
ENV_FILE="${ENV_FILE:-.env.production}"
EXPECTED_SERVICES="${EXPECTED_SERVICES:-11}"
FORCE_DEPLOY="${FORCE_DEPLOY:-0}"

cd "$REPO_DIR"

git fetch origin "$BRANCH"
target_revision="$(git rev-parse "origin/$BRANCH")"
deployed_revision="$(cat .deployed-revision 2>/dev/null || true)"
running_services="$(
  docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" ps --services --filter status=running 2>/dev/null | wc -l | tr -d ' '
)"

if [[ "$FORCE_DEPLOY" != "1" && "$target_revision" == "$deployed_revision" && "$running_services" -ge "$EXPECTED_SERVICES" ]]; then
  echo "PeakPick is already running at $target_revision"
  exit 0
fi

git reset --hard "$target_revision"

docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d --build --remove-orphans

for attempt in {1..30}; do
  if curl -fsS http://127.0.0.1:8000/health >/dev/null && curl -fsS http://127.0.0.1:5173/ >/dev/null; then
    echo "$target_revision" > .deployed-revision
    docker image prune -f >/dev/null
    echo "PeakPick deployed at $target_revision"
    exit 0
  fi
  sleep 3
done

docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" ps
echo "PeakPick deployment did not pass health checks" >&2
exit 1

