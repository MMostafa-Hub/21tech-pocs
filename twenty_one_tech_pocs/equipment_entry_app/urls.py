from django.urls import path
from equipment_entry_app.views import GenerateView

urlpatterns = [
    path('generate/<str:asset_id>', GenerateView.as_view(), name="generate")
]
