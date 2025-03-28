import os
import pandas as pd
from django.core.management.base import BaseCommand
from django.conf import settings
from InsuranceClaimsRecords.models import Record

def parse_boolean(value):
    if isinstance(value, str):
        return value.strip().lower() in ['yes', 'true', '1']
    return bool(value)

def safe_str(value):
    try:
        if pd.isna(value): return ""
        return str(value)
    except:
        return ""

def safe_int(value):
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None

def safe_decimal(value):
    try:
        if isinstance(value, str) and value.strip().lower() == "nan":
            return None
        if pd.isna(value): return None
        return float(value)
    except:
        return None

def safe_date(value):
    try:
        dt = pd.to_datetime(value, errors="coerce")
        return None if pd.isna(dt) else dt.date()
    except:
        return None

class Command(BaseCommand):
    help = "Import records from CSV file into the database"

    def handle(self, *args, **options):
        file_path = os.path.join(settings.BASE_DIR, 'MLModel', 'Patient_records.csv')

        if not os.path.exists(file_path):
            self.stderr.write(self.style.ERROR("CSV file not found"))
            return

        df = pd.read_csv(file_path)
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_").str.replace(r'[^a-z0-9_]', '', regex=True)

        for index, row in df.iterrows():
            try:
                Record.objects.create(
                    record_type="Insurance Claim",
                    settlement_value=safe_decimal(row.get("settlementvalue")),
                    accident_type=safe_str(row.get("accidenttype")),
                    injury_prognosis=safe_str(row.get("injury_prognosis")),
                    special_health_expenses=safe_decimal(row.get("specialhealthexpenses")),
                    special_reduction=safe_decimal(row.get("specialreduction")),
                    special_overage=safe_decimal(row.get("specialoverage")),
                    general_rest=safe_decimal(row.get("generalrest")),
                    special_additional_injury=safe_decimal(row.get("specialadditionalinjury")),
                    special_earnings_loss=safe_decimal(row.get("specialearningsloss")),
                    special_usage_loss=safe_decimal(row.get("specialusageloss")),
                    special_medications=safe_decimal(row.get("specialmedications")),
                    special_asset_damage=safe_decimal(row.get("specialassetdamage")),
                    special_rehabilitation=safe_decimal(row.get("specialrehabilitation")),
                    special_fixes=safe_decimal(row.get("specialfixes")),
                    general_fixed=safe_decimal(row.get("generalfixed")),
                    general_uplift=safe_decimal(row.get("generaluplift")),
                    special_loaner_vehicle=safe_decimal(row.get("specialloanervehicle")),
                    special_trip_costs=safe_decimal(row.get("specialtripcosts")),
                    special_journey_expenses=safe_str(row.get("specialjourneyexpenses")),
                    special_therapy=safe_str(row.get("specialtherapy")),
                    exceptional_circumstances=parse_boolean(row.get("exceptional_circumstances")),
                    minor_psychological_injury=parse_boolean(row.get("minor_psychological_injury")),
                    dominant_injury=safe_str(row.get("dominant_injury")),
                    whiplash=parse_boolean(row.get("whiplash")),
                    vehicle_type=safe_str(row.get("vehicle_type")),
                    weather_conditions=safe_str(row.get("weather_conditions")),
                    vehicle_age=safe_int(row.get("vehicle_age")),
                    driver_age=safe_int(row.get("driver_age")),
                    number_of_passengers=safe_int(row.get("number_of_passengers")),
                    accident_description=safe_str(row.get("accident_description")),
                    injury_description=safe_str(row.get("injury_description")),
                    police_report_filed=parse_boolean(row.get("police_report_filed")),
                    witness_present=parse_boolean(row.get("witness_present")),
                    gender=safe_str(row.get("gender")),
                    accident_date=safe_date(row.get("accident_date")),
                    claim_date=safe_date(row.get("claim_date")),
                )
                self.stdout.write(self.style.SUCCESS(f"✅ Imported row {index + 1}"))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"❌ Error on row {index + 1}: {str(e)}"))
