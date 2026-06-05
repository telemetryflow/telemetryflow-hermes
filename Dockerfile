# =============================================================================
# TelemetryFlow Hermes - Dockerfile
# =============================================================================
#
# TelemetryFlow Hermes - Community Enterprise Observability Platform (CEOP)
# Copyright (c) 2024-2026 Telemetri Data Indonesia. All rights reserved.
#
# Single-stage build for minimal image size with aggressive CVE patching.
# Uses Debian Trixie (13) base for patched system libraries and strips
# attack-surface packages including pip, tar, mount, and gpg.
#
# Hermes is a Python stdlib-only agent — no pip dependencies required.
# =============================================================================

FROM python:3.13-slim-trixie

ARG VERSION=1.2.0
ARG GIT_COMMIT=unknown
ARG GIT_BRANCH=unknown
ARG BUILD_TIME=unknown

LABEL org.opencontainers.image.title="TelemetryFlow Hermes" \
      org.opencontainers.image.description="Self-improving AI agent integration for TelemetryFlow Observability Platform" \
      org.opencontainers.image.version="1.2.0" \
      org.opencontainers.image.vendor="TelemetryFlow" \
      org.opencontainers.image.authors="Telemetri Data Indonesia <support@telemetryflow.id>" \
      org.opencontainers.image.url="https://telemetryflow.id" \
      org.opencontainers.image.documentation="https://docs.telemetryflow.id" \
      org.opencontainers.image.source="https://github.com/telemetryflow/telemetryflow-hermes" \
      org.opencontainers.image.licenses="Apache-2.0" \
      org.opencontainers.image.base.name="python:3.13-slim-trixie" \
      io.telemetryflow.product="TelemetryFlow Hermes" \
      io.telemetryflow.component="telemetryflow-hermes" \
      io.telemetryflow.platform="CEOP"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TELEMETRYFLOW_API_URL=http://localhost:3000 \
    TELEMETRYFLOW_ENVIRONMENT=production

RUN apt-get update && \
    apt-get dist-upgrade -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN dpkg --remove --force-remove-essential --force-depends \
       perl-base \
       libperl5.40 \
       perl-modules-5.40 \
       ncurses-bin \
       libncurses6 \
       libncursesw6 \
       ncurses-base \
       libtinfo6 \
       gnupg \
       gnupg-utils \
       gpg \
       gpgv \
       gpg-wks-client \
       gpg-wks-server \
       dirmngr \
       libldap-common \
       libldap-2.5-0 \
       libcurl4 \
       curl \
       binutils \
       binutils-common \
       libbinutils \
       libctf0 \
       libctf-nobfd0 \
       tar \
       mount \
       bzip2 \
       login \
       passwd \
       util-linux \
       libmount1 \
       libblkid1 \
       libuuid1 \
       libfdisk1 \
       libsmartcols1 \
       e2fsprogs \
       libext2fs2 \
    || true

RUN python -m pip uninstall -y pip setuptools wheel && \
    rm -rf /usr/local/lib/python3.13/ensurepip \
           /usr/local/lib/python3.13/site-packages/pip* \
           /usr/local/lib/python3.13/site-packages/setuptools* \
           /usr/local/lib/python3.13/site-packages/wheel* \
           /usr/local/bin/pip* \
           /usr/local/lib/python3.13/idlelib \
           /usr/local/lib/python3.13/pydoc_data \
           /usr/local/lib/python3.13/unittest \
           /usr/local/lib/python3.13/lib2to3

RUN apt-get autoremove -y --purge 2>/dev/null || true \
    && apt-get clean 2>/dev/null || true \
    && rm -rf \
       /var/lib/apt/lists/* \
       /tmp/* \
       /var/tmp/* \
       /usr/share/doc/* \
       /usr/share/man/* \
       /usr/share/info/* \
       /var/log/* \
       /var/cache/* \
       /usr/lib/*/libgcrypt* \
       /usr/lib/*/libsasl2*

RUN groupadd -g 10001 telemetryflow && \
    useradd -u 10001 -g telemetryflow -d /home/telemetryflow -m telemetryflow

COPY --chown=telemetryflow:telemetryflow plugins/ /app/plugins/
COPY --chown=telemetryflow:telemetryflow profiles/ /app/profiles/
COPY --chown=telemetryflow:telemetryflow skills/ /app/skills/
COPY --chown=telemetryflow:telemetryflow hooks/ /app/hooks/
COPY --chown=telemetryflow:telemetryflow cron/ /app/cron/
COPY --chown=telemetryflow:telemetryflow config.yaml /app/config.yaml
COPY --chown=telemetryflow:telemetryflow SOUL.md /app/SOUL.md
COPY --chown=telemetryflow:telemetryflow docker-entrypoint.py /app/docker-entrypoint.py

USER telemetryflow

WORKDIR /app

ENTRYPOINT ["python3", "/app/docker-entrypoint.py"]

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 /app/docker-entrypoint.py --check
