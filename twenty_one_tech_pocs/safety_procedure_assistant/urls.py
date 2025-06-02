from django.urls import path
from .views import ProcessIncidentReportView

app_name = 'safety_procedure_assistant'

urlpatterns = [
    path('process-incident-report/', ProcessIncidentReportView.as_view(), name='process_incident_report'),
] 