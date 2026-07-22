#!/usr/bin/env python3
"""
Helper script to create credentials.json from Google Cloud Console values.
Can be used with command-line arguments, environment variables, or interactive prompts.
"""

import json
import os
import argparse
import sys

def create_credentials(client_id=None, client_secret=None, project_id=None, overwrite=False, interactive=True):
    # Try to get from environment variables if not provided
    client_id = client_id or os.getenv('GOOGLE_CLIENT_ID')
    client_secret = client_secret or os.getenv('GOOGLE_CLIENT_SECRET')
    project_id = project_id or os.getenv('GOOGLE_PROJECT_ID', 'legacy-image-optimizer')
    
    # If still missing, prompt interactively
    if not client_id:
        if interactive:
            print("=" * 60)
            print("Google Drive API Credentials Setup")
            print("=" * 60)
            print("\nYou need to create a 'Desktop app' OAuth client in Google Cloud Console.")
            print("When you create it, copy the Client ID and Client secret immediately.")
            print("(The secret is only shown once!)\n")
        client_id = input("Enter your Desktop app Client ID: ").strip() if interactive else None
    
    if not client_id:
        print("Error: Client ID is required")
        return False
    
    if not client_secret:
        client_secret = input("Enter your Desktop app Client secret: ").strip() if interactive else None
    
    if not client_secret:
        print("Error: Client secret is required")
        return False
    
    # Only prompt for project_id if we're in interactive mode and using default
    if interactive and project_id == 'legacy-image-optimizer':
        project_id_input = input("Enter your Project ID (or press Enter to use 'legacy-image-optimizer'): ").strip()
        if project_id_input:
            project_id = project_id_input
        else:
            project_id = "legacy-image-optimizer"
    
    credentials = {
        "installed": {
            "client_id": client_id,
            "project_id": project_id,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": client_secret,
            "redirect_uris": [
                "urn:ietf:wg:oauth:2.0:oob",
                "http://localhost"
            ]
        }
    }
    
    output_file = "credentials.json"
    
    # Check if file already exists
    if os.path.exists(output_file) and not overwrite:
        response = input(f"\n{output_file} already exists. Overwrite? (y/N): ").strip().lower()
        if response != 'y':
            print("Cancelled.")
            return False
    
    # Write the file
    with open(output_file, 'w') as f:
        json.dump(credentials, f, indent=2)
    
    print(f"\n✓ Successfully created {output_file}")
    print("\nNext steps:")
    print("1. Run: python main.py --reauth")
    print("2. This will open a browser for Google authentication")
    print("3. After authentication, token.json will be created automatically")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create credentials.json for Google Drive API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode (prompts for values)
  python create_credentials.py
  
  # Command-line arguments
  python create_credentials.py --client-id "xxx" --client-secret "yyy" --project-id "my-project"
  
  # Environment variables
  export GOOGLE_CLIENT_ID="xxx"
  export GOOGLE_CLIENT_SECRET="yyy"
  export GOOGLE_PROJECT_ID="my-project"
  python create_credentials.py
        """
    )
    parser.add_argument('--client-id', help='Google OAuth Client ID')
    parser.add_argument('--client-secret', help='Google OAuth Client Secret')
    parser.add_argument('--project-id', help='Google Cloud Project ID (default: legacy-image-optimizer)')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing credentials.json without prompting')
    
    args = parser.parse_args()
    
    try:
        # Determine if we're in interactive mode (no args provided)
        interactive = not (args.client_id and args.client_secret)
        
        success = create_credentials(
            client_id=args.client_id,
            client_secret=args.client_secret,
            project_id=args.project_id,
            overwrite=args.overwrite,
            interactive=interactive
        )
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)

