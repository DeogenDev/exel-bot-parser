"""Google account."""

from src.shared import conf
from google.oauth2.service_account import Credentials
from google.oauth2 import service_account


class GoogleAccount:
    """Google account."""

    def __init__(self, credentials: Credentials, token: str):
        self.credentials = credentials
        self.token = token
