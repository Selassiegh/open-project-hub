from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Cooperative(Base):
    __tablename__ = "cooperatives"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(160))
    region: Mapped[str] = mapped_column(String(120))
    contact: Mapped[str] = mapped_column(String(120))
    verified_by_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    farmers: Mapped[list["Farmer"]] = relationship(back_populates="cooperative")


class Farmer(Base):
    __tablename__ = "farmers"

    id: Mapped[int] = mapped_column(primary_key=True)
    coop_id: Mapped[int] = mapped_column(ForeignKey("cooperatives.id"), index=True)
    name: Mapped[str] = mapped_column(String(160))
    phone: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    pin: Mapped[str] = mapped_column(String(20))
    id_number: Mapped[str] = mapped_column(String(30))
    farm_size_hectares: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    crop_type: Mapped[str] = mapped_column(String(80))
    gps_location: Mapped[str] = mapped_column(String(100))
    kyc_status: Mapped[str] = mapped_column(String(30), default="pending")
    kyc_verified_by: Mapped[str | None] = mapped_column(String(120), nullable=True)
    id_photo_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cooperative: Mapped[Cooperative] = relationship(back_populates="farmers")
    credit_lines: Mapped[list["CreditLine"]] = relationship(back_populates="farmer")
    policies: Mapped[list["InsurancePolicy"]] = relationship(back_populates="farmer")


class InputPackage(Base):
    __tablename__ = "input_packages"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    cost_zar: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    description: Mapped[str] = mapped_column(Text)


class CreditLine(Base):
    __tablename__ = "credit_lines"

    id: Mapped[int] = mapped_column(primary_key=True)
    farmer_id: Mapped[int] = mapped_column(ForeignKey("farmers.id"), index=True)
    inputs_value_zar: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    insurance_premium_zar: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    total_owed_zar: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    disbursed_date: Mapped[date] = mapped_column(Date)
    repay_due_date: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(30), default="active")
    farmer: Mapped[Farmer] = relationship(back_populates="credit_lines")
    policy: Mapped["InsurancePolicy | None"] = relationship(back_populates="credit_line", uselist=False)
    repayments: Mapped[list["Repayment"]] = relationship(back_populates="credit_line")


class InsurancePolicy(Base):
    __tablename__ = "insurance_policies"

    id: Mapped[int] = mapped_column(primary_key=True)
    farmer_id: Mapped[int] = mapped_column(ForeignKey("farmers.id"), index=True)
    credit_line_id: Mapped[int] = mapped_column(ForeignKey("credit_lines.id"), unique=True)
    trigger_type: Mapped[str] = mapped_column(String(30))
    rainfall_threshold_mm: Mapped[Decimal] = mapped_column(Numeric(8, 2))
    coverage_zar: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    region_weather_station_id: Mapped[str] = mapped_column(String(80))
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    farmer: Mapped[Farmer] = relationship(back_populates="policies")
    credit_line: Mapped[CreditLine] = relationship(back_populates="policy")
    payouts: Mapped[list["Payout"]] = relationship(back_populates="policy")


class WeatherReading(Base):
    __tablename__ = "weather_readings"
    __table_args__ = (UniqueConstraint("region", "date", name="uq_weather_region_date"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    region: Mapped[str] = mapped_column(String(120), index=True)
    date: Mapped[date] = mapped_column(Date, index=True)
    rainfall_mm: Mapped[Decimal] = mapped_column(Numeric(8, 2))
    source: Mapped[str] = mapped_column(String(80))


class Payout(Base):
    __tablename__ = "payouts"

    id: Mapped[int] = mapped_column(primary_key=True)
    policy_id: Mapped[int] = mapped_column(ForeignKey("insurance_policies.id"), index=True)
    amount_zar: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    triggered_date: Mapped[date] = mapped_column(Date)
    reason: Mapped[str] = mapped_column(String(255))
    policy: Mapped[InsurancePolicy] = relationship(back_populates="payouts")


class Repayment(Base):
    __tablename__ = "repayments"

    id: Mapped[int] = mapped_column(primary_key=True)
    credit_line_id: Mapped[int] = mapped_column(ForeignKey("credit_lines.id"), index=True)
    amount_zar: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    date: Mapped[date] = mapped_column(Date)
    method: Mapped[str] = mapped_column(String(30))
    credit_line: Mapped[CreditLine] = relationship(back_populates="repayments")
