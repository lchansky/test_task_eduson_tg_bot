import re

import requests

from exceptions.validation import URLValidationError


class PicsumAPI:
    def request_photos(self, url: str) -> list[dict]:
        self.validate_url(url)
        try:
            response = requests.get(url)
            result = response.json()
        except:
            raise ConnectionError
        return result

    def validate_url(self, url: str):
        if not isinstance(url, str):
            raise URLValidationError
        if not re.match(r'^https://picsum\.photos/v2/list', url):
            raise URLValidationError

    def request_photo_info(self, photo_id: int) -> dict:
        try:
            response = requests.get(f'https://picsum.photos/id/{photo_id}/info')
            result = response.json()
        except:
            raise ConnectionError
        return result

    def request_photo_bytes(self, url: str) -> bytes:
        try:
            response = requests.get(url)
            return response.content
        except:
            raise ConnectionError
