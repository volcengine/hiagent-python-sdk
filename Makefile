build: build-component build-api build-eva build-observe build-hibot

build-component:
	uv build --package hiagent-components

build-api:
	uv build --package hiagent-api

build-eva:
	uv build --package hiagent-eva

build-observe:
	uv build --package hiagent-observe

build-hibot:
	uv build --package hibot
