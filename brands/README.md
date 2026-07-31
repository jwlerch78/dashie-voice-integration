# home-assistant/brands PR staging

This directory stages the exact contents for a PR to
[home-assistant/brands](https://github.com/home-assistant/brands), which makes
HA render the Dashie icon in Devices & Services, the integration picker, and
HACS.

The images are **derived from the add-on's own art** — `dashie-ha/icon.png` and
`dashie-ha/logo.png` in [jwlerch78/dashie-ha](https://github.com/jwlerch78/dashie-ha)
— by [`make_icons.py`](make_icons.py). They are deliberately not separate
artwork: HA shows this icon beside an add-on the user just installed, so the two
must be the same picture. Re-run the script after any change to the add-on art:

```bash
python3 brands/make_icons.py ~/projects/dashie-ha-console
```

## PR contents

Copy `custom_integrations/dashie_voice/` into the brands repo at the same path:

```
custom_integrations/dashie_voice/icon.png       256×256
custom_integrations/dashie_voice/icon@2x.png    512×512
custom_integrations/dashie_voice/logo.png       512 wide, landscape
custom_integrations/dashie_voice/logo@2x.png    1024 wide, landscape
```

## PR steps (launch day)

1. Fork `home-assistant/brands`, branch `add-dashie-voice`.
2. Copy the directory above; run their linter if the repo currently has one
   (CI validates size/format on the PR anyway).
3. PR title: `Add dashie_voice (custom integration)`. Body: one line — custom
   integration at https://github.com/jwlerch78/dashie-ha-console, domain `dashie_voice`.
4. Check the current brands CONTRIBUTING.md for rule drift (image size rules
   have changed before) and adjust if CI complains.
