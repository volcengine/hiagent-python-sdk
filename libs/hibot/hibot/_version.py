"""Internal version & service constants mirroring go/hibot/internal/version."""

DEFAULT_REGION = "cn-north-1"

SERVER_SERVICE = "hibot-server"
UP_SERVICE = "up"

# Backward-compatible aliases. Hibot Actions no longer route to separate
# gateway/model services; callers importing the old constants receive the
# effective server values.
GATEWAY_SERVICE = SERVER_SERVICE
AIGW_SERVICE = SERVER_SERVICE

V1 = "v1"

# TOP-registered API Versions (YYYY-MM-DD).
SERVER_VERSION = "2026-04-23"
UP_VERSION = "2022-01-01"
CHAT_VERSION = SERVER_VERSION
MODEL_VERSION = SERVER_VERSION
