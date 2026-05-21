#!/bin/bash
# ============================================================
#  Grok2API — Contabo VPS 1-Click Installer
#  Repo: https://github.com/shakapakalo/grok-api-manager
#  Tested on: Ubuntu 22.04 / Debian 12
# ============================================================
set -e

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
log()  { echo -e "${GREEN}[✓]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
err()  { echo -e "${RED}[✗]${NC} $1"; exit 1; }
info() { echo -e "${BLUE}[→]${NC} $1"; }

PORT=8885

echo ""
echo -e "${BLUE}╔══════════════════════════════════════╗${NC}"
echo -e "${BLUE}║      Grok2API — VPS Installer        ║${NC}"
echo -e "${BLUE}║           Port: $PORT               ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════╝${NC}"
echo ""

# ── 0. Root check ────────────────────────────────────────────
[[ $EUID -ne 0 ]] && err "Root se chalao: sudo bash install.sh"

# ── 1. System packages ───────────────────────────────────────
info "System packages install ho rahe hain..."
apt-get update -qq
apt-get install -y -qq curl git sqlite3 2>/dev/null
log "System packages ready"

# ── 2. Install uv (Python manager) ──────────────────────────
info "uv install ho raha hai..."
if ! command -v uv &>/dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
    source "$HOME/.cargo/env" 2>/dev/null || true
fi
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
uv --version &>/dev/null || err "uv install nahi hua"
log "uv ready: $(uv --version)"

# ── 3. Clone / update repo ───────────────────────────────────
REPO_URL="https://github.com/shakapakalo/Grok-API-Manager.git"
INSTALL_DIR="/opt/grok2api"
info "Repo clone ho raha hai → $INSTALL_DIR"
if [ -d "$INSTALL_DIR/.git" ]; then
    warn "Pehle se installed hai — update kar raha hun..."
    cd "$INSTALL_DIR" && git pull origin main
else
    # Sparse checkout — sirf grok2api/ subfolder clone karo
    mkdir -p "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    git init -q
    git remote add origin "$REPO_URL"
    git config core.sparseCheckout true
    echo "grok2api/*" > .git/info/sparse-checkout
    git pull origin main --depth=1 -q
    # grok2api/ contents ko root mein le aao
    shopt -s dotglob
    mv grok2api/* .
    rmdir grok2api
    shopt -u dotglob
fi
log "Code ready"

# ── 4. Python + deps ─────────────────────────────────────────
info "Python 3.11 aur dependencies install ho rahi hain..."
cd "$INSTALL_DIR"
echo "3.11" > .python-version
sed -i 's/requires-python = ">=3.13"/requires-python = ">=3.11"/' pyproject.toml 2>/dev/null || true
uv sync --python 3.11 -q
log "Dependencies ready"

# ── 5. .env setup ────────────────────────────────────────────
SERVER_IP=$(curl -4 -s ifconfig.me 2>/dev/null || hostname -I | awk '{print $1}')
if [ ! -f "$INSTALL_DIR/.env" ]; then
    info ".env configure ho raha hai..."
    cat > "$INSTALL_DIR/.env" << ENVEOF
TZ=Asia/Karachi
LOG_LEVEL=INFO
LOG_FILE_ENABLED=true
ACCOUNT_SYNC_INTERVAL=30
SERVER_HOST=0.0.0.0
SERVER_PORT=$PORT
SERVER_WORKERS=2
HOST_PORT=$PORT
ACCOUNT_STORAGE=local
DATA_DIR=./data
LOG_DIR=./logs
APP_URL=http://${SERVER_IP}:${PORT}
ENVEOF
    log ".env ready (IP: $SERVER_IP, Port: $PORT)"
else
    warn ".env pehle se hai — skip"
fi

# ── 5b. config.toml — local image storage + app_url ─────────
info "Image local storage configure ho raha hai..."
mkdir -p "$INSTALL_DIR/data"
CONFIG_FILE="$INSTALL_DIR/data/config.toml"
SERVER_IP=$(curl -4 -s ifconfig.me 2>/dev/null || hostname -I | awk '{print $1}')
if [ -f "$CONFIG_FILE" ]; then
    # Update existing config
    sed -i "s|app_url = \".*\"|app_url = \"http://${SERVER_IP}:${PORT}\"|g" "$CONFIG_FILE"
    sed -i 's|image_format = "grok_url"|image_format = "local_url"|g' "$CONFIG_FILE"
    sed -i 's|image_format = ".*"|image_format = "local_url"|g' "$CONFIG_FILE"
    sed -i 's|video_format = "grok_url"|video_format = "local_url"|g' "$CONFIG_FILE"
    sed -i 's|video_format = ".*"|video_format = "local_url"|g' "$CONFIG_FILE"
    sed -i 's|imagine_public_image_proxy = false|imagine_public_image_proxy = true|g' "$CONFIG_FILE"
    log "config.toml updated: local_url (image+video) + app_url"
else
    # Create minimal config
    cat > "$CONFIG_FILE" << CFGEOF
[app]
app_key = "grok2api"
app_url = "http://${SERVER_IP}:${PORT}"
api_key = ""
webui_enabled = true
webui_key = ""

[features]
temporary = true
stream = true
thinking = true
image_format = "local_url"
imagine_public_image_proxy = true
video_format = "local_url"

[cache.local]
enabled = true
CFGEOF
    log "config.toml created: local_url mode (image+video)"
fi

# ── 5c. Auto-delete images after 10 minutes (cron) ──────────
info "Auto-delete cron setup ho raha hai (10 min)..."
IMAGE_DIR="$INSTALL_DIR/data/files/images"
VIDEO_DIR="$INSTALL_DIR/data/files/videos"
mkdir -p "$IMAGE_DIR" "$VIDEO_DIR"

CRON_JOB="*/10 * * * * find $IMAGE_DIR -type f -mmin +10 -delete 2>/dev/null; find $VIDEO_DIR -type f -mmin +10 -delete 2>/dev/null"
( crontab -l 2>/dev/null | grep -v "grok2api.*delete\|$IMAGE_DIR"; echo "$CRON_JOB" ) | crontab -
log "Auto-delete cron ready: images/videos delete after 10 min"

# ── 6. systemd service ────────────────────────────────────────
info "systemd service setup ho raha hai..."
UV_BIN=$(which uv 2>/dev/null || echo "$HOME/.local/bin/uv")

cat > /etc/systemd/system/grok2api.service << SVCEOF
[Unit]
Description=Grok2API — OpenAI-Compatible Grok Gateway
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR
ExecStart=$UV_BIN run granian --interface asgi --host 0.0.0.0 --port $PORT --workers 2 app.main:app
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
EnvironmentFile=$INSTALL_DIR/.env
Environment=PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$HOME/.local/bin:$HOME/.cargo/bin

[Install]
WantedBy=multi-user.target
SVCEOF

systemctl daemon-reload
systemctl enable grok2api
systemctl restart grok2api
log "systemd service ready"

# ── 7. Firewall (ufw) ────────────────────────────────────────
if command -v ufw &>/dev/null; then
    info "Firewall port $PORT open kar raha hun..."
    ufw allow $PORT/tcp &>/dev/null || true
    log "Port $PORT open"
fi

# ── 8. Health check ──────────────────────────────────────────
info "Health check (10 second wait)..."
sleep 10
SERVER_IP=$(curl -4 -s ifconfig.me 2>/dev/null || hostname -I | awk '{print $1}')
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:${PORT}/v1/models" 2>/dev/null)

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           🎉 Installation Complete!              ║${NC}"
echo -e "${GREEN}╠══════════════════════════════════════════════════╣${NC}"
echo -e "${GREEN}║${NC}  API Base URL:                                   ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}  http://${SERVER_IP}:${PORT}                     ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}                                                  ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}  Admin Dashboard:                                ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}  http://${SERVER_IP}:${PORT}/admin/login          ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}  Password: grok2api                              ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}                                                  ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}  Web Chat:                                       ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}  http://${SERVER_IP}:${PORT}/webui/chat           ${GREEN}║${NC}"
echo -e "${GREEN}╠══════════════════════════════════════════════════╣${NC}"
echo -e "${GREEN}║${NC}  API Health: HTTP $HTTP_CODE                             ${GREEN}║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Commands:${NC}"
echo "  Status:   systemctl status grok2api"
echo "  Logs:     journalctl -u grok2api -f"
echo "  Restart:  systemctl restart grok2api"
echo "  Update:   cd $INSTALL_DIR && git pull && systemctl restart grok2api"
echo ""
