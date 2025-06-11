build:
	uv build --package hiagent-components
	uv build --package hiagent-api
	uv build --package hiagent-eva
	uv build --package hiagent-observe

build-component:
	uv build --package hiagent-components

build-api:
	uv build --package hiagent-api

build-eva:
	uv build --package hiagent-eva

build-observe:
	uv build --package hiagent-observe