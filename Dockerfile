FROM ivre/client:latest

RUN apt-get update && apt-get install -y python3-venv python3-full psmisc procps && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv

RUN /opt/venv/bin/pip install requests jinja2 netutils ivre

WORKDIR /opt/ivre/ivre-opt

COPY opt/ /opt/ivre/ivre-opt/

RUN chmod +x /opt/ivre/ivre-opt/*.py /opt/ivre/ivre-opt/*.sh

RUN mkdir -p /opt/ivre/ivre-share

VOLUME /opt/ivre/ivre-share

ENV PATH="/opt/venv/bin:$PATH"

# ===== НАСТРОЙКИ ЧЕРЕЗ ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ =====
ENV NETBOX_URL=${NETBOX_URL:-http://netbox:8000}
ENV NETBOX_TOKEN=${NETBOX_TOKEN:-token}

CMD ["python3", "/opt/ivre/ivre-opt/orchestrator.py"]