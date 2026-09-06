"""Create the Harvest Credit MVP tables."""
from alembic import op
import sqlalchemy as sa

revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("cooperatives", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(160), nullable=False), sa.Column("region", sa.String(120), nullable=False), sa.Column("contact", sa.String(120), nullable=False), sa.Column("verified_by_admin", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.create_table("farmers", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("coop_id", sa.Integer(), sa.ForeignKey("cooperatives.id"), nullable=False), sa.Column("name", sa.String(160), nullable=False), sa.Column("phone", sa.String(30), nullable=False, unique=True), sa.Column("pin", sa.String(20), nullable=False), sa.Column("id_number", sa.String(30), nullable=False), sa.Column("farm_size_hectares", sa.Numeric(10, 2), nullable=False), sa.Column("crop_type", sa.String(80), nullable=False), sa.Column("gps_location", sa.String(100), nullable=False), sa.Column("kyc_status", sa.String(30), nullable=False), sa.Column("kyc_verified_by", sa.String(120)), sa.Column("id_photo_filename", sa.String(255)))
    op.create_table("input_packages", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(120), nullable=False), sa.Column("cost_zar", sa.Numeric(12, 2), nullable=False), sa.Column("description", sa.Text(), nullable=False))
    op.create_table("credit_lines", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("farmer_id", sa.Integer(), sa.ForeignKey("farmers.id"), nullable=False), sa.Column("inputs_value_zar", sa.Numeric(12, 2), nullable=False), sa.Column("insurance_premium_zar", sa.Numeric(12, 2), nullable=False), sa.Column("total_owed_zar", sa.Numeric(12, 2), nullable=False), sa.Column("disbursed_date", sa.Date(), nullable=False), sa.Column("repay_due_date", sa.Date(), nullable=False), sa.Column("status", sa.String(30), nullable=False))
    op.create_table("insurance_policies", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("farmer_id", sa.Integer(), sa.ForeignKey("farmers.id"), nullable=False), sa.Column("credit_line_id", sa.Integer(), sa.ForeignKey("credit_lines.id"), nullable=False, unique=True), sa.Column("trigger_type", sa.String(30), nullable=False), sa.Column("rainfall_threshold_mm", sa.Numeric(8, 2), nullable=False), sa.Column("coverage_zar", sa.Numeric(12, 2), nullable=False), sa.Column("region_weather_station_id", sa.String(80), nullable=False), sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.create_table("weather_readings", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("region", sa.String(120), nullable=False), sa.Column("date", sa.Date(), nullable=False), sa.Column("rainfall_mm", sa.Numeric(8, 2), nullable=False), sa.Column("source", sa.String(80), nullable=False), sa.UniqueConstraint("region", "date", name="uq_weather_region_date"))
    op.create_table("payouts", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("policy_id", sa.Integer(), sa.ForeignKey("insurance_policies.id"), nullable=False), sa.Column("amount_zar", sa.Numeric(12, 2), nullable=False), sa.Column("triggered_date", sa.Date(), nullable=False), sa.Column("reason", sa.String(255), nullable=False))
    op.create_table("repayments", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("credit_line_id", sa.Integer(), sa.ForeignKey("credit_lines.id"), nullable=False), sa.Column("amount_zar", sa.Numeric(12, 2), nullable=False), sa.Column("date", sa.Date(), nullable=False), sa.Column("method", sa.String(30), nullable=False))


def downgrade() -> None:
    for table in ("repayments", "payouts", "weather_readings", "insurance_policies", "credit_lines", "input_packages", "farmers", "cooperatives"):
        op.drop_table(table)
