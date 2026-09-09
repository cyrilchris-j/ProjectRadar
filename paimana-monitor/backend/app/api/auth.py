"""
Auth API — Firebase token verification, current-user lookup.

Flow:
  1. Frontend signs in via Firebase SDK → receives Firebase ID Token.
  2. Frontend sends POST /api/auth/verify with the ID Token.
  3. Backend verifies token with Firebase Admin SDK.
  4. Backend upserts the user row (populates firebase_uid on first login).
  5. All subsequent requests carry the Firebase ID Token as Bearer token.
     get_current_user() verifies it and returns the User ORM object.
"""
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.firebase_admin import verify_firebase_token
from app.config.settings import get_settings
from app.database.connection import get_db
from app.models.orm import AuditLog, User, UserRole
from app.schemas.schemas import FirebaseVerifyRequest, UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])


# ─── Dependency: resolve current user from Firebase Bearer token ──────────────

async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Extract the Firebase ID Token from the Authorization header,
    verify it, and return the matching User ORM object.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or malformed Authorization header.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    id_token = authorization.removeprefix("Bearer ").strip()
    decoded = verify_firebase_token(id_token)
    firebase_uid: str = decoded["uid"]
    if firebase_uid not in get_settings().allowed_firebase_uids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This Firebase account is not authorized to access the platform.",
        )

    result = await db.execute(select(User).where(User.firebase_uid == firebase_uid))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found. Contact an administrator.",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled.",
        )

    return user


def require_roles(*roles):
    """Dependency factory — raises 403 if user's role is not in allowed list."""
    async def _check(current_user: User = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return _check


# ─── POST /api/auth/verify ────────────────────────────────────────────────────

@router.post("/verify", response_model=UserOut)
async def verify_and_upsert(
    body: FirebaseVerifyRequest,
    db: AsyncSession = Depends(get_db),
    request: Request = None,
):
    """
    Called by the frontend immediately after Firebase sign-in.
    Verifies the Firebase ID token, then:
      - If a matching user (by firebase_uid OR email) exists → update firebase_uid.
      - Otherwise → creates a new user row with role=viewer.
    Returns the full user profile.
    """
    decoded = verify_firebase_token(body.id_token)
    firebase_uid: str = decoded["uid"]
    if firebase_uid not in get_settings().allowed_firebase_uids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This Firebase account is not authorized to access the platform.",
        )
    email: str = decoded.get("email", "")
    display_name: str = decoded.get("name", email.split("@")[0])

    # Try lookup by firebase_uid first, then fall back to email
    result = await db.execute(select(User).where(User.firebase_uid == firebase_uid))
    user = result.scalar_one_or_none()

    if not user and email:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

    if user:
        # Link firebase_uid if not already set (handles first login after migration)
        if user.firebase_uid != firebase_uid:
            user.firebase_uid = firebase_uid
        user.last_login_at = datetime.utcnow()
    else:
        # Brand-new user — default role is viewer; an admin can promote later
        user = User(
            email=email,
            full_name=display_name,
            firebase_uid=firebase_uid,
            role=UserRole.viewer,
        )
        db.add(user)

    # Audit log
    db.add(AuditLog(
        user_id=user.id,
        action="login",
        entity_type="user",
        entity_id=str(user.id),
        ip_address=request.client.host if request else None,
    ))

    await db.flush()
    return UserOut.model_validate(user)


# ─── GET /api/auth/me ─────────────────────────────────────────────────────────

@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)):
    """Return the currently authenticated user's profile."""
    return current_user
