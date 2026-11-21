import json
import re
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.database.models.tenant import Tenant
from app.database.models.training_session import TrainingSession
from app.database.models.user import User
from app.schemas.evaluation_schema import AnalystResponse, EvaluationResult
from app.schemas.scenario_schema import ScenarioSchema


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "tenant"


class AuthService:

    @staticmethod
    def register_user(
        db: Session,
        email: str,
        username: str,
        password: str,
        tenant_name: Optional[str] = None,
        tenant_slug: Optional[str] = None,
    ) -> User:
        if db.query(User).filter(User.email == email).first():
            raise ValueError("Email already registered")

        if db.query(User).filter(User.username == username).first():
            raise ValueError("Username already taken")

        tenant = None

        if tenant_slug:
            tenant = db.query(Tenant).filter(Tenant.slug == tenant_slug).first()
            if tenant is None:
                raise ValueError("Tenant not found")
        else:
            name = tenant_name or f"{username}'s Organization"
            slug_base = slugify(tenant_name or username)
            slug = slug_base
            counter = 1

            while db.query(Tenant).filter(Tenant.slug == slug).first():
                slug = f"{slug_base}-{counter}"
                counter += 1

            tenant = Tenant(name=name, slug=slug)
            db.add(tenant)
            db.flush()

        user = User(
            email=email,
            username=username,
            hashed_password=hash_password(password),
            tenant_id=tenant.id,
            role="admin" if tenant_name else "analyst",
        )

        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def authenticate_user(
        db: Session,
        username: str,
        password: str,
    ) -> Optional[User]:
        user = (
            db.query(User)
            .filter(
                (User.username == username) | (User.email == username)
            )
            .first()
        )

        if user is None or not verify_password(password, user.hashed_password):
            return None

        return user
