from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(40), unique=True, nullable=False, index=True)
    price_monthly: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="EUR")
    max_berths: Mapped[int] = mapped_column(Integer, nullable=False)
    max_staff_users: Mapped[int] = mapped_column(Integer, nullable=False)
    allow_map: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    allow_payments: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    allow_advanced_dashboard: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    marinas = relationship("Marina", back_populates="subscription_plan")
    subscriptions = relationship("MarinaSubscription", back_populates="subscription_plan")


class MarinaSubscription(Base):
    __tablename__ = "marina_subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    marina_id: Mapped[int] = mapped_column(ForeignKey("marinas.id"), nullable=False, index=True)
    subscription_plan_id: Mapped[int] = mapped_column(
        ForeignKey("subscription_plans.id"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active")
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    marina = relationship("Marina", back_populates="subscriptions")
    subscription_plan = relationship("SubscriptionPlan", back_populates="subscriptions")
