import base64
import os
import uuid

import requests


def save_file(file_input, site_name="erpnext.localhost", folder_type="logos"):
    """
    Save a file to the local ERPNext folder.
    file_input can be:
      - base64 string starting with 'data:image/...'
      - full URL starting with http/https
      - actual file-like object (from Flask/Django request.files)
    Returns the relative path to the saved file.
    """
    try:
        base_path = os.path.join(
            os.getcwd(),
            site_name,
            "public",
            "files",
            "uploads",
            folder_type,
        )
        os.makedirs(base_path, exist_ok=True)

        # Case 1: Base64 image
        if isinstance(file_input, str) and file_input.startswith("data:image/"):
            header, encoded = file_input.split(",", 1)
            ext = header.split(";")[0].split("/")[1]
            filename = f"{uuid.uuid4().hex}.{ext}"
            save_path = os.path.join(base_path, filename)

            with open(save_path, "wb") as f:
                f.write(base64.b64decode(encoded))

            return f"/files/uploads/{folder_type}/{filename}"

        # Case 2: URL
        elif isinstance(file_input, str) and (file_input.startswith("http://") or file_input.startswith("https://")):
            headers = {
                "User-Agent": "Mozilla/5.0",
                "Referer": "https://www.google.com/",
            }

            response = requests.get(file_input, headers=headers, stream=True)
            response.raise_for_status()

            ext = file_input.split("?")[0].split(".")[-1]
            if len(ext) > 4:
                ext = "png"

            filename = f"{uuid.uuid4().hex}.{ext}"
            save_path = os.path.join(base_path, filename)

            with open(save_path, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)

            return f"/files/uploads/{folder_type}/{filename}"

        # Case 3: Actual file object (from request.files)
        elif hasattr(file_input, "read"):
            filename = f"{uuid.uuid4().hex}_{getattr(file_input, 'filename', 'file')}"
            save_path = os.path.join(base_path, filename)

            with open(save_path, "wb") as f:
                f.write(file_input.read())

            return f"/files/uploads/{folder_type}/{filename}"

        else:
            raise ValueError("Unsupported file input type")

    except Exception as e:
        print(f"Error saving file: {e}")
        return None