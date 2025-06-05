from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from bson import ObjectId  # Import ObjectId for MongoDB
from .models import Patient
import json
from django.db.models import Q
from dashboard import threshold

def list_patients(request):
    search_query = request.GET.get('q', '').strip() # Get and strip whitespace
    patients_queryset = Patient.objects.all()

    if search_query:
        # --- NEW LOGIC FOR MULTI-WORD SEARCH ---
        search_words = search_query.split() # Split the query into individual words

        # Initialize a Q object that will combine all word conditions with AND
        # Start with an empty Q object that evaluates to True
        combined_name_conditions = Q()

        for word in search_words:
            # For each word, create a Q object that searches in first_name OR last_name
            word_conditions = Q(first_name__icontains=word) | \
                              Q(last_name__icontains=word)
            
            # Combine this word's conditions with the overall combined_name_conditions using AND (&)
            combined_name_conditions &= word_conditions
        # --- END NEW LOGIC ---

        # Start with the combined name conditions
        filter_conditions = combined_name_conditions

        # Attempt to add ID-based filtering if the query looks like a valid ObjectId
        # This will ONLY work for full, exact 24-character hexadecimal ObjectIds.
        # It will NOT work for partial ID strings (e.g., "101").
        if len(search_query) == 24 and all(c in '0123456789abcdefABCDEF' for c in search_query.lower()):
            try:
                object_id_search = ObjectId(search_query)
                # If it's a valid ObjectId, add an exact match for _id to the OR conditions
                filter_conditions |= Q(_id=object_id_search)
            except Exception:
                # If it looked like an ObjectId but was somehow invalid,
                # we just proceed with the name search part (which is already in filter_conditions).
                pass
        
        # Apply the final combined filter conditions to the queryset
        patients_queryset = patients_queryset.filter(filter_conditions)

    # Fetch only the necessary fields for efficiency and the JSON response
    # '_id' is included as it's needed for the 'id' conversion
    patients = patients_queryset.values('first_name', 'last_name', '_id')

    # Convert queryset to list and format for JSON response (converting ObjectId to string 'id')
    formatted_patients = []
    for patient in patients:
        formatted_patients.append({
            "id": str(patient["_id"]), # Convert ObjectId to string as expected by JavaScript
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
