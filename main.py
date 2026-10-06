"""
Main CLI entry point for Google Drive Image Optimizer.
"""

import argparse
import re
import sys
import os
import json

# Utility to extract folder ID from share link or accept direct ID
def extract_folder_id(folder_input):
    match = re.search(r"/folders/([\w-]+)", folder_input)
    if match:
        return match.group(1)
    # If input looks like a folder ID, return as is
    if re.match(r"^[\w-]{10,}$", folder_input):
        return folder_input
    raise ValueError("Invalid Google Drive folder link or ID.")

def load_cache(cache_path):
    if os.path.exists(cache_path):
        with open(cache_path, 'r') as f:
            return json.load(f)
    return {"downloaded": [], "processed": [], "failed": []}

def save_cache(cache, cache_path):
    with open(cache_path, 'w') as f:
        json.dump(cache, f, indent=2)

def main():
    parser = argparse.ArgumentParser(description="Google Drive Image Optimizer CLI")
    parser.add_argument('--drive-folder', required=False, help='Google Drive folder ID or share link')
    parser.add_argument('--upload-dir', help='Local directory of images to upload')
    parser.add_argument('--output-dir', default='optimized', help='Directory to save optimized images')
    parser.add_argument('--optimize', action='store_true', help='Optimize images (resize, compress, convert)')
    parser.add_argument('--resume', action='store_true', help='Resume from last cache')
    parser.add_argument('--upload-optimized', action='store_true', help='Upload optimized images to Drive')
    parser.add_argument('--cleanup', action='store_true', help='Prompt to delete originals after optimization')
    parser.add_argument('--ext', default='jpg,jpeg,png,bmp,tiff,heic,heif', help='Comma-separated list of extensions to process')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing optimized files')
    parser.add_argument('--skip-existing', action='store_true', help='Skip files that are already optimized')
    parser.add_argument('--fail-log', default='failures.log', help='Path to log failed conversions')
    parser.add_argument('--cache-file', default='cache.json', help='Custom path for cache file')
    parser.add_argument('--config', help='Path to config.json for persistent settings')
    parser.add_argument('--reauth', action='store_true', help='Force new Google account auth')
    parser.add_argument('--dry-run', action='store_true', help='Preview actions without making changes')
    parser.add_argument('--test-mode', action='store_true', help='Mock Drive calls and file operations')
    parser.add_argument('--keep-temp', action='store_true', help='Keep temp download directory after processing')
    parser.add_argument('--max-retries', type=int, default=3, help='Number of times to retry failed operations')
    parser.add_argument('--versioned', action='store_true', help='Save versioned filenames if conflicts')

    args = parser.parse_args()

    # Handle reauth flag (do this before any folder ID logic)
    if args.reauth:
        if os.path.exists('token.json'):
            os.remove('token.json')
            print('Removed token.json for re-authentication.')
        # Trigger auth flow and exit
        from drive_utils import get_drive_service
        get_drive_service()
        print('Re-authentication complete.')
        sys.exit(0)

    # Enforce --drive-folder is required for all other operations
    drive_folder = args.drive_folder
    if not drive_folder:
        drive_folder = input('Please enter a Google Drive folder share link or ID where your images are located: ').strip()
        if not drive_folder:
            print('Error: A Google Drive folder link or ID is required.')
            sys.exit(1)

    # Extract folder ID
    try:
        folder_id = extract_folder_id(drive_folder)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Fetch folder name for SEO-friendly filenames
    from drive_utils import get_folder_name
    folder_name = get_folder_name(folder_id) or "optimized"
    # Sanitize folder name for filenames
    import re as _re
    folder_name_clean = _re.sub(r'[^a-zA-Z0-9_-]+', '-', folder_name.strip().lower())

    # Use a unique output directory per Drive folder
    output_dir = f"optimized_{folder_name_clean}"
    temp_dir = 'temp_download'
    extensions = [e.strip().lower() for e in args.ext.split(',')] if args.ext else ['jpg', 'jpeg', 'png', 'bmp', 'tiff']
    print(f"Downloading images from Drive folder {folder_id} to {temp_dir}...")
    from drive_utils import download_images
    downloaded, failed, file_ids = download_images(
        folder_id,
        temp_dir,
        extensions=extensions,
        fail_log_path='failures.log',
        max_retries=3
    )
    print(f"Downloaded: {downloaded}")
    if failed:
        print(f"Failed to download: {failed}")

    # Optimize images
    from image_processor import process_image
    os.makedirs(output_dir, exist_ok=True)
    optimized = []
    skipped = []
    process_errors = []
    output_names = {}  # downloaded filename -> optimized .webp filename
    for fname in downloaded:
        input_path = os.path.join(temp_dir, fname)
        try:
            out_path, status = process_image(
                input_path,
                output_dir,
                overwrite=False,
                skip_existing=True,
                versioned=False,
                seo_prefix=folder_name_clean
            )
            output_names[fname] = os.path.basename(out_path)
            if status == 'skipped':
                skipped.append(fname)
            else:
                optimized.append(fname)
        except Exception as e:
            process_errors.append(fname)
            print(f"Error processing {fname}: {e}")
            with open('failures.log', 'a') as f:
                f.write(f"Failed to process {fname}: {e}\n")
    print(f"\nOptimization complete. {len(optimized)} images optimized, {len(skipped)} skipped (already optimized). Optimized images are in '{output_dir}'.\n")

    # Automatically upload optimized images to the same Drive folder
    print(f"Uploading optimized images from {output_dir} to Drive folder {folder_id}...")
    from drive_utils import upload_images, delete_images
    uploaded, failed_uploads, skipped_uploads = upload_images(output_dir, folder_id, extensions=['.webp'], fail_log_path='failures.log', max_retries=3)
    print(f"\nUpload complete. {len(uploaded)} uploaded, {len(failed_uploads)} failed, {len(skipped_uploads)} skipped (already in Drive).\n")

    # Trash an original only once its optimized version is safely in Drive
    in_drive = set(uploaded) | set(skipped_uploads)
    original_file_ids = []
    kept_originals = []
    for fname in downloaded:
        if output_names.get(fname) in in_drive:
            original_file_ids.append(file_ids[fname])
        else:
            kept_originals.append(fname)
    if kept_originals:
        print(f"Keeping {len(kept_originals)} originals because their optimized version is not in Drive: {kept_originals}")

    delete_errors = 0
    if original_file_ids:
        print("Automatically deleting original images from Google Drive...")
        delete_errors = delete_images(folder_id, original_file_ids)
    else:
        print("No original images to clean up.")

    print("\nSummary:")
    print(f"  Downloaded: {len(downloaded)}")
    print(f"  Failed downloads: {len(failed)}")
    print(f"  Optimized: {len(optimized)}")
    print(f"  Skipped (already optimized): {len(skipped)}")
    print(f"  Failed to optimize: {len(process_errors)}")
    print(f"  Uploaded: {len(uploaded)}")
    print(f"  Skipped upload (already in Drive): {len(skipped_uploads)}")
    print(f"  Failed uploads: {len(failed_uploads)}")
    print(f"  Originals kept: {len(kept_originals)}")
    print(f"  Failed to trash originals: {delete_errors}")
    had_errors = bool(failed or process_errors or failed_uploads or delete_errors)
    
    # Clean up local directories
    print("\nCleaning up local directories...")
    import shutil
    
    # Remove temp download directory
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
        print(f"Removed temp directory: {temp_dir}")
    
    # Remove optimized directory
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
        print(f"Removed optimized directory: {output_dir}")
    
    print("Cleanup complete.")
    if had_errors:
        print("\nFinished with errors — see the summary above.")
        sys.exit(1)
    print("\nThank you for using Google Drive Image Optimizer!")
    sys.exit(0)

if __name__ == "__main__":
    main() 