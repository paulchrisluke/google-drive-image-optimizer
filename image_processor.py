"""
Image resizing, compression, and conversion utilities.
"""

import os
from PIL import Image, ImageOps
import io
import json
import pillow_heif

pillow_heif.register_heif_opener()

# Portrait: 1200x900, Landscape: 900x1200
PORTRAIT_SIZE = (900, 1200)
LANDSCAPE_SIZE = (1200, 900)
DEFAULT_MAX_SIZE_KB = 300


def resize_image(input_path, output_path, target_size):
    """Resize image to target_size and save to output_path."""
    with Image.open(input_path) as img:
        img = ImageOps.exif_transpose(img)
        img = img.convert('RGB')
        img = img.resize(target_size, Image.LANCZOS)
        img.save(output_path)


def compress_and_convert_to_webp(input_path, output_path, max_size_kb=DEFAULT_MAX_SIZE_KB, quality=80):
    """Compress and convert image to .webp under max_size_kb."""
    with Image.open(input_path) as img:
        img = ImageOps.exif_transpose(img)
        img = img.convert('RGB')
        for q in range(quality, 10, -5):
            buffer = io.BytesIO()
            img.save(buffer, format='WEBP', quality=q)
            size_kb = buffer.tell() / 1024
            if size_kb <= max_size_kb:
                with open(output_path, 'wb') as f:
                    f.write(buffer.getvalue())
                return True
        # If not small enough, save at lowest quality
        img.save(output_path, format='WEBP', quality=10)
    return False


def extract_alt_text(filename):
    """Extract alt text from filename (without extension)."""
    name = os.path.splitext(os.path.basename(filename))[0]
    return name.replace('-', ' ').replace('_', ' ').replace('.', ' ').strip()


def update_alt_text_map(webp_filename, alt_text, map_path='alt_text_map.json'):
    """Update alt_text_map.json with new alt text."""
    if os.path.exists(map_path):
        with open(map_path, 'r') as f:
            alt_map = json.load(f)
    else:
        alt_map = {}
    alt_map[webp_filename] = alt_text
    with open(map_path, 'w') as f:
        json.dump(alt_map, f, indent=2)


def process_image(input_path, output_dir, overwrite=False, skip_existing=False, versioned=False, max_size_kb=DEFAULT_MAX_SIZE_KB, alt_text_map_path='alt_text_map.json', seo_prefix=None):
    """Resize, compress, and convert image to .webp in output_dir. Update alt text map. Handle conflict logic. Optionally prefix output filename with seo_prefix."""
    base = os.path.basename(input_path)
    name, _ = os.path.splitext(base)
    if seo_prefix:
        out_name = f"{seo_prefix}-{name}.webp"
    else:
        out_name = f"{name}.webp"
    output_path = os.path.join(output_dir, out_name)
    if os.path.exists(output_path):
        if skip_existing:
            print(f"Skipping existing: {output_path}")
            return output_path, 'skipped'
        if not overwrite and versioned:
            # Find next available versioned filename
            v = 2
            while True:
                if seo_prefix:
                    versioned_name = f"{seo_prefix}-{name}_v{v}.webp"
                else:
                    versioned_name = f"{name}_v{v}.webp"
                versioned_path = os.path.join(output_dir, versioned_name)
                if not os.path.exists(versioned_path):
                    output_path = versioned_path
                    break
                v += 1
        elif not overwrite:
            print(f"Skipping (exists, no overwrite): {output_path}")
            return output_path, 'skipped'
    with Image.open(input_path) as img:
        img = ImageOps.exif_transpose(img)
        w, h = img.size
        if h > w:
            target_size = PORTRAIT_SIZE
        else:
            target_size = LANDSCAPE_SIZE
        resized = img.resize(target_size, Image.LANCZOS)
        for q in range(80, 10, -5):
            buffer = io.BytesIO()
            resized.save(buffer, format='WEBP', quality=q)
            size_kb = buffer.tell() / 1024
            if size_kb <= max_size_kb:
                with open(output_path, 'wb') as f:
                    f.write(buffer.getvalue())
                print(f"Optimized: {output_path} ({int(size_kb)} KB)")
                alt_text = extract_alt_text(base)
                update_alt_text_map(os.path.basename(output_path), alt_text, alt_text_map_path)
                return output_path, 'ok'
        resized.save(output_path, format='WEBP', quality=10)
        print(f"Saved at lowest quality: {output_path}")
        alt_text = extract_alt_text(base)
        update_alt_text_map(os.path.basename(output_path), alt_text, alt_text_map_path)
    return output_path, 'low_quality' 