import csv
from datetime import date
from decimal import Decimal
from pathlib import Path

from app.database import Base, SessionLocal, engine
from app.models import Cooperative, Farmer, InputPackage, WeatherReading
from app.services import approve_credit, check_weather_triggers


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if db.query(Cooperative).count():
            print("Seed data already exists; nothing changed.")
            return
        coops = [
            Cooperative(name="Limpopo Harvest Co-op", region="Limpopo", contact="015 555 0101", verified_by_admin=True),
            Cooperative(name="Eastern Cape Growers", region="Eastern Cape", contact="047 555 0102", verified_by_admin=True),
            Cooperative(name="KwaZulu-Natal Field Union", region="KwaZulu-Natal", contact="035 555 0103", verified_by_admin=True),
        ]
        db.add_all(coops)
        db.flush()
        crops = ["maize", "beans", "sorghum", "vegetables", "wheat"]
        for index in range(10):
            farmer = Farmer(
                coop_id=coops[index % 3].id,
                name=["Thandi Mokoena", "Sipho Dlamini", "Lerato Ndlovu", "Nomsa Khumalo", "Mandla Mthembu", "Ayanda Cele", "Palesa Molefe", "Bongani Zulu", "Zanele Maseko", "Vusi Nkosi"][index],
                phone=f"+2782000{index + 1:04d}",
                pin="1234",
                id_number=f"80010150090{index}",
                farm_size_hectares=Decimal(str(1.2 + index / 10)),
                crop_type=crops[index % len(crops)],
                gps_location=f"-{23 + index / 10:.4f}, {29 + index / 10:.4f}",
                kyc_status="verified" if index < 8 else "pending",
                kyc_verified_by="Co-op demo agent" if index < 8 else None,
                id_photo_filename=f"demo-id-{index + 1}.jpg",
            )
            db.add(farmer)
        db.add_all([
            InputPackage(name="Maize starter pack", cost_zar=Decimal("12000"), description="Certified maize seed and starter fertilizer"),
            InputPackage(name="Vegetable resilience pack", cost_zar=Decimal("8500"), description="Vegetable seed, compost and crop protection"),
            InputPackage(name="Small grain pack", cost_zar=Decimal("15000"), description="Sorghum or wheat seed and fertilizer"),
        ])
        db.commit()
        farmers = db.query(Farmer).filter(Farmer.kyc_status == "verified").all()
        maize_package = db.query(InputPackage).filter(InputPackage.name == "Maize starter pack").one()
        approve_credit(db, farmers[0], maize_package.cost_zar, True, date(2026, 12, 31))
        for index, farmer in enumerate(farmers[1:4], start=1):
            approve_credit(db, farmer, Decimal(str(8000 + index * 1000)), True, date(2026, 12, 31))
        with Path(__file__).with_name("data").joinpath("weather.csv").open(newline="") as weather_file:
            for row in csv.DictReader(weather_file):
                db.add(WeatherReading(region=row["region"], date=date.fromisoformat(row["date"]), rainfall_mm=Decimal(row["rainfall_mm"]), source=row["source"]))
        db.commit()
        payouts = check_weather_triggers(db, date(2026, 9, 6))
        print(f"Seeded {len(coops)} cooperatives, 10 farmers, 4 credit lines, and {len(payouts)} drought payout(s).")


if __name__ == "__main__":
    seed()
