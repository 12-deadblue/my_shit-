"""
Google OAuth Service
====================
Handles Google OAuth 2.0 token verification and user creation/lookup.
"""

import requests
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests


GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


def verify_google_token(token, client_id):
    """
    Verify a Google OAuth ID token.

    Args:
        token: The ID token from the client.
        client_id: Our Google OAuth client ID.

    Returns:
        dict with user info (sub, email, name, picture) or None.
    """
    try:
        id_info = id_token.verify_oauth2_token(
            token, google_requests.Request(), client_id
        )

        # Verify the token was issued for our app
        if id_info.get("aud") != client_id:
            return None

        return {
            "google_id": id_info["sub"],
            "email": id_info.get("email", ""),
            "name": id_info.get("name", ""),
            "avatar_url": id_info.get("picture", ""),
        }
    except ValueError:
        return None


def get_user_info_from_access_token(access_token):
    """
    Fetch user info using a Google access token (alternative flow).

    Args:
        access_token: OAuth 2.0 access token.

    Returns:
        dict with user info or None.
    """
    try:
        response = requests.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )
        if response.status_code != 200:
            return None

        data = response.json()
        return {
            "google_id": data["sub"],
            "email": data.get("email", ""),
            "name": data.get("name", ""),
            "avatar_url": data.get("picture", ""),
        }
    except (requests.RequestException, KeyError):
        return None
