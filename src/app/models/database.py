

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.sql import func
from app.core.database import Base
from app.models.task import TaskPriority, TaskStatus


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=True)
    hashed_password = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship
    tasks = relationship("Task", back_populates="owner", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    # Use native_enum=False for SQLite compatibility in tests
    priority = Column(Enum(TaskPriority, native_enum=False, length=20), default=TaskPriority.MEDIUM)
    status = Column(Enum(TaskStatus, native_enum=False, length=20), default=TaskStatus.PENDING)
    due_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Foreign key
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationship
    owner = relationship("User", back_populates="tasks")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    jti : Mapped[str] = mapped_column(String(255), primary_key=True, index=True)
    user_id : Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    expiry_date : Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    revoked : Mapped[bool] = mapped_column(Boolean, default=False)
    user = relationship("User", back_populates="refresh_tokens")

