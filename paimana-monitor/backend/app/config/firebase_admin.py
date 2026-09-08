"""
Firebase Admin SDK — initialise once at startup, verify ID tokens on every request.
"""
import logging
import os

import firebase_admin
from firebase_admin import auth, credentials
from fastapi import HTTPException, status

from app.config.settings import get_settings

logger = logging.getLogger(__name__)

_initialized = False


def _init_firebase() -> None:
    """Initialise Firebase Admin SDK (idempotent)."""
    global _initialized
    if _initialized or len(firebase_admin._apps):
        _initialized = True
        return

    settings = get_settings()
    sa_path = os.path.abspath(settings.FIREBASE_SERVICE_ACCOUNT_PATH)

    if not os.path.exists(sa_path):
        # In CI / local dev without credentials, log a warning — endpoints will
        # return 503 until the service-account file is placed at the path.
        logger.warning(
            "Firebase service-account file not found at %s. "
            "Auth endpoints will be unavailable. "
            "Download it from Firebase Console → Project Settings → Service Accounts.",
            sa_path,
        )
        return

    cred = credentials.Certificate(sa_path)
    firebase_admin.initialize_app(cred)
    _initialized = True
    logger.info("Firebase Admin SDK initialised (project: %s)", cred.project_id)


# Initialise at import time (main.py imports this module during startup)
_init_firebase()


def verify_firebase_token(id_token: str) -> dict:
    """
    Verify a Firebase ID token and return the decoded payload.

    Raises:
        HTTPException 503 — Firebase not configured (service account missing).
        HTTPException 401 — Token is invalid or expired.
    """
    if not _initialized or not len(firebase_admin._apps):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Firebase is not configured on this server. "
                "Please provide the service-account JSON file."
            ),
        )
    try:
        decoded = auth.verify_id_token(id_token, check_revoked=True)
        return decoded
    except auth.RevokedIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked. Please sign in again.",
        )
    except auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Please sign in again.",
        )
    except Exception as exc:
        logger.debug("Firebase token verification failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
        )
