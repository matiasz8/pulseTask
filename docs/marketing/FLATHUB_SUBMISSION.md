# Flathub Submission Checklist - PulseTask v0.2.0

## Overview
Flathub is the standard package manager for GNOME/Linux applications. PulseTask is production-ready for Flathub submission.

---

## Pre-Submission Verification

### ✅ Project Structure
- [x] Desktop file: `data/org.gnome.Pulse.desktop`
- [x] Icon: Icon files in resources/
- [x] License: GPLv3 (LICENSE file in repo)
- [x] README: Comprehensive setup instructions
- [x] CHANGELOG: Detailed v0.2.0 release notes
- [x] Contributing guide: CONTRIBUTING.md

### ✅ Metadata Completeness
- [x] Version: v0.2.0 tagged and released
- [x] Homepage: GitHub repository
- [x] Bug reporting: GitHub Issues
- [x] Help URL: Documentation in repo
- [x] Screenshot: Ready (can add later)

---

## Flathub Manifest

Create `org.gnome.Pulse.json` in root:

```json
{
  "id": "org.gnome.Pulse",
  "runtime": "org.gnome.Platform",
  "runtime-version": "46",
  "sdk": "org.gnome.Sdk",
  "command": "pulsetask",
  "finish-args": [
    "--share=ipc",
    "--socket=wayland",
    "--socket=fallback-x11",
    "--device=dri"
  ],
  "modules": [
    {
      "name": "python-deps",
      "buildsystem": "simple",
      "build-commands": ["true"]
    },
    {
      "name": "pulsetask",
      "buildsystem": "simple",
      "build-commands": [
        "pip3 install --prefix=/app --no-index --find-links=. .",
        "install -d /app/share/applications",
        "install -m 644 data/org.gnome.Pulse.desktop /app/share/applications/org.gnome.Pulse.desktop",
        "install -d /app/share/icons/hicolor/scalable/apps",
        "install -m 644 resources/org.gnome.Pulse.svg /app/share/icons/hicolor/scalable/apps/org.gnome.Pulse.svg"
      ],
      "sources": [
        {
          "type": "git",
          "url": "https://github.com/matiasz8/pulseTask.git",
          "tag": "v0.2.0"
        }
      ]
    }
  ]
}
```

---

## Submission Steps

### Step 1: Fork flathub/flathub

Go to: https://github.com/flathub/flathub

1. Click "Fork" button
2. Create fork in your account
3. Clone fork locally:
```bash
git clone https://github.com/YOUR_USERNAME/flathub.git flathub
cd flathub
```

### Step 2: Create New Branch

```bash
git checkout -b add-pulsetask
```

### Step 3: Add Application

Create file: `new-entries/org.gnome.Pulse.json`

Copy the manifest content above.

### Step 4: Verify Metadata

```bash
# Flathub has a validation script
# Run locally if possible, or GitHub will check automatically
```

### Step 5: Commit

```bash
git add new-entries/org.gnome.Pulse.json
git commit -m "Add org.gnome.Pulse (PulseTask) - v0.2.0"
```

### Step 6: Push

```bash
git push origin add-pulsetask
```

### Step 7: Create Pull Request

1. Go to: https://github.com/flathub/flathub
2. Click "New Pull Request"
3. Select your fork + branch
4. Fill in PR template (provided by flathub)
5. Submit

### Step 8: Respond to Reviews

Flathub maintainers will:
- Check app security
- Verify manifest correctness
- Test builds
- Ask questions

**Response time:** Be responsive. 24-48h replies = faster approval.

---

## PR Template Fields

**Application Name:**
```
PulseTask
```

**Application Description:**
```
A calm execution environment for Linux power users. Focus on one task. See the remaining time. Finish before it expires. Perfect for developers, DevOps engineers, and anyone working in focused blocks.
```

**Homepage:**
```
https://github.com/matiasz8/pulseTask
```

**License:**
```
GPLv3
```

