FROM mcr.microsoft.com/playwright/python@sha256:aa81288e738725378becba5b3e06cb0f3a7f012a610e87e8d767a090ea3f740d

ARG PLAYWRIGHT_VERSION=1.62.0
RUN python -m pip install --no-cache-dir "playwright==${PLAYWRIGHT_VERSION}" \
    && useradd --create-home --uid 10001 --shell /usr/sbin/nologin groxbrowser

COPY src/grox/tools/browser_worker.py /opt/grox/browser_worker.py
RUN chown root:root /opt/grox/browser_worker.py && chmod 0555 /opt/grox/browser_worker.py

USER groxbrowser
WORKDIR /work
ENV HOME=/home/groxbrowser LANG=C.UTF-8 LC_ALL=C.UTF-8
ENTRYPOINT ["python", "/opt/grox/browser_worker.py"]
