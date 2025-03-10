from django.urls import path
from .views import ProcessMaintenanceDocumentView

urlpatterns = [
    path('process-document/', ProcessMaintenanceDocumentView.as_view(), name='process-maintenance-document'),
]