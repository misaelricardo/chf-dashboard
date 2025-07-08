import random
from faker import Faker
from datetime import datetime, timedelta
from dashboard import threshold

# --- Django Setup ---
# This section is crucial to allow the script to interact with your Django models.
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hfmonitoring.settings")
django.setup()
# --- End of Django Setup ---

from django.contrib.auth.models import User
from dashboard.models import Patient # Import your Patient model

fake = Faker()

# --- Clear existing data using the Django ORM ---
User.objects.all().delete()
Patient.objects.all().delete()

DAYS_TO_GENERATE = 120
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

    if anomaly_type:
        sample_range_start = max(0, num_days - 14)
        if sample_range_start < num_days - 1:
            recent_anomaly_days = random.sample(range(sample_range_start, num_days - 1), k=min(random.randint(2, 4), (num_days - 1) - sample_range_start))
            anomaly_days = recent_anomaly_days + [num_days - 1]
        else:
            anomaly_days = [num_days - 1] if num_days > 0 else []
    else:
        anomaly_days = []

    previous_day_weight = current_weight

    # --- FIXED: The logic for generating daily vitals was missing and has been restored. ---
    for i in range(num_days + 1):
        timestamp = start_date + timedelta(days=i)

        weight = random_deviation(current_weight, -0.2, 0.2)
        systolic = random_deviation(current_systolic, -2, 2)
        diastolic = random_deviation(current_diastolic, -1, 1)
        hr = random_deviation(current_hr, -2, 2)
        sp02 = current_sp02

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
        "date_of_birth": fake.date_of_birth(minimum_age=40, maximum_age=90),
        "contacts": {
            "phone": fake.phone_number(),
            "email": fake.email()
        },
        "vitals": generate_daily_vitals_trend(start_date, DAYS_TO_GENERATE, height, base_vitals, anomaly_type)
    }


# --- Create 3 specific doctors ---
dr_house = User.objects.create_user(username='dr_house', password='password123')
dr_strange = User.objects.create_user(username='dr_strange', password='password123')
dr_who = User.objects.create_user(username='dr_who', password='password123')
print("✅ Created 3 doctor users.")

# --- Patient data with anomaly types ---
patients_to_create = [
    {"first_name": "Agus", "last_name": "Prawira", "anomaly": "normal"},
    {"first_name": "Budi", "last_name": "Cahyono", "anomaly": "weight_spike"},
    {"first_name": "Chandra", "last_name": "Wijaya", "anomaly": "weight_decrease"},
    {"first_name": "Dewi", "last_name": "Lestari", "anomaly": "hr_abnormal"},
    {"first_name": "Eka", "last_name": "Fitriani", "anomaly": "spo2_caution"},
    {"first_name": "Fajar", "last_name": "Nugroho", "anomaly": "spo2_critical"},
    {"first_name": "Hendra", "last_name": "Gunawan", "anomaly": "bp_elevated"},
    {"first_name": "Indah", "last_name": "Puspita", "anomaly": "bp_stage1"},
    {"first_name": "Joko", "last_name": "Susilo", "anomaly": "bp_stage2"},
    # --- ADDED: Two new patients with normal profiles ---
    {"first_name": "Klara", "last_name": "Tan", "anomaly": "normal"},
    {"first_name": "Leo", "last_name": "Wijaya", "anomaly": "normal"},
]

# --- Create patients and assign doctors with specific logic ---
print("Inserting patient data and assigning doctors...")
for p_data in patients_to_create:
    # Generate the patient data dictionary
    patient_dict = generate_patient_specific(
        p_data["first_name"], 
        p_data["last_name"], 
        p_data["anomaly"], 
        START_DATE
    )
    
    # Create the Patient object using the Django ORM
    vitals_data = patient_dict.pop('vitals')
    patient = Patient.objects.create(**patient_dict)
    patient.vitals = vitals_data
    
    # --- MODIFIED: Assignment Logic ---
    # 1. Assign all patients with an anomaly to Dr. House
    if p_data["anomaly"] != 'normal':
        patient.doctors.add(dr_house)
        
    # 2. Assign the new patient "Klara Tan" to Dr. Strange
    if p_data["first_name"] == "Klara":
        patient.doctors.add(dr_strange)
        
    # 3. Assign the new patient "Leo Wijaya" to Dr. Who
    if p_data["first_name"] == "Leo":
        patient.doctors.add(dr_who)
        
    patient.save()

print(f"✅ Inserted {len(patients_to_create)} test patients and assigned doctors according to rules.")
