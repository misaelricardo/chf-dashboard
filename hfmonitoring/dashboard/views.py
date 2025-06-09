from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from bson import ObjectId  # Import ObjectId for MongoDB
from .models import Patient
import json
from django.db.models import Q
from dashboard import threshold
from datetime import datetime, time, date
import logging

# It's a good practice to set up a logger to see errors on the server side
logger = logging.getLogger(__name__)

def patient_landing_page(request):
    """
    Renders the initial landing page that prompts the user
    to select a patient.
    """
    return render(request, "dashboard/patient_landing.html")


# RENAMED: This function now serves as the API for the search dropdown
def list_patients_api(request):
    """
    API endpoint to search for patients and return a JSON list.
    """
    search_query = request.GET.get('q', '').strip()
    patients_queryset = Patient.objects.all()

    if search_query:
        search_words = search_query.split()
        combined_name_conditions = Q()
        for word in search_words:
            word_conditions = Q(first_name__icontains=word) | Q(last_name__icontains=word)
            combined_name_conditions &= word_conditions
        
        filter_conditions = combined_name_conditions
        
        if len(search_query) == 24 and all(c in '0123456789abcdefABCDEF' for c in search_query.lower()):
            try:
                object_id_search = ObjectId(search_query)
                filter_conditions |= Q(_id=object_id_search)
            except Exception:
                pass
        
        patients_queryset = patients_queryset.filter(filter_conditions)

    patients = patients_queryset.values('first_name', 'last_name', '_id')
    
    formatted_patients = []
    for patient in patients:
        formatted_patients.append({
            "id": str(patient["_id"]),
            "first_name": patient.get("first_name", ""),
            "last_name": patient.get("last_name", "")
        })

    return JsonResponse(formatted_patients, safe=False)
def get_patient(request, patient_id):
    # Ensure the patient_id is a valid ObjectId
    try:
        patient_id = ObjectId(patient_id)
    except Exception as e:
        return JsonResponse({"error": "Invalid Patient ID format"}, status=400)

    try:
        patient = Patient.objects.get(_id=patient_id)
        # Calculate BMI for every vitals record
        for v in patient.vitals:
            height = v.get("height")
            weight = v.get("weight")
            bmi = None
            if height and weight and height > 0:
                height_m = height / 100
                bmi = round(weight / (height_m ** 2), 2)
            v["bmi"] = bmi  # mutate in-place
        
        return JsonResponse({
            "id": str(patient._id),  # Convert ObjectId to string for JSON response
            "first_name": patient.first_name,
            "last_name": patient.last_name,
            "sex": patient.sex,
            "date_of_birth": patient.date_of_birth.isoformat() if patient.date_of_birth else None,
            "contacts": patient.contacts,
            "emergency_contact": patient.emergency_contact,
            "vitals": patient.vitals,
        })
    except Patient.DoesNotExist:
        return JsonResponse({"error": "Patient not found"}, status=404)

