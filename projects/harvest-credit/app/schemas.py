from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class FarmerCreate(BaseModel):
    name: str
    phone: str
    pin: str = Field(min_length=4, max_length=20)
    id_number: str
    farm_size_hectares: Decimal = Field(gt=0)
    crop_type: str
    gps_location: str
    id_photo_filename: str | None = None


class KycUpdate(BaseModel):
    verified: bool
    verified_by: str


class LoginRequest(BaseModel):
    phone: str
    pin: str


class CreditLineCreate(BaseModel):
    farmer_id: int
    input_package_id: int
    include_insurance: bool = True
    repay_due_date: date | None = None


class RepaymentCreate(BaseModel):
    amount_zar: Decimal = Field(gt=0)
    method: str = Field(pattern="^(cash|mobile_money|coop_collection)$")


class WeatherReadingCreate(BaseModel):
    region: str
    date: date
    rainfall_mm: Decimal = Field(ge=0)
    source: str = "simulated_csv"


class ModelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
