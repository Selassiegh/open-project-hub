from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from .models import CreditLine, Farmer, InsurancePolicy, Payout, Repayment, WeatherReading

MAX_CREDIT_ZAR = Decimal("50000")
INSURANCE_RATE = Decimal("0.03")
SUPPORTED_CROPS = {"maize", "beans", "sorghum", "wheat", "vegetables"}


def approve_credit(db: Session, farmer: Farmer, package_cost: Decimal, include_insurance: bool, due_date: date | None) -> CreditLine:
    if farmer.kyc_status != "verified":
        raise ValueError("Farmer KYC must be verified before credit can be approved")
    if not farmer.cooperative.verified_by_admin:
        raise ValueError("The cooperative must be verified before credit can be approved")
    if farmer.farm_size_hectares < Decimal("0.5"):
        raise ValueError("Farm size is below the cooperative's starting limit")
    if farmer.crop_type.lower() not in SUPPORTED_CROPS:
        raise ValueError("Crop type is outside the starting credit programme")
    premium = (package_cost * INSURANCE_RATE).quantize(Decimal("0.01")) if include_insurance else Decimal("0")
    total = package_cost + premium
    if total > MAX_CREDIT_ZAR:
        raise ValueError(f"This request is above the ZAR {MAX_CREDIT_ZAR:,.0f} starting limit")
    credit_line = CreditLine(
        farmer_id=farmer.id,
        inputs_value_zar=package_cost,
        insurance_premium_zar=premium,
        total_owed_zar=total,
        disbursed_date=date.today(),
        repay_due_date=due_date or date.today() + timedelta(days=180),
        status="active",
    )
    db.add(credit_line)
    db.flush()
    if include_insurance:
        db.add(InsurancePolicy(
            farmer_id=farmer.id,
            credit_line_id=credit_line.id,
            trigger_type="drought",
            rainfall_threshold_mm=Decimal("20"),
            coverage_zar=package_cost,
            region_weather_station_id=farmer.cooperative.region,
            active=True,
        ))
    db.commit()
    db.refresh(credit_line)
    return credit_line


def check_weather_triggers(db: Session, trigger_date: date | None = None) -> list[Payout]:
    check_date = trigger_date or date.today()
    policies = db.scalars(select(InsurancePolicy).where(InsurancePolicy.active.is_(True)).options(joinedload(InsurancePolicy.credit_line), joinedload(InsurancePolicy.farmer).joinedload(Farmer.cooperative))).all()
    payouts: list[Payout] = []
    for policy in policies:
        reading = db.scalar(select(WeatherReading).where(WeatherReading.region == policy.farmer.cooperative.region, WeatherReading.date == check_date))
        if reading is None or reading.rainfall_mm >= policy.rainfall_threshold_mm:
            continue
        duplicate = db.scalar(select(Payout).where(Payout.policy_id == policy.id, Payout.triggered_date == check_date))
        if duplicate:
            continue
        amount = min(policy.coverage_zar, policy.credit_line.total_owed_zar)
        if amount <= 0:
            policy.active = False
            continue
        payout = Payout(policy_id=policy.id, amount_zar=amount, triggered_date=check_date, reason=f"Drought: {reading.rainfall_mm} mm rainfall, below {policy.rainfall_threshold_mm} mm threshold")
        policy.credit_line.total_owed_zar -= amount
        if policy.credit_line.total_owed_zar <= 0:
            policy.credit_line.total_owed_zar = Decimal("0")
            policy.credit_line.status = "paid"
            policy.active = False
        db.add(payout)
        payouts.append(payout)
    db.commit()
    return payouts


def record_repayment(db: Session, credit_line: CreditLine, amount: Decimal, method: str) -> Repayment:
    if credit_line.status != "active":
        raise ValueError("This credit line is already settled")
    payment = min(amount, credit_line.total_owed_zar)
    credit_line.total_owed_zar -= payment
    if credit_line.total_owed_zar <= 0:
        credit_line.total_owed_zar = Decimal("0")
        credit_line.status = "paid"
    repayment = Repayment(credit_line_id=credit_line.id, amount_zar=payment, date=date.today(), method=method)
    db.add(repayment)
    db.commit()
    db.refresh(repayment)
    return repayment


def sms_summary(db: Session, farmer_id: int) -> str:
    farmer = db.get(Farmer, farmer_id)
    if farmer is None:
        raise ValueError("Farmer not found")
    owed = sum((line.total_owed_zar for line in farmer.credit_lines if line.status == "active"), Decimal("0"))
    return f"Harvest Credit: {farmer.name}, you owe ZAR {owed:,.2f}. Repay after harvest at your cooperative."
