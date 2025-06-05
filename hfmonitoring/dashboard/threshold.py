# --- Oxygen Saturation (SpO2) ---
# Value < 90% is Critical
# Value >= 90% and < 95% is Caution
SPO2_CRITICAL_THRESHOLD = 90
SPO2_CAUTION_THRESHOLD = 95

# --- Weight (kg) ---
# Critical if current weight is more than X kg higher than the previous day's weight.
WEIGHT_DAILY_INCREASE_CRITICAL_KG = 3

# --- Heart Rate (bpm) ---
# Value < 60 bpm is Critical (Bradycardia - too slow)
# Value > 100 bpm is Critical (Tachycardia - too fast)
HR_NORMAL_MIN = 60
HR_NORMAL_MAX = 100

# --- Blood Pressure (mmHg) ---
# New BP categories based on provided definitions:
# 1) normal (<120 systolic and <80 mm Hg diastolic)
# 2) elevated (120–129 systolic and <80 mm Hg diastolic)
# 3) stage 1 hypertension (130–139 systolic or 80–89 mm Hg diastolic)
# 4) stage 2 hypertension (≥140 systolic or ≥90 mm Hg diastolic)

# Normal BP
BP_NORMAL_SYSTOLIC_MAX = 119
BP_NORMAL_DIASTOLIC_MAX = 79

# Elevated BP
BP_ELEVATED_SYSTOLIC_MIN = 120
BP_ELEVATED_SYSTOLIC_MAX = 129
BP_ELEVATED_DIASTOLIC_MAX = 79 # Diastolic must be < 80 for Elevated

# Stage 1 Hypertension
BP_STAGE1_SYSTOLIC_MIN = 130
BP_STAGE1_SYSTOLIC_MAX = 139
BP_STAGE1_DIASTOLIC_MIN = 80
BP_STAGE1_DIASTOLIC_MAX = 89

# Stage 2 Hypertension (Critical/High)
BP_STAGE2_SYSTOLIC_MIN = 140
BP_STAGE2_DIASTOLIC_MIN = 90