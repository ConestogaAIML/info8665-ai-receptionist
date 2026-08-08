from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class RiskAssessment(Base):
    """Stored customer risk features + ML prediction for manager review."""

    __tablename__ = "risk_assessments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    client_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("clients.id"), nullable=True, index=True
    )
    client_name: Mapped[str] = mapped_column(String(200), nullable=False, default="Walk-in")
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    waiting_days: Mapped[int] = mapped_column(Integer, nullable=False)
    sms_received: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_new_customer: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # Best available slot from advisor search
    preferred_hour: Mapped[str] = mapped_column(String(20), nullable=False, default="")
    preferred_weekday: Mapped[str] = mapped_column(String(20), nullable=False, default="")
    best_slot_risk: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    # Profile risk used for high-risk flagging (avg across business hours)
    profile_risk: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    recommendation: Mapped[str] = mapped_column(String(40), nullable=False, default="")
    is_high_risk: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    client: Mapped["Client | None"] = relationship("Client", back_populates="risk_assessments")
