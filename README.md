<div align="center">

# 🖼️ Google Drive Image Optimizer

**Automatically convert your Google Drive photos to WebP — faster pages, better SEO, no server needed.**

[![Python](https://img.shields.io/badge/python-3.8+-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-22c55e.svg)](LICENSE)
[![GitHub Actions](https://img.shields.io/badge/powered%20by-GitHub%20Actions-2088FF.svg?logo=github-actions&logoColor=white)](https://github.com/features/actions)
[![WebP](https://img.shields.io/badge/output-WebP-FF6B35.svg)](https://developers.google.com/speed/webp)

</div>

---

Large JPEGs kill your [PageSpeed score](https://pagespeed.web.dev). WebP images are **30–80% smaller** at the same visual quality — meaning faster load times, higher search rankings, and happier visitors.

This tool automates the whole process. Point it at a Google Drive folder, and it will download every image, resize it, convert it to WebP with SEO-friendly filenames, upload the result back to Drive, and clean up the originals — all for free, using GitHub Actions.

**Built for:** bloggers, photographers, small business owners, and anyone who stores photos in Google Drive and wants them web-ready without a manual workflow.

---

## ✨ What It Does

| Step | Action |
|---|---|
| 📥 Download | Pulls every image from your Google Drive folder |
| ✂️ Resize | Scales to SEO-optimal dimensions (1200×900 landscape / 900×1200 portrait) |
| 🔄 Convert | Converts to WebP and compresses to under 300 KB |
| 🏷️ Rename | Adds SEO-friendly, folder-based prefixes to every filename |
| 📤 Upload | Puts optimized images back into the same Drive folder |
| 🗑️ Clean up | Moves originals to Trash (recoverable) and removes temp files |

Supports: **JPG, PNG, BMP, TIFF, HEIC/HEIF**

---

## 🚀 Quick Start

### 1. Use this template

Click **"Use this template"** at the top of this page to create your own copy of the repo.

### 2. One-time local setup (~5 min)

```bash
git clone https://github.com/YOUR_USERNAME/google-drive-image-optimizer
cd google-drive-image-optimizer
pip install -r requirements.txt
python setup_secrets.py
```

The setup script will:
- Walk you through creating a free Google Cloud OAuth credential (with direct links)
- Open a browser to authorize your Google account
- Print your **3 GitHub Secrets** ready to copy-paste

### 3. Add your 3 GitHub Secrets

In your repo, go to **Settings → Secrets and variables → Actions → New repository secret** and add:

| Secret Name | Where to get it |
|---|---|
| `GDRIVE_CLIENT_ID` | Printed by `setup_secrets.py` |
| `GDRIVE_CLIENT_SECRET` | Printed by `setup_secrets.py` |
| `GDRIVE_REFRESH_TOKEN` | Printed by `setup_secrets.py` |

### 4. Run the optimizer

Go to **Actions → Optimize Drive Folder → Run workflow**

Paste your Google Drive folder link (e.g. `https://drive.google.com/drive/folders/abc123`) and click **Run workflow**. Done.

---

## 📁 Output

Images are renamed with a SEO-friendly prefix based on your Drive folder name:

```
Before:  IMG_4821.JPG  (4.2 MB)
After:   sooke-marina-IMG_4821.webp  (187 KB)
```

Alt text is automatically extracted from filenames and saved to `alt_text_map.json` in your repo, so you can reference it in your CMS or website.

---

## 🔧 Advanced Usage

Run locally with full control over the process:

```bash
# Basic — download, optimize, upload, clean up
python main.py --drive-folder "YOUR_FOLDER_LINK_OR_ID"

# Preview what would happen without making changes
python main.py --drive-folder "YOUR_FOLDER_ID" --dry-run

# Only process specific file types
python main.py --drive-folder "YOUR_FOLDER_ID" --ext "jpg,png,heic"

# Overwrite existing optimized files
python main.py --drive-folder "YOUR_FOLDER_ID" --overwrite

# Re-authenticate with a different Google account
python main.py --reauth
```

---

## 🏗️ Project Structure

```
google-drive-image-optimizer/
├── main.py               # CLI entry point
├── drive_utils.py        # Google Drive API (download, upload, delete)
├── image_processor.py    # Resize, compress, WebP conversion
├── setup_secrets.py      # One-time setup wizard → prints GitHub Secrets
├── create_credentials.py # Helper to build credentials.json
├── requirements.txt      # Python dependencies
└── .github/
    └── workflows/
        └── optimize.yml  # GitHub Actions workflow
```

---

## ❓ FAQ

**Does it delete my original photos permanently?**
No. Originals are moved to Google Drive Trash, where they stay for 30 days before auto-deletion. You can restore them any time.

**Will it re-process images that are already optimized?**
No. It skips files that already exist in Drive, so re-running on the same folder is safe.

**Does it work with shared Drive folders?**
Yes, as long as the authorized Google account has edit access to the folder.

**What if an image fails to process?**
Errors are caught per-file, logged to `failures.log`, and the rest of the batch continues.

**Is this free?**
Yes. GitHub Actions gives you 2,000 free minutes/month on public repos and 500 on private. The Google Drive API is free within standard quota limits.

---

## 📋 Requirements

- A free GitHub account
- A Google account with Drive
- Python 3.8+ (for one-time local setup only — the Action runs in the cloud)

---

## 📄 License

MIT — free for personal and commercial use. See [LICENSE](LICENSE).

---

<div align="center">

Made with ☕ and too many large JPEGs.

</div>