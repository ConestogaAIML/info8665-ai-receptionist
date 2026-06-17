from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class SentimentLog(Base):
    __tablename__ = "sentiment_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    conversation_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    text: Mapped[str] = mapped_column(Text, nullable=True)
    sentiment: Mapped[str] = mapped_column(String(20), nullable=False)          # positive | neutral | negative
    emotion: Mapped[str] = mapped_column(String(50), nullable=True)             # e.g. frustrated, happy, calm
    category: Mapped[str] = mapped_column(String(50), nullable=False)           # making_appointment | cancel_appointment | ask_question | other
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    escalate: Mapped[bool] = mapped_column(Boolean, default=False)
    corrected: Mapped[bool] = mapped_column(Boolean, default=False)
    correction_note: Mapped[str] = mapped_column(Text, nullable=True)
    logged_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