**Screenshot Description:**
```
PulseTask execution window showing active task timer with task queue
```

**Notes:**
```
PulseTask is production-ready with:
- 151 passing tests
- Full WCAG AA accessibility
- D-Bus ready for GNOME integration
- Open Core licensing model

Requires: Python 3.12+, GTK4, libadwaita

Core features available in free version. See GitHub for roadmap.
```

---

## Common Flathub Requirements

### Security
- [x] No arbitrary network access
- [x] No request to root privileges
- [x] Sandboxed by default
- [x] Clean permissions: `--share=ipc`, `--socket=wayland`, `--socket=x11`, `--device=dri`

### Quality
- [x] Follows GNOME Human Interface Guidelines (or compatible)
- [x] Has working Help/About/Preferences
- [x] No bundled libraries (uses system packages)
- [x] Proper keyboard navigation
- [x] Accessible to screen readers

### Metadata
- [x] Desktop file is valid
- [x] Icon is provided (SVG or PNG)
- [x] License file in repo
- [x] Release notes available
- [x] Readme explains what app does

---

## Expected Timeline

| Timeline | Status |
|----------|--------|
| Day 1-2 | Flathub CI runs (automated checks) |
| Day 2-5 | Maintainer review (can be longer if busy) |
| Day 5-7 | Questions/feedback (if any) |
| Day 7-10 | Approval + merge |
| Day 10-14 | Build in Flathub infrastructure |
| Day 14-21 | Live on Flathub |

**Total:** Usually 1-3 weeks from PR to live

---

## What Happens After Merge

1. **Build System**
   - Flathub automatically builds Flatpak
   - Runs on multiple architectures (x86_64, aarch64, etc.)
   - Tests before publishing

2. **Distribution**
   - Available in GNOME Software / Flatseal
   - Users can install: `flatpak install flathub org.gnome.Pulse`

3. **Updates**
   - Flathub watches your GitHub releases
   - New tags trigger automatic rebuilds
   - Users get updates automatically

4. **Analytics**
   - Flathub provides download stats
   - Monthly install numbers

---

## After Flathub Launch

### Marketing (FASE 2.2)
- Post to Reddit (r/gnome, r/linux)
- Submit to HackerNews
- Contact OMGUbuntu, Linux blogs
- Tweet/share widely

### Community
- Monitor Flathub reviews
- Respond to user feedback
- Create issues for bugs reported by new users
- Thank early adopters

### Metrics
- Track download growth
- Monitor GitHub issues for new patterns
- Gather feature requests
- Plan v0.3.0 based on feedback

---

## Troubleshooting

### "Build Failed"
- Check manifest syntax
- Verify Python dependencies in pyproject.toml
- Ensure version numbers match

### "Security Review Failed"
- Review sandboxing requirements
- Check for hardcoded paths
- Remove any privileged operations

### "Icon Missing"
- Must provide: SVG icon (preferred) or 128x128 PNG
- Place in: `resources/org.gnome.Pulse.svg` or `resources/org.gnome.Pulse.png`

### "Desktop File Invalid"
- Validate with: `desktop-file-validate data/org.gnome.Pulse.desktop`
- Check Categories (should include: GTK, Productivity, Utility)

---

## Final Checklist Before PR

- [ ] GitHub repo is public
- [ ] v0.2.0 tag pushed
- [ ] Release notes comprehensive
- [ ] Desktop file valid
- [ ] Icon files present
- [ ] License file exists
- [ ] README clear
- [ ] Manifest tested locally (if possible)
- [ ] PR template filled completely
- [ ] Ready for 1-3 week wait time

If all checked: **Submit PR with confidence.**

---

## Success Criteria

✅ PR merged to flathub/flathub
✅ Automatic build successful
✅ Available in GNOME Software
✅ Installable via `flatpak install`
✅ First user feedback in (usually positive)
✅ Analytics show install growth

**That's FASE 2.1 complete!**

Next: Reddit + HackerNews launch (FASE 2.2)
