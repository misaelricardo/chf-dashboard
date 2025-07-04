from django.contrib import admin
from django.urls import path
from dashboard.views import (
    patient_landing_page, 
    list_patients_api, 
    get_patient, 
    patient_detail, 
    generate_abnormal_report
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('patients/', patient_landing_page, name='patient_landing_page'),
    path('api/list-patients/', list_patients_api, name='list_patients_api'),
    path('patients/<str:patient_id>/json', get_patient, name='get_patient'),
    path("patients/<str:patient_id>/", patient_detail, name="patient_detail"),
    path('api/patients/<str:patient_id>/generate-abnormal-report/', generate_abnormal_report, name='generate_abnormal_report'),
]