def patient_detail(request, patient_id):
    # Ensure the patient_id is a valid ObjectId
    try:
        patient_id = ObjectId(patient_id)
    except Exception as e:
        return JsonResponse({"error": "Invalid Patient ID format"}, status=400)

    patient = Patient.objects.get(_id=patient_id)
    vitals = patient.vitals

    for v in vitals:
        height = v.get("height")
        weight = v.get("weight")
        bmi = None
        if height and weight and height > 0:
            height_m = height / 100
            bmi = round(weight / (height_m ** 2), 2)
        v["bmi"] = bmi

    # Fetch all patients and exclude the _id field for better readability
    all_patients = Patient.objects.all().values()
    patients_list = [
        {
        "id": str(p["_id"]),
        "full_name": f"{p.get('first_name', '')} {p.get('last_name', '')}".strip(),
        **{k: v for k, v in p.items() if k != "_id"}
    }
        for p in all_patients
    ]

    # Prepare vital data for the patient
    if vitals:
        timestamps = [v["timestamp"].strftime("%d-%m-%Y") for v in vitals]
        systolic_bp_values = [v["systolic_bp"] for v in vitals]
        diastolic_bp_values = [v["diastolic_bp"] for v in vitals]
        latest_systolic_bp = systolic_bp_values[-1] if systolic_bp_values else None
        latest_diastolic_bp = diastolic_bp_values[-1] if diastolic_bp_values else None
        heart_rate_values = [v["heart_rate"] for v in vitals]
        latest_heart_rate = heart_rate_values[-1] if heart_rate_values else None
        weight_values = [v["weight"] for v in vitals]
        latest_weight = weight_values[-1] if weight_values else None
        sp02_values = [v["oxygen_saturation"] for v in vitals]
        latest_sp02 = sp02_values[-1] if sp02_values else None
        height_values = [v.get("height") for v in vitals]
        latest_height = height_values[-1] if height_values else None
        bmi_values = [v.get("bmi") for v in vitals]
        latest_bmi = bmi_values[-1] if bmi_values else None

         # --- LOGIC FOR LATEST WEIGHT COLOR ---
        if len(weight_values) >= 2: # Need at least two readings to calculate change
            previous_day_weight = weight_values[-2] # Second to last weight
            current_day_weight = latest_weight
            weight_change = current_day_weight - previous_day_weight

            if abs(weight_change) > threshold.WEIGHT_DAILY_INCREASE_CRITICAL_KG:
                latest_weight_color_class = "text-red-500" # Critical change (increase or decrease)
            else:
                latest_weight_color_class = "text-blue-500" # Normal change
        elif len(weight_values) == 1: # Only one reading, no change to compare
            latest_weight_color_class = "text-blue-500" # Default to blue
        # --- END COLOR LOGIC ---

    else:
        timestamps = []
        systolic_bp_values = []
        diastolic_bp_values = []
        heart_rate_values = []
        weight_values = []
        sp02_values = []
        height_values = []
        bmi_values = []
        latest_systolic_bp = None
        latest_diastolic_bp = None
        latest_heart_rate = None
        latest_weight = None
        latest_sp02 = None
        latest_height = None
        latest_bmi = None
        latest_weight_color_class = "text-gray-500"
    # Pass patient data and the list of all patients to the template
    context = {
        "patient": patient,
        "patient_id": str(patient._id),
        "patients_list": patients_list,
        "timestamps": json.dumps(timestamps),
        "systolic_bp_values": json.dumps(systolic_bp_values),
        "diastolic_bp_values": json.dumps(diastolic_bp_values),
        "latest_systolic_bp": latest_systolic_bp,
        "latest_diastolic_bp": latest_diastolic_bp,
        "heart_rate_values": json.dumps(heart_rate_values),
        "latest_heart_rate": latest_heart_rate,
        "weight_values": json.dumps(weight_values),
        "latest_weight":latest_weight,
        "sp02_values": json.dumps(sp02_values),
        "latest_sp02": latest_sp02,
        "height_values": json.dumps(height_values),
        "latest_height": latest_height,
        "bmi_values": json.dumps(bmi_values),
        "latest_bmi": latest_bmi,

        # --- THESE THRESHOLD VALUES HAVE ALREADY BEEN ADDED TO THE CONTEXT ---
        "SPO2_CRITICAL_THRESHOLD": threshold.SPO2_CRITICAL_THRESHOLD,
        "SPO2_CAUTION_THRESHOLD": threshold.SPO2_CAUTION_THRESHOLD,
        "HR_NORMAL_MIN": threshold.HR_NORMAL_MIN,
        "HR_NORMAL_MAX": threshold.HR_NORMAL_MAX,
        "WEIGHT_DAILY_INCREASE_CRITICAL_KG": threshold.WEIGHT_DAILY_INCREASE_CRITICAL_KG,
        
        # BP Categories
        "BP_NORMAL_SYSTOLIC_MAX": threshold.BP_NORMAL_SYSTOLIC_MAX,
        "BP_NORMAL_DIASTOLIC_MAX": threshold.BP_NORMAL_DIASTOLIC_MAX,
        "BP_ELEVATED_SYSTOLIC_MIN": threshold.BP_ELEVATED_SYSTOLIC_MIN,
        "BP_ELEVATED_SYSTOLIC_MAX": threshold.BP_ELEVATED_SYSTOLIC_MAX,
        "BP_ELEVATED_DIASTOLIC_MAX": threshold.BP_ELEVATED_DIASTOLIC_MAX,
        "BP_STAGE1_SYSTOLIC_MIN": threshold.BP_STAGE1_SYSTOLIC_MIN,
        "BP_STAGE1_SYSTOLIC_MAX": threshold.BP_STAGE1_SYSTOLIC_MAX,
        "BP_STAGE1_DIASTOLIC_MIN": threshold.BP_STAGE1_DIASTOLIC_MIN,
        "BP_STAGE1_DIASTOLIC_MAX": threshold.BP_STAGE1_DIASTOLIC_MAX,
        "BP_STAGE2_SYSTOLIC_MIN": threshold.BP_STAGE2_SYSTOLIC_MIN,
        "BP_STAGE2_DIASTOLIC_MIN": threshold.BP_STAGE2_DIASTOLIC_MIN,
        # --- END OF THRESHOLD ADDITIONS ---

        "latest_weight_color_class": latest_weight_color_class,
    }
    return render(request, "dashboard/patient.html", context)

