"""
Google Drive upload, download, and delete utilities.
"""

import os
import io
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

# Supported image extensions
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.heic'}

SCOPES = ["https://www.googleapis.com/auth/drive"]

def get_drive_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            # Use port 8080 to match common OAuth redirect URI patterns
            creds = flow.run_local_server(port=8080)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return build("drive", "v3", credentials=creds)

def list_files_in_folder(drive_folder_id):
    """Return a set of filenames in the given Google Drive folder."""
    service = get_drive_service()
    page_token = None
    filenames = set()
    while True:
        response = service.files().list(
            q=f"'{drive_folder_id}' in parents and trashed = false",
            spaces='drive',
            fields='nextPageToken, files(name)',
            pageToken=page_token
        ).execute()
        for file in response.get('files', []):
            filenames.add(file['name'])
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
    return filenames

def upload_images(local_folder, drive_folder_id, extensions=None, fail_log_path=None, max_retries=3):
    """Upload images from local_folder to Google Drive folder, skipping files that already exist."""
    if extensions is None:
        extensions = IMAGE_EXTENSIONS
    else:
        extensions = set(e.lower() if e.startswith('.') else f'.{e.lower()}' for e in extensions)
    service = get_drive_service()
    uploaded = []
    failed = []
    existing_files = list_files_in_folder(drive_folder_id)
    for fname in os.listdir(local_folder):
        ext = os.path.splitext(fname)[1].lower()
        if ext.lower() not in {e.lower() for e in extensions}:
            continue
        if fname in existing_files:
            print(f"[SKIP] Already exists in Drive: {fname}")
            continue
        file_path = os.path.join(local_folder, fname)
        for attempt in range(max_retries):
            try:
                file_metadata = {
                    'name': fname,
                    'parents': [drive_folder_id]
                }
                media = MediaIoBaseUpload(open(file_path, 'rb'), mimetype='application/octet-stream')
                service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()
                uploaded.append(fname)
                print(f"Uploaded: {fname}")
                break
            except Exception as e:
                print(f"Failed to upload {fname} (attempt {attempt+1}): {e}")
                if attempt == max_retries - 1:
                    failed.append(fname)
    if fail_log_path and failed:
        with open(fail_log_path, 'a') as flog:
            for fname in failed:
                flog.write(fname + '\n')
    return uploaded, failed

def download_images(drive_folder_id, local_temp_dir, extensions=None, fail_log_path=None, max_retries=3):
    """Download images from Google Drive folder to local_temp_dir. Save with unique filenames if needed."""
    if extensions is None:
        extensions = IMAGE_EXTENSIONS
    else:
        extensions = set(e.lower() if e.startswith('.') else f'.{e.lower()}' for e in extensions)
    os.makedirs(local_temp_dir, exist_ok=True)
    service = get_drive_service()
    page_token = None
    downloaded = []
    failed = []
    print(f"[DEBUG] Extensions being used for filtering: {extensions}")
    while True:
        try:
            response = service.files().list(
                q=f"'{drive_folder_id}' in parents and trashed = false",
                spaces='drive',
                fields='nextPageToken, files(id, name, mimeType)',
                pageToken=page_token
            ).execute()
            print("[DEBUG] Files found in folder:")
            for file in response.get('files', []):
                print(f"  - {file['name']} (mimeType: {file['mimeType']})")
            for file in response.get('files', []):
                name = file['name']
                ext = os.path.splitext(name)[1]
                mime_type = file.get('mimeType', '')
                print(f"[DEBUG] Checking file: {name}, extracted ext: '{ext}' (lower: '{ext.lower()}'), mimeType: {mime_type}")
                
                # Check if it's an image by extension OR MIME type
                is_image_by_ext = ext.lower() in {e.lower() for e in extensions}
                is_image_by_mime = mime_type.startswith('image/') and mime_type in [
                    'image/jpeg', 'image/jpg', 'image/png', 'image/bmp', 'image/tiff', 'image/heic', 'image/heif'
                ]
                
                if not (is_image_by_ext or is_image_by_mime):
                    print(f"[DEBUG] Skipping {name}: not an image by extension or MIME type")
                    continue
                file_id = file['id']
                # Save with unique filename: name_fileid.ext
                name_no_ext, ext = os.path.splitext(name)
                
                # If no extension but it's an image by MIME type, add appropriate extension
                if not ext and mime_type.startswith('image/'):
                    if mime_type in ['image/jpeg', 'image/jpg']:
                        ext = '.jpg'
                    elif mime_type == 'image/png':
                        ext = '.png'
                    elif mime_type == 'image/bmp':
                        ext = '.bmp'
                    elif mime_type == 'image/tiff':
                        ext = '.tiff'
                    elif mime_type == 'image/heic':
                        ext = '.heic'
                    elif mime_type == 'image/heif':
                        ext = '.heif'
                    else:
                        ext = '.jpg'  # Default to jpg for other image types
                    print(f"[DEBUG] No extension found, adding {ext} based on MIME type {mime_type}")
                
                unique_name = f"{name_no_ext}_{file_id}{ext}"
                local_path = os.path.join(local_temp_dir, unique_name)
                print(f"[DEBUG] Attempting to download: {name} (id: {file_id}) -> {local_path}")
                for attempt in range(max_retries):
                    try:
                        request = service.files().get_media(fileId=file_id)
                        with io.FileIO(local_path, 'wb') as fh:
                            downloader = MediaIoBaseDownload(fh, request)
                            done = False
                            while not done:
                                status, done = downloader.next_chunk()
                        downloaded.append(unique_name)
                        print(f"Downloaded: {unique_name}")
                        break
                    except Exception as e:
                        print(f"Failed to download {name} (attempt {attempt+1}): {e}")
                        if attempt == max_retries - 1:
                            failed.append(unique_name)
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break
        except HttpError as error:
            print(f"An error occurred: {error}")
            break
    if fail_log_path and failed:
        with open(fail_log_path, 'a') as flog:
            for fname in failed:
                flog.write(fname + '\n')
    return downloaded, failed

def delete_images(drive_folder_id, image_ids):
    """Delete images from Google Drive folder by image_ids."""
    service = get_drive_service()
    deleted_count = 0
    not_found_count = 0
    error_count = 0
    
    print(f"Attempting to delete {len(image_ids)} files...")
    
    for file_id in image_ids:
        try:
            service.files().delete(fileId=file_id).execute()
            print(f"Deleted file ID: {file_id}")
            deleted_count += 1
        except HttpError as e:
            if e.resp.status == 404:
                print(f"File not found (already deleted?): {file_id}")
                not_found_count += 1
            else:
                print(f"Failed to delete file ID {file_id}: {e}")
                error_count += 1
        except Exception as e:
            print(f"Failed to delete file ID {file_id}: {e}")
            error_count += 1
    
    # Print summary
    print(f"\nDeletion summary:")
    print(f"  Successfully deleted: {deleted_count}")
    print(f"  Not found (already deleted): {not_found_count}")
    print(f"  Errors: {error_count}")

def get_folder_name(folder_id):
    """Fetch the name of a Google Drive folder by its ID."""
    service = get_drive_service()
    try:
        folder = service.files().get(fileId=folder_id, fields='name').execute()
        return folder['name']
    except Exception as e:
        print(f"Failed to get folder name for ID {folder_id}: {e}")
        return None 