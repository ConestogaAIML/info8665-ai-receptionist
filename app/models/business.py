from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Business(Base):
    __tablename__ = "businesses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    phone: Mapped[str] = mapped_column(String(30), default="")
    email: Mapped[str] = mapped_column(String(255), default="")
    address: Mapped[str] = mapped_column(Text, default="")
    business_hours: Mapped[str] = mapped_column(Text, default="")
    website: Mapped[str] = mapped_column(String(500), default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    faqs: Mapped[list["BusinessFAQ"]] = relationship(  # noqa: F821
        "BusinessFAQ", back_populates="business", cascade="all, delete-orphan"
    )
