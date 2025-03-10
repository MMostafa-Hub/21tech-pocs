from django.urls import path
from equipment_entry_app.views import GenerateAssetView

urlpatterns = [
    path('generate/<str:asset_name>/',
         GenerateAssetView.as_view(), name="generate_asset"),
]
