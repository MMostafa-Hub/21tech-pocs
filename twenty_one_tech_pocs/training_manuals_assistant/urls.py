from django.urls import path
from .views import ProcessTrainingManualView

app_name = 'training_manuals_assistant'

urlpatterns = [
    path('process-training-manual/', ProcessTrainingManualView.as_view(), name='process_training_manual'),
] 