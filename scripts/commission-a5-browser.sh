#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STATE_DIR="${A5_BROWSER_STATE_DIR:-$ROOT/configs/state/a5-browser}"
IMAGE="${A5_BROWSER_DOCKER_IMAGE:-grox-a5-browser:1.62.0}"
PROFILE_COMMIT="e3950d9c140d007bd52853b45813c6274b24e36f"
PROFILE_URL="https://raw.githubusercontent.com/microsoft/playwright/${PROFILE_COMMIT}/utils/docker/seccomp_profile.json"
BASE_IMAGE="mcr.microsoft.com/playwright/python@sha256:aa81288e738725378becba5b3e06cb0f3a7f012a610e87e8d767a090ea3f740d"

command -v docker >/dev/null
command -v curl >/dev/null
mkdir -p "$STATE_DIR"
curl -fsSL "$PROFILE_URL" -o "$STATE_DIR/seccomp_profile.json.tmp"
python - <<'PY' "$STATE_DIR/seccomp_profile.json.tmp"
import json, sys
p=sys.argv[1]
raw=json.load(open(p, encoding='utf-8'))
first=(raw.get('syscalls') or [{}])[0]
assert raw.get('defaultAction') == 'SCMP_ACT_ERRNO'
assert set(first.get('names') or ()) >= {'clone','setns','unshare'}
assert first.get('action') == 'SCMP_ACT_ALLOW'
PY
mv "$STATE_DIR/seccomp_profile.json.tmp" "$STATE_DIR/seccomp_profile.json"
docker pull "$BASE_IMAGE"
docker build --pull=false -f "$ROOT/docker/a5-browser/Dockerfile" -t "$IMAGE" "$ROOT"
docker image inspect "$IMAGE" >/dev/null
printf 'A5 browser image: %s\n' "$IMAGE"
printf 'A5 browser image ID: %s\n' "$(docker image inspect --format '{{.Id}}' "$IMAGE")"
printf 'A5 browser seccomp: %s\n' "$STATE_DIR/seccomp_profile.json"
