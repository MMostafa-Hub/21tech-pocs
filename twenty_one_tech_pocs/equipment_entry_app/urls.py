from django.urls import path
from equipment_entry_app.views import GenerateAssetView, GenerateBulkAssetView

urlpatterns = [
    path('generate/<str:asset_name>/',
         GenerateAssetView.as_view(), name="generate_asset"),
    path('generate-bulk/<str:asset_name>/',
         GenerateBulkAssetView.as_view(), name="generate_bulk_asset"),
]
