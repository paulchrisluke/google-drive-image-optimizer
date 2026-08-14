<div align="center">

# Google Drive Image Optimizer

**The image optimization step everyone skips — and why your pages are still slow.**

[![Python](https://img.shields.io/badge/python-3.8+-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-22c55e.svg)](LICENSE)
[![GitHub Actions](https://img.shields.io/badge/powered%20by-GitHub%20Actions-2088FF.svg?logo=github-actions&logoColor=white)](https://github.com/features/actions)
[![WebP](https://img.shields.io/badge/output-WebP-FF6B35.svg)](https://developers.google.com/speed/webp)

</div>

---

## The problem no one talks about

You installed an image optimizer plugin. Shopify compresses your uploads. Your CDN serves images from the edge. And yet your PageSpeed score is still stuck in the 50s.

Here's why.

**Every optimizer you're using is working on the wrong file.**

When a photographer sends you a 6MB JPEG from their iPhone, and you upload it to WordPress, Shopify, or Squarespace — the platform's optimizer does its best. But it's polishing a stone. Even after compression, you're serving a 1.5MB file where a 180KB WebP would do the same job.

This is the **"garbage in, garbage out" problem** of web image optimization, and it's the reason images account for [70–80% of poor LCP scores](https://web.dev/lcp/) across the web.

> **Your plugin optimizes the image you give it. It can't fix the fact that you gave it the wrong image.**

---

## The fix: optimize at the source

The solution isn't a better plugin. It's optimizing the image *before it ever touches your CMS*.

Here's the workflow that's driven **#1 search rankings and 2M+ organic impressions per day** on production sites:

```
📸 Photographer uploads photos to Google Drive
         ↓
🔄 This tool runs automatically (GitHub Actions, free)
         ↓
✅ Drive folder now contains: resized, compressed, WebP images
   with SEO-friendly filenames (e.g. sooke-marina-sunset.webp)
         ↓
🚀 You upload THOSE images to WordPress / Shopify / your CMS
         ↓
⚡ Platform optimizer does its thing — on an already-lean file
```

The compounding effect is dramatic:

| | Without this tool | With this tool |
|---|---|---|
| **Source file** | 6MB iPhone JPEG | 6MB iPhone JPEG |
| **After upload to CMS** | ~1.5MB (plugin compressed JPEG) | ~160KB (pre-optimized WebP) |
| **Total size reduction** | ~75% | **~97%** |
| **LCP element load time** | 4–8 seconds | 0.8–1.5 seconds |
| **PageSpeed score (typical)** | 45–65 | 88–98 |
| **Google's verdict** | ⚠️ Needs Improvement | ✅ Good |

> A 31% improvement in LCP has been shown to increase sales by 8% ([Vodafone case study](https://web.dev/vodafone/)). Roughly 40–50% of the web currently fails to meet Google's LCP threshold of 2.5 seconds — giving well-optimized sites a significant ranking advantage.

---

## What this tool does

Point it at a Google Drive folder. It handles everything automatically:

| Step | What happens |
|---|---|
| 📥 **Download** | Pulls every image from your Drive folder |
| ✂️ **Resize** | Scales to web-appropriate dimensions (1200×900 landscape / 900×1200 portrait) |
| 🔄 **Convert** | Converts to WebP — 25–34% smaller than JPEG at equivalent quality |
| 🏷️ **Rename** | Adds SEO-friendly, folder-based prefixes (`sooke-marina-sunset.webp`) |
| 📤 **Upload** | Puts optimized images back into the same Drive folder |
| 🗑️ **Clean up** | Moves originals to Trash (recoverable for 30 days) |

Supports: **JPG · PNG · HEIC/HEIF · BMP · TIFF**

Runs free on GitHub Actions — no server, no subscription, no monthly bill.

---

## Quick Start

### 1. Use this template

Click **"Use this template"** at the top of this page to fork your own copy.

### 2. One-time local setup (~5 minutes)

```bash
git clone https://github.com/YOUR_USERNAME/google-drive-image-optimizer
cd google-drive-image-optimizer
pip install -r requirements.txt
python setup_secrets.py
```

The setup wizard will:
- Walk you through creating a free Google Cloud OAuth credential (with direct links and instructions)
- Open a browser to authorize your Google account
- Print your **3 GitHub Secrets** — ready to copy and paste

### 3. Add your 3 GitHub Secrets

Go to your repo → **Settings → Secrets and variables → Actions → New repository secret**

| Secret | Value |
|---|---|
| `GDRIVE_CLIENT_ID` | From setup wizard output |
| `GDRIVE_CLIENT_SECRET` | From setup wizard output |
| `GDRIVE_REFRESH_TOKEN` | From setup wizard output |

### 4. Run it

**Actions → Optimize Drive Folder → Run workflow**

Paste your Google Drive folder link. Click Run. That's it.

---

## Before & After

Images are renamed with a clean, SEO-friendly prefix based on your folder name:

```
Before:  IMG_4821.JPG         →   6.2 MB   JPEG
After:   sooke-marina-IMG_4821.webp   →   184 KB  WebP
```

Alt text is automatically extracted from filenames and saved to `alt_text_map.json` — ready to reference in your CMS or static site.

---

## Advanced usage

```bash
# Run locally with full control
python main.py --drive-folder "YOUR_FOLDER_LINK_OR_ID"

# Preview actions without making any changes
python main.py --drive-folder "YOUR_FOLDER_ID" --dry-run

# Process specific file types only
python main.py --drive-folder "YOUR_FOLDER_ID" --ext "jpg,heic"

# Overwrite existing optimized files
python main.py --drive-folder "YOUR_FOLDER_ID" --overwrite

# Re-authenticate with a different Google account
python main.py --reauth
```

---

## Project structure

```
google-drive-image-optimizer/
├── main.py                 # CLI entry point
├── drive_utils.py          # Google Drive API (download, upload, delete)
├── image_processor.py      # Resize, compress, WebP conversion
├── setup_secrets.py        # One-time setup wizard → prints GitHub Secrets
├── create_credentials.py   # Helper to build credentials.json
├── requirements.txt        # Python dependencies
└── .github/workflows/
    └── optimize.yml        # GitHub Actions workflow definition
```

---

## FAQ

**Does this delete my original photos permanently?**
No. Originals are moved to Google Drive Trash, where they stay for 30 days before auto-deletion. Restore them any time from Trash.

**Will it re-process images that are already optimized?**
No. It skips files that already exist in your Drive folder — safe to run repeatedly on the same folder.

**What if an image fails to process?**
Errors are caught per-file, logged to `failures.log`, and the rest of the batch continues uninterrupted.

**Does it work with shared Drive folders?**
Yes — as long as the authorized Google account has edit access to the folder.

**Is this actually free?**
Yes. GitHub Actions gives 2,000 free minutes/month on public repos, 500 on private. The Google Drive API is free within standard quota limits.

**I already have an image optimizer plugin. Do I still need this?**
Yes — and now your plugin will finally have something worth optimizing. This doesn't replace your CMS optimizer. It makes it dramatically more effective by giving it a lean, correctly-sized WebP instead of a raw 6MB JPEG.

---

## Requirements

- A free GitHub account
- A Google account with Drive
- Python 3.8+ *(for one-time local setup only — the Action runs in the cloud)*

---

## License

MIT — free for personal and commercial use.

---

<div align="center">
<sub>Built by people who got tired of uploading 6MB JPEGs and wondering why their sites were slow.</sub>
</div>