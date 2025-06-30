import random
import pymongo
from faker import Faker
from datetime import datetime, timedelta
from dashboard import threshold

fake = Faker()
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["hf_monitoring_db"]
patients_collection = db["patients"]
patients_collection.delete_many({})  # Clear existing records

DAYS_TO_GENERATE = 120  # 4 months
START_DATE = datetime.now() - timedelta(days=DAYS_TO_GENERATE)


def random_deviation(base, min_dev, max_dev):
    return round(base + random.uniform(min_dev, max_dev), 1)


def get_base_vitals():
    return {
        "weight": round(random.uniform(70, 80), 1),
        "systolic": random.randint(105, 115),
        "diastolic": random.randint(68, 78),
        "hr": random.randint(70, 85),
        "sp02": random.randint(97, 99)
    }


def inject_anomaly(day_index, anomaly_type, vitals_entry, previous_day_weight):
    if anomaly_type == 'weight_spike':
        vitals_entry["weight"] = round(previous_day_weight + random.uniform(
            threshold.WEIGHT_DAILY_INCREASE_CRITICAL_KG + 0.5,
            threshold.WEIGHT_DAILY_INCREASE_CRITICAL_KG + 2
        ), 1)
    elif anomaly_type == 'weight_decrease':
        vitals_entry["weight"] = round(previous_day_weight - random.uniform(
            threshold.WEIGHT_DAILY_INCREASE_CRITICAL_KG + 0.5,
            threshold.WEIGHT_DAILY_INCREASE_CRITICAL_KG + 2
        ), 1)
    elif anomaly_type == 'hr_abnormal':
        vitals_entry["heart_rate"] = random.choice([
            random.randint(threshold.HR_NORMAL_MIN - 5, threshold.HR_NORMAL_MIN - 1),
            random.randint(threshold.HR_NORMAL_MAX + 1, threshold.HR_NORMAL_MAX + 10)
        ])
    elif anomaly_type == 'spo2_caution':
        vitals_entry["oxygen_saturation"] = random.randint(
            threshold.SPO2_CRITICAL_THRESHOLD,
            threshold.SPO2_CAUTION_THRESHOLD - 1
        )
    elif anomaly_type == 'spo2_critical':
        vitals_entry["oxygen_saturation"] = random.randint(
            threshold.SPO2_CRITICAL_THRESHOLD - 3,
            threshold.SPO2_CRITICAL_THRESHOLD - 1
        )
    elif anomaly_type == 'bp_elevated':
        vitals_entry["systolic_bp"] = random.randint(
            threshold.BP_ELEVATED_SYSTOLIC_MIN,
            threshold.BP_ELEVATED_SYSTOLIC_MAX
        )
        vitals_entry["diastolic_bp"] = random.randint(60, threshold.BP_ELEVATED_DIASTOLIC_MAX - 1)
    elif anomaly_type == 'bp_stage1':
        if random.random() < 0.5:
            vitals_entry["systolic_bp"] = random.randint(
                threshold.BP_STAGE1_SYSTOLIC_MIN,
                threshold.BP_STAGE1_SYSTOLIC_MAX
            )
        else:
            vitals_entry["diastolic_bp"] = random.randint(
                threshold.BP_STAGE1_DIASTOLIC_MIN,
                threshold.BP_STAGE1_DIASTOLIC_MAX
            )
    elif anomaly_type == 'bp_stage2':
        if random.random() < 0.5:
            vitals_entry["systolic_bp"] = random.randint(
                threshold.BP_STAGE2_SYSTOLIC_MIN,
                threshold.BP_STAGE2_SYSTOLIC_MIN + 10
            )
        else:
            vitals_entry["diastolic_bp"] = random.randint(
                threshold.BP_STAGE2_DIASTOLIC_MIN,
                threshold.BP_STAGE2_DIASTOLIC_MIN + 5
            )


