from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class BusinessFAQ(Base):
    __tablename__ = "business_faqs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    business_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("businesses.id"), nullable=False, index=True
    )
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(100), default="")
    tags: Mapped[str] = mapped_column(String(500), default="")  # comma-separated
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    business: Mapped["Business"] = relationship(  # noqa: F821
        "Business", back_populates="faqs"
    )
