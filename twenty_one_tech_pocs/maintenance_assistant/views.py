from django.core.files.uploadedfile import UploadedFile
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .schemas import MaintenanceSchedule
from .services import MaintenanceAssistantService
from .services.common import EAMApiService, LLMFactory
from .services.common.config_manager import ConfigManager  # Import ConfigManager


class ProcessMaintenanceDocumentView(APIView):
    parser_classes = (MultiPartParser,)

    def post(self, request):
        try:
            if "document" not in request.FILES:
                return Response(
                    {"error": "No document provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            document: UploadedFile = request.FILES["document"]
            create_in_eam = request.data.get(
                "create_in_eam", "false").lower() == "true"

            # Validate the file type
            if not document.name.lower().endswith(".pdf"):
                return Response(
                    {"error": "Only PDF files are supported"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            service = MaintenanceAssistantService()
            eam_api = EAMApiService()
            response_data = {}
            llm_factory = LLMFactory()
            config_manager = ConfigManager()  # Instantiate ConfigManager

            # Get LLM parameters from config manager
            llm_params = config_manager.get_llm_config()

            # Validate required parameters
            if not llm_params.get("name"):
                return Response(
                    {"error": "LLM_NAME not found in environment variables."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            llm = llm_factory.get_llm(
                llm_name=llm_params.pop("name"),
                **llm_params
            )
            try:
                # Process the document to extract maintenance data
                maintenance_schedule: MaintenanceSchedule = service.process_document(
                    document, llm=llm
                )
                response_data["extracted_data"] = maintenance_schedule.model_dump()

                # If requested, create the task plans and checklists in EAM
                if create_in_eam:
                    created_tasks = []

                    # Create the maintenance schedule in EAM
                    eam_api.create_maintenance_schedule(maintenance_schedule)

                    # Iterate through each task plan in the extracted data
                    # and create the task plans and checklists in EAM
                    for task_plan in maintenance_schedule.task_plans:
                        # Create the task plan
                        task_response = eam_api.create_task_plan(task_plan)
                        task_info = {
                            "task_code": task_plan.task_code,
                            "description": task_plan.description,
                            "api_response": task_response,
                            "checklists": [],
                        }

                        # Create each checklist for this task plan
                        for i, checklist_item in enumerate(task_plan.checklist):
                            checklist_response = eam_api.create_checklist(
                                task_plan.task_code,
                                checklist_item,
                                sequence=(i + 1) * 10,
                            )
                            task_info["checklists"].append(
                                {
                                    "checklist_id": checklist_item.checklist_id,
                                    "description": checklist_item.description,
                                    "api_response": checklist_response,
                                }
                            )

                        created_tasks.append(task_info)

                    response_data["created_in_eam"] = created_tasks

                return Response(response_data, status=status.HTTP_200_OK)
            finally:
                service.cleanup()

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
