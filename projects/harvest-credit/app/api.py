from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from .config import settings
from .database import get_db
from .models import Cooperative, CreditLine, Farmer, InputPackage, Payout, Repayment, WeatherReading
from .schemas import CreditLineCreate, FarmerCreate, KycUpdate, LoginRequest, RepaymentCreate, WeatherReadingCreate
from .services import approve_credit, check_weather_triggers, record_repayment, sms_summary

router = APIRouter()


def fail(message: str, code: int = status.HTTP_400_BAD_REQUEST) -> HTTPException:
    return HTTPException(code, detail=message)


@router.post("/auth/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    farmer = db.scalar(select(Farmer).where(Farmer.phone == payload.phone, Farmer.pin == payload.pin))
    if farmer is None:
        raise fail("Phone number or PIN is not correct", status.HTTP_401_UNAUTHORIZED)
    return {"farmer_id": farmer.id, "name": farmer.name, "cooperative_id": farmer.coop_id}


@router.get("/cooperatives")
def list_cooperatives(db: Session = Depends(get_db)):
    return db.scalars(select(Cooperative)).all()


@router.post("/cooperatives/{coop_id}/farmers", status_code=201)
def register_farmer(coop_id: int, payload: FarmerCreate, db: Session = Depends(get_db)):
    if db.get(Cooperative, coop_id) is None:
        raise fail("Cooperative not found", status.HTTP_404_NOT_FOUND)
    farmer = Farmer(coop_id=coop_id, **payload.model_dump())
    db.add(farmer)
    db.commit()
    db.refresh(farmer)
    return farmer


@router.patch("/farmers/{farmer_id}/kyc")
def update_kyc(farmer_id: int, payload: KycUpdate, db: Session = Depends(get_db)):
    farmer = db.get(Farmer, farmer_id)
    if farmer is None:
        raise fail("Farmer not found", status.HTTP_404_NOT_FOUND)
    farmer.kyc_status = "verified" if payload.verified else "rejected"
    farmer.kyc_verified_by = payload.verified_by
    db.commit()
    return farmer


@router.get("/input-packages")
def list_packages(db: Session = Depends(get_db)):
    return db.scalars(select(InputPackage)).all()


@router.post("/credit-lines", status_code=201)
def create_credit_line(payload: CreditLineCreate, db: Session = Depends(get_db)):
    farmer = db.scalar(select(Farmer).where(Farmer.id == payload.farmer_id).options(joinedload(Farmer.cooperative)))
    package = db.get(InputPackage, payload.input_package_id)
    if farmer is None or package is None:
        raise fail("Farmer or input package not found", status.HTTP_404_NOT_FOUND)
    try:
        return approve_credit(db, farmer, package.cost_zar, payload.include_insurance, payload.repay_due_date)
    except ValueError as error:
        raise fail(str(error)) from error


@router.get("/credit-lines/{credit_line_id}")
def get_credit_line(credit_line_id: int, db: Session = Depends(get_db)):
    line = db.scalar(select(CreditLine).where(CreditLine.id == credit_line_id).options(joinedload(CreditLine.farmer)))
    if line is None:
        raise fail("Credit line not found", status.HTTP_404_NOT_FOUND)
    return line


@router.post("/credit-lines/{credit_line_id}/repayments", status_code=201)
def repay(credit_line_id: int, payload: RepaymentCreate, db: Session = Depends(get_db)):
    line = db.get(CreditLine, credit_line_id)
    if line is None:
        raise fail("Credit line not found", status.HTTP_404_NOT_FOUND)
    try:
        return record_repayment(db, line, payload.amount_zar, payload.method)
    except ValueError as error:
        raise fail(str(error)) from error


@router.post("/weather-readings", status_code=201)
def add_weather_reading(payload: WeatherReadingCreate, db: Session = Depends(get_db)):
    reading = WeatherReading(**payload.model_dump())
    db.add(reading)
    try:
        db.commit()
    except Exception as error:
        db.rollback()
        raise fail("A weather reading already exists for this region and date") from error
    db.refresh(reading)
    return reading


@router.post("/weather/check-triggers")
def trigger_weather_check(trigger_date: date | None = None, db: Session = Depends(get_db)):
    payouts = check_weather_triggers(db, trigger_date)
    return {"triggered": len(payouts), "payouts": payouts}


@router.get("/farmers/{farmer_id}/sms-summary")
def farmer_sms_summary(farmer_id: int, db: Session = Depends(get_db)):
    try:
        return {"message": sms_summary(db, farmer_id)}
    except ValueError as error:
        raise fail(str(error), status.HTTP_404_NOT_FOUND) from error


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):
    return {
        "total_owed_zar": db.scalar(select(func.coalesce(func.sum(CreditLine.total_owed_zar), 0)).where(CreditLine.status == "active")) or 0,
        "pending_kyc": db.scalar(select(func.count(Farmer.id)).where(Farmer.kyc_status == "pending")) or 0,
        "active_credit_lines": db.scalar(select(func.count(CreditLine.id)).where(CreditLine.status == "active")) or 0,
        "upcoming_repayments": db.scalar(select(func.count(CreditLine.id)).where(CreditLine.status == "active", CreditLine.repay_due_date >= date.today())) or 0,
        "triggered_payouts": db.scalar(select(func.count(Payout.id))) or 0,
    }
