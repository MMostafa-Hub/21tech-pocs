from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import status
from django.core.files.uploadedfile import UploadedFile
from .services import MaintenanceAssistantService
from .schemas import MaintenanceSchedule


class ProcessMaintenanceDocumentView(APIView):
    parser_classes = (MultiPartParser,)

    def post(self, request):
        try:
            if 'document' not in request.FILES:
                return Response(
                    {'error': 'No document provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            document: UploadedFile = request.FILES['document']
            if not document.name.lower().endswith('.pdf'):
                return Response(
                    {'error': 'Only PDF files are supported'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            service = MaintenanceAssistantService()
            try:
                result: MaintenanceSchedule = service.process_document(
                    document)
                # Convert Pydantic model to dict for JSON serialization
                return Response(result, status=status.HTTP_200_OK)
            finally:
                service.cleanup()

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