def generate_daily_vitals_trend(start_date, num_days, height, base_vitals, anomaly_type=None):
    vitals = []
    current_weight = base_vitals["weight"]
    current_systolic = base_vitals["systolic"]
    current_diastolic = base_vitals["diastolic"]
    current_hr = base_vitals["hr"]
    current_sp02 = base_vitals["sp02"]

    # Anomaly days: mostly in last 14 days plus last day always included
    if anomaly_type:
        # Ensure we don't try to sample from a negative range if num_days < 15
        sample_range_start = max(0, num_days - 14)
        if sample_range_start < num_days -1 :
            recent_anomaly_days = random.sample(range(sample_range_start, num_days - 1), k=min(random.randint(2, 4), (num_days - 1) - sample_range_start))
            anomaly_days = recent_anomaly_days + [num_days - 1]
        else:
            anomaly_days = [num_days - 1]
    else:
        anomaly_days = []

    previous_day_weight = current_weight

    # FIXED: The loop now runs one extra time to include today
    for i in range(num_days + 1):
        timestamp = start_date + timedelta(days=i)

        weight = random_deviation(current_weight, -0.2, 0.2)
        systolic = random_deviation(current_systolic, -2, 2)
        diastolic = random_deviation(current_diastolic, -1, 1)
        hr = random_deviation(current_hr, -2, 2)
        sp02 = current_sp02  # stable

        weight = max(base_vitals["weight"] - 3, min(base_vitals["weight"] + 3, weight))
        systolic = max(95, min(threshold.BP_NORMAL_SYSTOLIC_MAX - 1, systolic))
        diastolic = max(60, min(threshold.BP_NORMAL_DIASTOLIC_MAX - 1, diastolic))
        hr = max(threshold.HR_NORMAL_MIN + 5, min(threshold.HR_NORMAL_MAX - 5, hr))
        sp02 = max(95, min(99, sp02))

        entry = {
            "timestamp": timestamp,
            "weight": round(weight, 1),
            "height": height,
            "systolic_bp": int(systolic),
            "diastolic_bp": int(diastolic),
            "heart_rate": int(hr),
            "oxygen_saturation": int(sp02)
        }

        if i in anomaly_days:
            inject_anomaly(i, anomaly_type, entry, previous_day_weight)

        vitals.append(entry)

        # Update current base values for next day
        current_weight = entry["weight"]
        current_systolic = entry["systolic_bp"]
        current_diastolic = entry["diastolic_bp"]
        current_hr = entry["heart_rate"]
        current_sp02 = entry["oxygen_saturation"]
        previous_day_weight = entry["weight"]

    return vitals


def generate_patient_specific(first_name, last_name, anomaly_type, start_date):
    gender = random.choice(["Male", "Female"])
    height = random.randint(165, 185) if gender == "Male" else random.randint(150, 170)
    base_vitals = get_base_vitals()

    return {
        "first_name": first_name,
        "last_name": last_name,
        "sex": gender,
        "date_of_birth": fake.date_of_birth(minimum_age=40, maximum_age=90).strftime("%Y-%m-%d"),
        "contacts": {
            "phone": fake.phone_number(),
            "email": fake.email()
        },
        "vitals": generate_daily_vitals_trend(start_date, DAYS_TO_GENERATE, height, base_vitals, anomaly_type)
    }


patients_data = [
    # Profil Normal
    generate_patient_specific("Agus", "Prawira", 'normal', START_DATE),
    # Profil untuk tes Berat Badan
    generate_patient_specific("Budi", "Cahyono", 'weight_spike', START_DATE),
    generate_patient_specific("Chandra", "Wijaya", 'weight_decrease', START_DATE),
    # Profil untuk tes Detak Jantung
    generate_patient_specific("Dewi", "Lestari", 'hr_abnormal', START_DATE),
    # Profil untuk tes  Saturasi Oksigen
    generate_patient_specific("Eka", "Fitriani", 'spo2_caution', START_DATE),
    generate_patient_specific("Fajar", "Nugroho", 'spo2_critical', START_DATE),
    # Profil untuk tes Tekanan Darah
    generate_patient_specific("Hendra", "Gunawan", 'bp_elevated', START_DATE),
    generate_patient_specific("Indah", "Puspita", 'bp_stage1', START_DATE),
    generate_patient_specific("Joko", "Susilo", 'bp_stage2', START_DATE),
]

patients_collection.insert_many(patients_data)
print("✅ Inserted test patient data with recent and last-day anomalies.")
