REGISTRY   ?= # e.g. docker.io/yourname
BE_IMAGE   := $(if $(REGISTRY),$(REGISTRY)/diet-be,diet-be)
FE_IMAGE   := $(if $(REGISTRY),$(REGISTRY)/diet-fe,diet-fe)

# 优先用 git tag，没有 tag 则用 短 commit hash，均附加 dirty 标记
GIT_TAG    := $(shell git describe --tags --exact-match 2>/dev/null)
GIT_HASH   := $(shell git rev-parse --short HEAD 2>/dev/null || echo unknown)
GIT_DIRTY  := $(shell git status --porcelain 2>/dev/null | grep -q . && echo -dirty || echo)
TAG        ?= $(if $(GIT_TAG),$(GIT_TAG),$(GIT_HASH))$(GIT_DIRTY)

BUILDER    := diet-builder

# ── ensure buildx builder exists ─────────────────────────────────────────────
.PHONY: buildx-init
buildx-init:
	@docker buildx inspect $(BUILDER) > /dev/null 2>&1 || \
		docker buildx create --name $(BUILDER) --driver docker-container --bootstrap --use

# ── ARM64 (Apple Silicon / linux/arm64) ─────────────────────────────────────────────
.PHONY: build-arm
build-arm:
	docker build -t $(BE_IMAGE):$(TAG)-arm64 ./diet_be
	docker build -t $(FE_IMAGE):$(TAG)-arm64 ./diet_fe

# ── AMD64 (x86-64 / linux/amd64) — 跨平台用 buildx，x86 原生机器直接 docker build ──
.PHONY: build-amd64
build-amd64: buildx-init
	docker buildx build --builder $(BUILDER) \
		--platform linux/amd64 \
		--load \
		-t $(BE_IMAGE):$(TAG)-amd64 \
		./diet_be
	docker buildx build --builder $(BUILDER) \
		--platform linux/amd64 \
		--load \
		-t $(FE_IMAGE):$(TAG)-amd64 \
		./diet_fe

# ── AMD64 原生构建（────────────────────────────
.PHONY: build-amd64-native
build-amd64-native:
	docker build -t $(BE_IMAGE):$(TAG)-amd64 ./diet_be
	docker build -t $(FE_IMAGE):$(TAG)-amd64 ./diet_fe

# ── Shortcuts ────────────────────────────────────────────────────────────────
.PHONY: clean
clean:
	docker buildx rm $(BUILDER) 2>/dev/null || true
