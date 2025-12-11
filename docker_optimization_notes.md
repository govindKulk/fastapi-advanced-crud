# 🐳 Docker Optimization: Complete Guide

A comprehensive guide to Docker optimization techniques, layer caching, multi-stage builds, and best practices.

---

## 📋 Table of Contents

1. [Understanding Docker Layers](#understanding-docker-layers)
2. [Layer Caching Strategy](#layer-caching-strategy)
3. [Multi-Stage Builds](#multi-stage-builds)
4. [Image Size Optimization](#image-size-optimization)
5. [Build Performance](#build-performance)
6. [Security Best Practices](#security-best-practices)
7. [Production Optimizations](#production-optimizations)
8. [Common Anti-Patterns](#common-anti-patterns)
9. [Real-World Examples](#real-world-examples)

---

## 🏗 Understanding Docker Layers

### What is a Docker Layer?

Every instruction in a Dockerfile (`FROM`, `RUN`, `COPY`, `ADD`, etc.) creates a new **read-only layer**. These layers are stacked on top of each other to form the final image.

```dockerfile
FROM python:3.13-slim        # Layer 1: Base image
RUN apt-get update           # Layer 2: Update package list
COPY requirements.txt .      # Layer 3: Copy file
RUN pip install -r requirements.txt  # Layer 4: Install dependencies
COPY . .                     # Layer 5: Copy application
```

**Visual Representation:**
```
┌─────────────────────────┐
│   Layer 5: App Code     │ ← Top (Most recent)
├─────────────────────────┤
│   Layer 4: Dependencies │
├─────────────────────────┤
│   Layer 3: requirements │
├─────────────────────────┤
│   Layer 2: apt-get      │
├─────────────────────────┤
│   Layer 1: Base Image   │ ← Bottom (Oldest)
└─────────────────────────┘
```

### How Layers Work

1. **Immutable**: Once created, layers never change
2. **Cached**: Docker caches layers for faster rebuilds
3. **Shared**: Multiple images can share the same layers
4. **Incremental**: Only changed layers are rebuilt

### Viewing Layers

```bash
# See all layers in an image
docker history myimage:latest

# See layer sizes
docker history --no-trunc --format "table {{.Size}}\t{{.CreatedBy}}" myimage:latest
```

---

## 💾 Layer Caching Strategy

### How Cache Works

Docker checks if a layer can be reused by:
1. Comparing the instruction (e.g., `RUN apt-get update`)
2. Checking if files being copied have changed (for `COPY`/`ADD`)
3. Using cache only if both match exactly

### Cache Invalidation

**Once a layer changes, ALL subsequent layers are invalidated.**

```dockerfile
FROM python:3.13-slim        # ✅ Cached
RUN apt-get update           # ✅ Cached
COPY requirements.txt .      # ✅ Cached
RUN pip install -r requirements.txt  # ✅ Cached
COPY . .                     # ❌ Changed (code updated)
RUN pytest                   # ❌ Must rebuild (cache invalidated)
```

### Optimal Layer Ordering

**Rule: Order instructions from least to most frequently changed**

```dockerfile
# ❌ BAD: Frequently changing code copied early
FROM python:3.13-slim
COPY . .                              # Changes often
RUN pip install -r requirements.txt   # Reinstalls every time
CMD ["python", "app.py"]

# ✅ GOOD: Dependencies installed first
FROM python:3.13-slim
COPY requirements.txt .               # Changes rarely
RUN pip install -r requirements.txt   # Cached unless requirements change
COPY . .                              # Changes often, but deps already cached
CMD ["python", "app.py"]
```

**Frequency Hierarchy (Least → Most Frequent):**
```
Base Image (FROM)
    ↓
System Packages (apt-get, apk)
    ↓
Language Package Manager Setup (pip, npm)
    ↓
Dependency Files (requirements.txt, package.json)
    ↓
Application Code (.)
```

### Example: Python FastAPI Project

```dockerfile
FROM python:3.13-slim

# 1. System dependencies (rarely change)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# 2. Install Poetry (rarely changes)
RUN pip install poetry

# 3. Configure Poetry (never changes)
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1

# 4. Copy only dependency files (change occasionally)
COPY pyproject.toml poetry.lock ./

# 5. Install dependencies (cached unless pyproject.toml/poetry.lock change)
RUN poetry install --only=main --no-root

# 6. Copy application code (changes frequently)
COPY . .

# 7. Runtime configuration (rarely changes)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

**Result:**
- Code changes → Only layer 6 rebuilds (seconds)
- Dependency changes → Layers 5-6 rebuild (1-2 minutes)
- System package changes → Layers 1-6 rebuild (3-5 minutes)

---

## 🏭 Multi-Stage Builds

### What are Multi-Stage Builds?

Multi-stage builds use multiple `FROM` statements in one Dockerfile. Each `FROM` starts a new stage, and you can **copy artifacts from one stage to another**, leaving behind unnecessary files.

### Why Use Multi-Stage Builds?

1. **Smaller Images**: Build tools not included in final image
2. **Security**: Fewer packages = smaller attack surface
3. **Separation**: Build dependencies separate from runtime dependencies
4. **Cleaner**: No need for cleanup scripts

### Basic Syntax

```dockerfile
# Stage 1: Named "builder"
FROM python:3.13-slim AS builder
RUN pip install build-tools
COPY . .
RUN python setup.py build

# Stage 2: Final image (unnamed or named)
FROM python:3.13-slim
# Copy only the built artifacts from "builder"
COPY --from=builder /app/dist /app/dist
CMD ["python", "/app/dist/main.py"]
```

### Real-World Example: Python with Compiled Dependencies

```dockerfile
# ============================================
# Stage 1: Builder - Heavy image with build tools
# ============================================
FROM python:3.13-slim AS builder

WORKDIR /app

# Install build dependencies (gcc, make, etc.)
# These are LARGE but needed to compile packages like psycopg2, cryptography
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \      # ~150MB (gcc, g++, make)
    libpq-dev \           # ~30MB (PostgreSQL headers)
    libssl-dev \          # ~10MB (OpenSSL headers)
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1

# Copy only dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies into .venv
# This compiles wheels for packages that need compilation
RUN poetry install --only=main --no-root

# ============================================
# Stage 2: Runtime - Lightweight image
# ============================================
FROM python:3.13-slim

WORKDIR /app

# Install ONLY runtime libraries (no headers, no compilers)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \              # ~1MB (PostgreSQL client library ONLY)
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash app

# Copy ONLY the virtual environment (already compiled)
COPY --from=builder --chown=app:app /app/.venv /app/.venv

# Copy application code
COPY --chown=app:app . .

USER app

ENV PATH="/app/.venv/bin:$PATH"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

**Size Comparison:**
| Stage | Image Size | Contains |
|-------|-----------|----------|
| Builder | ~800MB | Base + build-essential + libpq-dev + dependencies |
| Runtime | ~400MB | Base + libpq5 + dependencies (compiled) |
| **Savings** | **~400MB (50%)** | Build tools left behind |

### Advanced: Multiple Build Stages

```dockerfile
# Stage 1: Install dependencies
FROM node:18-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Stage 2: Build application
FROM node:18-alpine AS builder
WORKDIR /app
COPY . .
COPY --from=deps /app/node_modules ./node_modules
RUN npm run build

# Stage 3: Run tests
FROM node:18-alpine AS test
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=deps /app/node_modules ./node_modules
RUN npm test

# Stage 4: Production image
FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=deps /app/node_modules ./node_modules
CMD ["node", "dist/index.js"]
```

### Building Specific Stages

```bash
# Build only up to "builder" stage
docker build --target builder -t myapp:builder .

# Build only "test" stage
docker build --target test -t myapp:test .

# Build final image (default: last stage)
docker build -t myapp:latest .
```

---

## 📦 Image Size Optimization

### 1. Choose Slim Base Images

```dockerfile
# ❌ Full image: ~1GB
FROM python:3.13

# ✅ Slim: ~120MB (missing some libraries)
FROM python:3.13-slim

# ✅ Alpine: ~50MB (different package manager, may break some packages)
FROM python:3.13-alpine

# ✅ Distroless: ~50MB (ultra-secure, no shell or package manager)
FROM gcr.io/distroless/python3-debian12
```

**When to use each:**
- **Full**: Development, need all system tools
- **Slim**: Production (recommended for Python)
- **Alpine**: Very size-sensitive, willing to debug musl libc issues
- **Distroless**: Maximum security, no shell access needed

### 2. Combine RUN Commands

Each `RUN` creates a new layer. Combine commands to reduce layers.

```dockerfile
# ❌ BAD: 3 layers, intermediate files saved
FROM python:3.13-slim
RUN apt-get update
RUN apt-get install -y curl
RUN rm -rf /var/lib/apt/lists/*

# ✅ GOOD: 1 layer, cleaned up in same command
FROM python:3.13-slim
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*
```

**Why this works:**
- Docker saves the state AFTER each `RUN`
- Deleting files in a later `RUN` doesn't reduce image size (file still in earlier layer)
- Cleanup must happen in the SAME `RUN` command

### 3. Use .dockerignore

Prevent unnecessary files from being sent to Docker daemon.

```bash
# .dockerignore
__pycache__/
*.pyc
*.pyo
*.pyd
.git/
.gitignore
.env
.venv/
node_modules/
tests/
*.md
.vscode/
.idea/
*.log
.DS_Store
```

**Impact:**
- Faster builds (smaller context sent to daemon)
- Smaller images (fewer files copied)
- Security (secrets not accidentally copied)

### 4. Remove Build Artifacts

```dockerfile
# ❌ BAD: Cache files increase image size
RUN pip install -r requirements.txt

# ✅ GOOD: Disable cache
RUN pip install --no-cache-dir -r requirements.txt

# ✅ BETTER: Multi-stage build (cache in builder only)
FROM python:3.13-slim AS builder
RUN pip install -r requirements.txt  # Cache OK here

FROM python:3.13-slim
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
```

### 5. Leverage Build Arguments

```dockerfile
FROM python:3.13-slim

# Allow customization at build time
ARG INSTALL_DEV_DEPS=false

COPY requirements.txt requirements-dev.txt ./

# Conditional installation
RUN pip install --no-cache-dir -r requirements.txt \
    && if [ "$INSTALL_DEV_DEPS" = "true" ]; then \
        pip install --no-cache-dir -r requirements-dev.txt; \
    fi
```

```bash
# Production build (smaller)
docker build -t myapp:prod .

# Development build (includes dev tools)
docker build --build-arg INSTALL_DEV_DEPS=true -t myapp:dev .
```

---

## ⚡ Build Performance

### 1. Parallel Builds with BuildKit

Enable BuildKit for faster, smarter builds.

```bash
# Enable globally
export DOCKER_BUILDKIT=1

# Or per-build
DOCKER_BUILDKIT=1 docker build -t myapp .
```

**BuildKit Benefits:**
- Parallel layer building
- Better caching (more intelligent)
- Secrets management
- SSH forwarding

### 2. Mount Caches for Package Managers

```dockerfile
# Traditional: Cache cleared after each build
RUN pip install -r requirements.txt

# BuildKit: Cache persists across builds
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt
```

**Other cache mounts:**
```dockerfile
# npm cache
RUN --mount=type=cache,target=/root/.npm \
    npm ci

# apt cache
RUN --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/var/lib/apt \
    apt-get update && apt-get install -y curl

# Poetry cache
RUN --mount=type=cache,target=/root/.cache/pypoetry \
    poetry install
```

### 3. Bind Mounts for Development

```dockerfile
# Use bind mounts in docker-compose for hot reload
services:
  web:
    build: .
    volumes:
      - ./src:/app/src  # Source code mounted (changes reflected immediately)
      - /app/.venv      # Named volume (dependencies persist)
```

### 4. Pre-pull Base Images

```bash
# Pull base images in CI/CD before building
docker pull python:3.13-slim
docker build -t myapp .  # Uses cached base image
```

---

## 🔒 Security Best Practices

### 1. Run as Non-Root User

```dockerfile
# ❌ BAD: Runs as root (UID 0)
FROM python:3.13-slim
COPY . /app
CMD ["python", "app.py"]

# ✅ GOOD: Creates and uses non-root user
FROM python:3.13-slim

# Create user with specific UID (consistency across environments)
RUN useradd --create-home --uid 1000 --shell /bin/bash appuser

# Copy with correct ownership
COPY --chown=appuser:appuser . /app

# Switch to non-root user
USER appuser

CMD ["python", "app.py"]
```

### 2. Don't Install Unnecessary Packages

```dockerfile
# ❌ BAD: Installs recommended packages (bloat)
RUN apt-get install -y curl

# ✅ GOOD: Only required packages
RUN apt-get install -y --no-install-recommends curl
```

### 3. Use Specific Image Tags

```dockerfile
# ❌ BAD: "latest" changes over time (unpredictable)
FROM python:latest

# ❌ BAD: Major version only (3.13.1 → 3.13.2 breaks things)
FROM python:3.13

# ✅ GOOD: Specific version (reproducible builds)
FROM python:3.13.1-slim

# ✅ BETTER: SHA256 digest (immutable)
FROM python:3.13-slim@sha256:abc123...
```

### 4. Scan Images for Vulnerabilities

```bash
# Using Trivy
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image myapp:latest

# Using Snyk
snyk container test myapp:latest

# Using Docker Scout (built-in)
docker scout cves myapp:latest
```

### 5. Don't Store Secrets in Images

```dockerfile
# ❌ BAD: Hardcoded secrets
ENV DATABASE_PASSWORD=supersecret

# ❌ BAD: Secrets in layers
RUN echo "password" > /app/secret.txt && \
    rm /app/secret.txt  # Still in layer!

# ✅ GOOD: Use build secrets (BuildKit)
RUN --mount=type=secret,id=db_password \
    export DB_PASS=$(cat /run/secrets/db_password) && \
    # Use DB_PASS here

# ✅ BEST: Provide secrets at runtime
docker run -e DATABASE_PASSWORD=$DB_PASS myapp
```

---

## 🚀 Production Optimizations

### 1. Health Checks

```dockerfile
# Add health check to Dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Or in docker-compose.yml
services:
  web:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### 2. Signal Handling

```dockerfile
# Use exec form to ensure signals are handled properly
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]

# ❌ BAD: Shell form doesn't forward signals
CMD uvicorn app.main:app --host 0.0.0.0
```

### 3. Metadata Labels

```dockerfile
LABEL maintainer="your.email@example.com"
LABEL version="1.0.0"
LABEL description="FastAPI Task Management System"
LABEL org.opencontainers.image.source="https://github.com/user/repo"
```

### 4. Resource Limits in Compose

```yaml
services:
  web:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

---

## ❌ Common Anti-Patterns

### 1. Installing and Removing in Separate Layers

```dockerfile
# ❌ ANTI-PATTERN
RUN apt-get update
RUN apt-get install -y build-essential
RUN make install
RUN apt-get remove -y build-essential  # Doesn't reduce image size!

# ✅ CORRECT
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && make install \
    && apt-get remove -y build-essential \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*
```

### 2. Using ADD Instead of COPY

```dockerfile
# ❌ BAD: ADD has implicit behaviors (auto-extract, URL support)
ADD app.tar.gz /app

# ✅ GOOD: COPY is explicit
COPY app/ /app/
```

**When to use ADD:**
- Only when you specifically need auto-extraction of tar files

### 3. Forgetting .dockerignore

```dockerfile
# Without .dockerignore
COPY . /app  # Copies .git, node_modules, __pycache__, etc.

# With .dockerignore (lists files to exclude)
COPY . /app  # Only copies necessary files
```

### 4. apt-get upgrade in Dockerfile

```dockerfile
# ❌ BAD: Non-deterministic (different versions over time)
RUN apt-get update && apt-get upgrade -y

# ✅ GOOD: Use newer base image instead
FROM python:3.13.2-slim  # Already has security updates
```

### 5. Not Using Layer Caching Effectively

```dockerfile
# ❌ BAD: Dependencies reinstalled on every code change
COPY . /app
RUN pip install -r requirements.txt

# ✅ GOOD: Dependencies cached separately
COPY requirements.txt /app/
RUN pip install -r requirements.txt
COPY . /app
```

---

## 🎯 Real-World Examples

### Example 1: Python FastAPI (Our Project)

```dockerfile
# ============================================
# Builder Stage
# ============================================
FROM python:3.13-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry

# Configure Poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Copy only dependency files (cache layer)
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --only=main --no-root && rm -rf $POETRY_CACHE_DIR

# ============================================
# Runtime Stage
# ============================================
FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Install only runtime libraries
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --no-log-init --shell /bin/bash app

# Copy virtual environment from builder
COPY --from=builder --chown=app:app /app/.venv /app/.venv

# Copy application code
COPY --chown=app:app . .

USER app

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["uvicorn", "src.app.main:task_app", "--host", "0.0.0.0", "--port", "8000"]
```

### Example 2: Node.js with Next.js

```dockerfile
FROM node:18-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:18-alpine AS builder
WORKDIR /app
COPY . .
COPY --from=deps /app/node_modules ./node_modules
RUN npm run build

FROM node:18-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production

RUN addgroup --system --gid 1001 nodejs \
    && adduser --system --uid 1001 nextjs

COPY --from=builder --chown=nextjs:nodejs /app/.next ./.next
COPY --from=builder --chown=nextjs:nodejs /app/public ./public
COPY --from=deps /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

USER nextjs

EXPOSE 3000

CMD ["npm", "start"]
```

### Example 3: Go Application

```dockerfile
# Builder: Compile Go binary
FROM golang:1.21-alpine AS builder

WORKDIR /app

# Copy go.mod and go.sum first (cache dependencies)
COPY go.mod go.sum ./
RUN go mod download

# Copy source code
COPY . .

# Build static binary
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main .

# Runtime: Ultra-minimal image
FROM scratch

# Copy CA certificates (for HTTPS requests)
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/

# Copy binary
COPY --from=builder /app/main /main

EXPOSE 8080

CMD ["/main"]
```

**Size:** ~10-20MB (vs ~300MB+ with full Go image)

---

## 📊 Optimization Checklist

### Image Size
- [ ] Use slim/alpine base images
- [ ] Multi-stage build for compiled dependencies
- [ ] Combine RUN commands with cleanup
- [ ] Use .dockerignore
- [ ] Remove package manager caches (`--no-cache-dir`)
- [ ] Avoid installing recommended packages (`--no-install-recommends`)

### Build Performance
- [ ] Order layers from least to most frequently changed
- [ ] Copy dependency files before application code
- [ ] Enable BuildKit
- [ ] Use cache mounts for package managers
- [ ] Pre-pull base images in CI/CD

### Security
- [ ] Run as non-root user
- [ ] Use specific image tags (not `latest`)
- [ ] Scan for vulnerabilities
- [ ] Don't store secrets in images
- [ ] Minimize installed packages
- [ ] Keep base images updated

### Production
- [ ] Add health checks
- [ ] Use exec form for CMD/ENTRYPOINT
- [ ] Add metadata labels
- [ ] Configure proper signal handling
- [ ] Set resource limits
- [ ] Use read-only filesystem where possible

---

## 🔗 Additional Resources

### Official Documentation
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Dockerfile Reference](https://docs.docker.com/engine/reference/builder/)
- [Multi-Stage Builds](https://docs.docker.com/build/building/multi-stage/)
- [BuildKit](https://docs.docker.com/build/buildkit/)

### Tools
- [Dive](https://github.com/wagoodman/dive) - Explore image layers
- [Hadolint](https://github.com/hadolint/hadolint) - Dockerfile linter
- [Trivy](https://github.com/aquasecurity/trivy) - Vulnerability scanner
- [Docker Slim](https://github.com/docker-slim/docker-slim) - Minify images

### Commands Reference

```bash
# View image layers and sizes
docker history <image>

# Inspect image metadata
docker inspect <image>

# See disk usage
docker system df

# Remove unused images/containers
docker system prune -a

# Build with BuildKit
DOCKER_BUILDKIT=1 docker build -t myapp .

# Build specific stage
docker build --target builder -t myapp:builder .

# Use build cache from another image
docker build --cache-from myapp:latest -t myapp:new .

# Export image as tar
docker save myapp:latest -o myapp.tar

# Analyze layers with dive
dive myapp:latest
```

---

## 🎓 Key Takeaways

1. **Layer caching is your friend** - Order matters!
2. **Multi-stage builds** reduce image size dramatically
3. **Combine RUN commands** - Cleanup in same layer
4. **Copy dependencies separately** from application code
5. **Use slim base images** unless you need the full version
6. **Run as non-root** for security
7. **Add health checks** for production
8. **Use .dockerignore** to exclude unnecessary files
9. **BuildKit** makes builds faster and smarter
10. **Scan for vulnerabilities** regularly

---

**Remember:** Optimization is about trade-offs. Balance between:
- Image size vs. functionality
- Build speed vs. runtime performance
- Security vs. convenience
- Simplicity vs. optimization

Start simple, measure, then optimize based on actual needs! 🚀
