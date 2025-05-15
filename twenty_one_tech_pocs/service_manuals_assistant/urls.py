from django.urls import path
from .views import ProcessServiceManualDocumentView

urlpatterns = [
    path('process-document/', ProcessServiceManualDocumentView.as_view(), name='process-service-manual-document'),
] 