def generate_abnormal_report(request, patient_id):
    """
    API endpoint to generate a comprehensive report for a specific patient,
    including categorized abnormal readings.
    """
    try:
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')

        if not start_date_str or not end_date_str:
            return JsonResponse({"error": "Missing date range parameters."}, status=400)

        start_date = datetime.combine(datetime.strptime(start_date_str, '%Y-%m-%d'), time.min)
        end_date = datetime.combine(datetime.strptime(end_date_str, '%Y-%m-%d'), time.max)
        patient_obj_id = ObjectId(patient_id)

        patient = get_object_or_404(Patient, _id=patient_obj_id)
        
        patient_vitals = getattr(patient, 'vitals', [])
        if not isinstance(patient_vitals, list):
            return JsonResponse({'report_data': []})

        patient_vitals_in_range = []
        for v in patient_vitals:
            ts = v.get('timestamp')
            if isinstance(ts, datetime) and start_date <= ts <= end_date:
                height, weight = v.get("height"), v.get("weight")
                if isinstance(height, (int, float)) and isinstance(weight, (int, float)) and height > 0:
                    v["bmi"] = round(weight / ((height / 100) ** 2), 2)
                else:
                    v["bmi"] = None
                patient_vitals_in_range.append(v)
        
        def calculate_stats(key):
            vals = [v[key] for v in patient_vitals_in_range if v.get(key) is not None and isinstance(v.get(key), (int, float))]
            if not vals: return {'avg': 'N/A', 'min': 'N/A', 'max': 'N/A'}
            return {'avg': round(sum(vals) / len(vals), 1), 'min': min(vals), 'max': max(vals)}

        stats = {
            "systolic_bp": calculate_stats('systolic_bp'),
            "diastolic_bp": calculate_stats('diastolic_bp'),
            "heart_rate": calculate_stats('heart_rate'),
            "oxygen_saturation": calculate_stats('oxygen_saturation'),
            "weight": calculate_stats('weight'),
            "bmi": calculate_stats('bmi'),
        }

        abnormal_instances = []
        all_vitals_sorted = sorted([v for v in patient_vitals if isinstance(v.get('timestamp'), datetime)], key=lambda v: v.get('timestamp'))

        for i, vital in enumerate(all_vitals_sorted):
            if not (vital.get('timestamp') and start_date <= vital.get('timestamp') <= end_date): continue
            
            abnormal_details = {}
            
            # --- MODIFIED: BP Check with descriptive categories ---
            systolic, diastolic = vital.get("systolic_bp"), vital.get("diastolic_bp")
            if isinstance(systolic, (int, float)) and isinstance(diastolic, (int, float)):
                if systolic >= threshold.BP_STAGE2_SYSTOLIC_MIN or diastolic >= threshold.BP_STAGE2_DIASTOLIC_MIN:
                    abnormal_details['Blood Pressure'] = f"{systolic}/{diastolic} mmHg (Stage 2 Hypertension)"
                elif (threshold.BP_STAGE1_SYSTOLIC_MIN <= systolic <= threshold.BP_STAGE1_SYSTOLIC_MAX) or \
                     (threshold.BP_STAGE1_DIASTOLIC_MIN <= diastolic <= threshold.BP_STAGE1_DIASTOLIC_MAX):
                    abnormal_details['Blood Pressure'] = f"{systolic}/{diastolic} mmHg (Stage 1 Hypertension)"
                elif (threshold.BP_ELEVATED_SYSTOLIC_MIN <= systolic <= threshold.BP_ELEVATED_SYSTOLIC_MAX) and \
                     (diastolic < threshold.BP_ELEVATED_DIASTOLIC_MAX):
                     # Note: Elevated BP is also considered abnormal in this context
                    abnormal_details['Blood Pressure'] = f"{systolic}/{diastolic} mmHg (Elevated)"

            # --- MODIFIED: Heart Rate check with descriptive categories ---
            hr = vital.get("heart_rate")
            if isinstance(hr, (int, float)):
                if hr > threshold.HR_NORMAL_MAX:
                    abnormal_details['Heart Rate'] = f"{hr} bpm (Tachycardia / Too Fast)"
                elif hr < threshold.HR_NORMAL_MIN:
                    abnormal_details['Heart Rate'] = f"{hr} bpm (Bradycardia / Too Slow)"

            # --- MODIFIED: Oxygen Saturation check with descriptive categories ---
            spo2 = vital.get("oxygen_saturation")
            if isinstance(spo2, (int, float)):
                if spo2 < threshold.SPO2_CRITICAL_THRESHOLD:
                    abnormal_details['Oxygen Saturation'] = f"{spo2}% (Dangerous)"
                elif spo2 < threshold.SPO2_CAUTION_THRESHOLD:
                    abnormal_details['Oxygen Saturation'] = f"{spo2}% (Caution)"

            # --- MODIFIED: Weight Change check with descriptive category ---
            if i > 0:
                previous_vital = all_vitals_sorted[i-1]
                current_weight, previous_weight = vital.get('weight'), previous_vital.get('weight')
                if isinstance(current_weight, (int, float)) and isinstance(previous_weight, (int, float)):
                    weight_change = current_weight - previous_weight
                    if abs(weight_change) > threshold.WEIGHT_DAILY_INCREASE_CRITICAL_KG:
                        abnormal_details['Weight Change'] = f"{weight_change:+.2f} kg from previous reading (Significant Change)"
            
            if abnormal_details:
                abnormal_instances.append({"date": vital.get('timestamp').strftime('%Y-%m-%d %H:%M'), "details": abnormal_details})
        
        dob_val = patient.date_of_birth
        if isinstance(dob_val, (datetime, date)):
            dob_str = dob_val.strftime('%Y-%m-%d')
        elif isinstance(dob_val, str) and dob_val:
            dob_str = dob_val
        else:
            dob_str = 'N/A'

        report_data = [{
            "patient_info": {
                "name": f"{patient.first_name} {patient.last_name}",
                "id": str(patient._id),
                "dob": dob_str,
                "sex": patient.sex
            },
            "stats": stats,
            "abnormal_instances": abnormal_instances
        }]

        return JsonResponse({'report_data': report_data})

    except Exception as e:
        logger.error(f"An unexpected error occurred in generate_abnormal_report: {e}", exc_info=True)
        return JsonResponse({"error": "An unexpected server error occurred."}, status=500)
