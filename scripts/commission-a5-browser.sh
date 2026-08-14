#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="${A5_BROWSER_DOCKER_IMAGE:-grox-a5-browser:1.62.0}"
BASE_IMAGE="mcr.microsoft.com/playwright/python@sha256:aa81288e738725378becba5b3e06cb0f3a7f012a610e87e8d767a090ea3f740d"

command -v docker >/dev/null
docker pull "$BASE_IMAGE"
docker build --pull=false -f "$ROOT/docker/a5-browser/Dockerfile" -t "$IMAGE" "$ROOT"
docker image inspect "$IMAGE" >/dev/null
printf 'A5 browser image: %s\n' "$IMAGE"
printf 'A5 browser image ID: %s\n' "$(docker image inspect --format '{{.Id}}' "$IMAGE")"
