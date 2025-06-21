

from abc import ABC, abstractmethod
from typing import List
import dropbox
import cloudinary
import cloudinary.uploader
# local imports
from config import (
    CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET, DROPBOX_API_KEY
)

class CloudBackend(ABC):
    @abstractmethod
    def upload(self, file_path: str, key: str) -> str:
        """ upload local file to remote; returns accessible URL """
        pass


class CloudinaryBackend(CloudBackend):
    def __init__(self):
        #& added this check to the config but it may be better to keep it here - depends on if I ever want to use this without any cloud uploads
        # if not (CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET):
        #     raise RuntimeError('Missing Cloudinary credentials')
        cloudinary.config(
            cloud_name=CLOUDINARY_CLOUD_NAME,
            api_key=CLOUDINARY_API_KEY,
            api_secret=CLOUDINARY_API_SECRET,
            secure=True
        )

    def upload(self, file_path: str, key: str) -> str:
        result: dict = cloudinary.uploader.upload(
            file_path,
            resource_type='raw',
            public_id=key
        )
        return result.get('secure_url')


class DropboxBackend(CloudBackend):
    def __init__(self):
        if not DROPBOX_API_KEY:
            raise RuntimeError('Missing Dropbox API key')
        self.dbx = dropbox.Dropbox(DROPBOX_API_KEY)
        raise FutureWarning('Dropbox API is deprecated and may not work in the future. Consider using Cloudinary or another service.')

    def upload(self, file_path: str, key: str) -> str:
        dbx_path = f"/{key}" # Dropbox path must start with '/'
        with open(file_path, 'rb') as f:
            self.dbx.files_upload(f.read(), dbx_path) # mode=dropbox.files.WriteMode.overwrite)
        # return a shareable link
        self.dbx.sharing_create_shared_link_with_settings(dbx_path)
        links: List[str] = self.dbx.sharing_get_shared_links(dbx_path)
        if not links:
            raise RuntimeError('Failed to create shared link for Dropbox file')
        return str(links[-1])