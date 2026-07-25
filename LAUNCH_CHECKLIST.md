# Chickadee launch-day checklist

Everything that happens the day the repos flip public. Nothing here runs early —
several steps leak the name (domain registration is discoverable, brands PR is
public). Order matters within sections.

## 0. Pre-flip sweep (do first, while still private)

- [ ] **Scrub the dev rig hostnames**: `chickadee-addons/tools/*.py` hard-code
      `ha.dashieapp.com` (John's own HA box). Genericize to an env var
      (`CHICKADEE_HA_HOST`) or move `tools/` to a private repo. Note: git
      *history* retains the hostname either way — it's Cloudflare-fronted and no
      token is committed, so exposure is a hostname only. Decide: scrub-and-keep
      (accept history) vs move out + fresh history.
- [ ] **Dashie-reference sweep**: README footers ("operated by the makers of
      Dashie") and the compatibility-matrix row are the two *allowed* mentions.
      Everything else is code comments pointing at internal Dashie docs
      (`const.py`, `addon_bridge.py`, `entity_context.py`, `conversation.py`,
      `engines.js` reference e.g. `20260702_BRIDGE_AUTH_HARDENING`,
      `20260717_HA_ENTITY_EXPOSURE_CONTRACT`). Harmless but confusing to
      outsiders — either keep (honest provenance) or reword to describe the
      pattern instead of naming the doc. Vendored `server/brain/` keeps its
      Dashie strings (generated code; canonical upstream).
- [ ] **Secret scan the full history** of both repos (`gitleaks detect` or
      `trufflehog git`) — tools read `~/.ha_token` at runtime and nothing is
      known-committed, but verify before it's permanent.
- [ ] **Fresh eyes on the icon** — John reviews/approves the chickadee mark
      (`brands/make_icons.py` regenerates all sizes if tweaked).
- [ ] Optional but recommended: add CI before flip so the public repo is green
      from day one — `hassfest` action + `hacs/action` (integration repo);
      add-on lint / build action (addons repo).

## 1. Namespace grabs (same day, before the announcement)

- [ ] **Register the domain** — available as of 07-25: getchickadee.com,
      chickadeehq.com, usechickadee.com, chickadee.sh, chickadee.casa.
      ⚠️ `repository.yaml` currently says `hello@getchickadee.org` — either
      register the `.org` too or update the maintainer email to the domain
      actually registered. Needed for: auth/receipt email sending (add to
      Resend), stable API CNAME, squat protection.
- [ ] Docker Hub / GHCR namespace if add-on images ever publish outside GHCR
      (GHCR under jwlerch78 works by default).
- [ ] PyPI: `chickadee` is taken (small OSINT tool) — grab `chickadee-voice`
      only if we ever ship a lib. Low priority.
- [ ] Defensive GitHub org (e.g. `chickadee-voice`) if desired — decide once;
      repos can transfer later with redirects.
- [ ] Optional: EUIPO search pass; intent-to-use filing when revenue nears.

## 2. Flip public (both repos together — they cross-link)

- [ ] `gh repo edit jwlerch78/chickadee --visibility public`
- [ ] `gh repo edit jwlerch78/chickadee-addons --visibility public`
- [ ] Add topics (HACS default-store submission requires them later):
      - chickadee: `home-assistant`, `hacs`, `integration`, `voice-assistant`,
        `assist-pipeline`, `conversation`, `stt`, `tts`, `llm`
      - chickadee-addons: `home-assistant`, `home-assistant-addons`,
        `voice-assistant`, `llm`
- [ ] Set social-preview images (repo Settings → Social preview; use the logo).
- [ ] Verify the v0.1.0 / v0.2.0 releases render publicly; verify HACS custom-repo
      install works from a clean HA box; verify the add-on repo installs via
      Settings → Add-ons → Repositories.
- [ ] Add my.home-assistant.io badge links to both READMEs (they only work
      against public repos): add-on repository badge + HACS repository badge.

## 3. Upstream submissions (launch day, after flip)

- [ ] **home-assistant/brands PR** — contents staged in [`brands/`](brands/);
      steps in [`brands/README.md`](brands/README.md).
- [ ] HACS **custom repo** is the launch path. Default-store submission comes
      later, once there's release history + the brands PR is merged.

## 4. Announce

- [ ] Launch post from u/jwlerch: architecture story + benchmark data
      (~8 s LAN pipeline, engine mix-and-match) + GitHub link. No Dashie framing
      beyond the README footer. Per the plan: don't announce before installable
      (it is, after §2), don't hide the Dashie connection.
- [ ] Release-per-post cadence afterward off the roadmap backlog
      (auto-create-pipeline, hosted engines, streaming).

## Deliberately NOT launch-day

- Hosted/cloud engine routing (needs the account port) — docs already say
  "planned", keep it that way.
- Hermes dual-listing in chickadee-addons.
- Stripe/public-business-name check (Phase 3, before any Chickadee user sees
  checkout).
- HA "Works with Home Assistant" application (Dashie-the-product lane).
