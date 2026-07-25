"""Constants for the Chickadee integration."""

DOMAIN = "chickadee"

# ── Add-on bridge ──────────────────────────────────────────────────────────────
# The integration never talks to a brain provider directly: the Chickadee add-on
# owns engine routing (cloud / BYOK / local) and key custody. The integration is
# the Assist-pipeline surface; the add-on is the brain. One brain POST site total
# (seam rule) — it lives in addon_bridge.call_addon_brain.
#
# Same-box candidates when Supervisor discovery is unavailable (container DNS
# names differ between supervised installs; try both, first reachable wins).
ADDON_PORT = 8099
ADDON_CANDIDATES = (
    "http://local-chickadee:8099",
    "http://addon_local_chickadee:8099",
)

# Shared bridge secret. The add-on writes it to its addon_config folder, which HA
# Core mounts read-only at /config/addon_configs/<slug>/ — readable by this
# integration, NOT by other add-ons. (Pattern inherited from the Dashie bridge
# auth hardening; see that repo's 20260702_BRIDGE_AUTH_HARDENING.md.)
BRIDGE_HEADER = "X-Chickadee-Bridge-Secret"
# Secret location: addon_configs/<installed-slug>/bridge_secret, where the installed
# slug carries an install-dependent prefix (local_chickadee from /addons,
# <repo-hash>_chickadee from a repo channel). addon_bridge globs for *chickadee.

# Add-on HTTP contract (v1). The add-on serves these on its LAN port, authed by
# the bridge secret header. Documented in CONTRACTS.md at repo root — change them
# there and here together, never in one place only.
ADDON_CONVERSE_PATH = "/api/voice/converse"
ADDON_PING_PATH = "/api/ping"

# ── Config entry ───────────────────────────────────────────────────────────────
CONF_ASSISTANT_NAME = "assistant_name"
DEFAULT_ASSISTANT_NAME = "Chickadee"
