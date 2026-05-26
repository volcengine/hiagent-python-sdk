"""Internal version & service constants mirroring go/hibot/internal/version."""

DEFAULT_REGION = "cn-north-1"

SERVER_SERVICE = "hibot-server"
GATEWAY_SERVICE = "hibot-gateway"
# AIGW DestService: the TOP gateway registers model/provider
# Actions under this exact service name; "aigw-server" returns InvalidAction.
AIGW_SERVICE = "aigw"
UP_SERVICE = "up"

V1 = "v1"

# TOP-registered API Versions (YYYY-MM-DD).
SERVER_VERSION = "2026-04-23"
CHAT_VERSION = "2026-05-11"
MODEL_VERSION = "2023-08-01"
UP_VERSION = "2022-01-01"
