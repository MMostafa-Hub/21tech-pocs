import os

from dotenv import load_dotenv
from langchain_openai.chat_models import ChatOpenAI
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from equipment_entry_app.prompt_factory import PromptFactory
from equipment_entry_app.vector_store.equipment_entry import EquipmentEntryElasticSearch

# Initialize vector store for asset entry
vector_store = EquipmentEntryElasticSearch()


class GenerateAssetView(APIView):
    def options(self, request, asset_name, *args, **kwargs):
        """
        Handle OPTIONS preflight requests for CORS
        """
        response = Response(status=status.HTTP_200_OK)
        # Adjust the allowed origins, methods, and headers as needed
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Accept, Content-Type, ngrok-skip-browser-warning"
        return response

    def get(self, request, asset_name):
        attribute_key = request.query_params.get('attribute', None)
        if attribute_key is None:
            return Response({"error": "Please provide the attribute to generate"})

        # Use the vector store’s fuzzy_search (which uses label_mapping internally)
        historical_values = vector_store.fuzzy_search(
            asset_name, attribute_key)
        target_field = vector_store.label_mapping.get(attribute_key)
        if target_field is None:
            return Response({"error": "Invalid attribute provided"})
        if historical_values == []:
            return Response({"historical_values": historical_values, "response": None})

        # Use prompt factory for asset_entry_prompt
        equipment_prompt = PromptFactory.get_prompt("asset_entry_prompt")

        load_dotenv()
        api_key = os.environ["OPENAI_API_KEY_21T"]

        model = ChatOpenAI(model="gpt-4o-mini", temperature=1, api_key=api_key)
        chain = equipment_prompt | model
        x = chain.invoke({
            "asset_name": asset_name,
            "historical_values": historical_values,
            "target_field": target_field
        })

        return Response({
            "historical_values": historical_values,
            "llm_response": x.content
        })
