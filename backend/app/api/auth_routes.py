"""
Auth routes — registration, login, and current user profile.

Multi-tenant model:
  - Register with tenant_name to create a new organization (admin role)
  - Register with tenant_slug to join an existing organization (analyst role)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.security import create_access_token
from app.database.connection import get_db
from app.database.models.tenant import Tenant
from app.database.models.user import User
from app.schemas.auth_schema import RegisterRequest, TokenResponse, UserResponse
from app.services.auth.auth_service import AuthService

router = APIRouter()


def _user_response(user: User, tenant: Tenant) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        role=user.role,
        tenant_id=user.tenant_id,
        tenant_name=tenant.name,
        tenant_slug=tenant.slug,
    )


@router.post("/register", response_model=UserResponse)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    if not request.tenant_name and not request.tenant_slug:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide either tenant_name (new org) or tenant_slug (join existing).",
        )

    try:
        user = AuthService.register_user(
            db=db,
            email=request.email,
            username=request.username,
            password=request.password,
            tenant_name=request.tenant_name,
            tenant_slug=request.tenant_slug,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    tenant = db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
    return _user_response(user, tenant)


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = AuthService.authenticate_user(
        db=db,
        username=form_data.username,
        password=form_data.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    return _user_response(current_user, tenant)
