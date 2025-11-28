from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    pass_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    roles: Mapped[list["Role"]] = relationship(
        "Role", secondary="user_roles", back_populates="users"
    )
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    projects: Mapped[list["Project"]] = relationship(
        "Project", back_populates="owner", foreign_keys="[Project.owner_id]"
    )


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255))

    users: Mapped[list["User"]] = relationship(
        "User", secondary="user_roles", back_populates="roles"
    )
    access_rules: Mapped[list["AccessRule"]] = relationship(
        "AccessRule", back_populates="role", cascade="all, delete-orphan"
    )


class UserRole(Base):
    __tablename__ = "user_roles"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    )


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    token_hash: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")


class BusinessElement(Base):
    __tablename__ = "business_elements"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255))

    access_rules: Mapped[list["AccessRule"]] = relationship(
        "AccessRule", back_populates="element", cascade="all, delete-orphan"
    )


class AccessRule(Base):
    __tablename__ = "access_rules"

    id: Mapped[int] = mapped_column(primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"))
    element_id: Mapped[int] = mapped_column(
        ForeignKey("business_elements.id", ondelete="CASCADE")
    )

    read_permission: Mapped[bool] = mapped_column(Boolean, default=False)
    read_all_permission: Mapped[bool] = mapped_column(Boolean, default=False)
    create_permission: Mapped[bool] = mapped_column(Boolean, default=False)
    update_permission: Mapped[bool] = mapped_column(Boolean, default=False)
    update_all_permission: Mapped[bool] = mapped_column(Boolean, default=False)
    delete_permission: Mapped[bool] = mapped_column(Boolean, default=False)
    delete_all_permission: Mapped[bool] = mapped_column(Boolean, default=False)

    role: Mapped["Role"] = relationship("Role", back_populates="access_rules")
    element: Mapped["BusinessElement"] = relationship(
        "BusinessElement", back_populates="access_rules"
    )

    __table_args__ = (
        UniqueConstraint("role_id", "element_id", name="unique_role_element"),
    )


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    owner: Mapped["User"] = relationship("User", back_populates="projects")
