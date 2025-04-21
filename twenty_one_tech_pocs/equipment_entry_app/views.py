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
            return Response({"error": "Please provide the attribute to generate"}, status=status.HTTP_400_BAD_REQUEST)

        # Use the vector store’s fuzzy_search (which uses label_mapping internally)
        historical_values = vector_store.fuzzy_search(
            asset_name, attribute_key)
        target_field = vector_store.label_mapping.get(attribute_key)
        field_description = vector_store.field_descriptions.get(
            attribute_key, "No description available.")

        if target_field is None:
            # Use 400 Bad Request for invalid client input
            return Response({"error": "Invalid attribute provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Return early if no historical values found, but with a 200 OK status as the request was valid
        if not historical_values:
            return Response({"historical_values": [], "llm_response": None}, status=status.HTTP_200_OK)

        # Use prompt factory for asset_entry_prompt
        equipment_prompt = PromptFactory.get_prompt("asset_entry_prompt")

        load_dotenv()
        # Use .get for safer access
        api_key = os.environ.get("OPENAI_API_KEY_21T")
        if not api_key:
            # Use 500 Internal Server Error if config is missing
            return Response({"error": "Server configuration error: OpenAI API key not found."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            model = ChatOpenAI(model="gpt-4o-mini",
                               temperature=1, api_key=api_key)
            chain = equipment_prompt | model
            llm_result = chain.invoke({
                "asset_name": asset_name,
                "historical_values": historical_values,
                "target_field": target_field,
                "field_description": field_description  # Pass description to prompt
            })
        except Exception as e:
            # Log the exception e for debugging
            print(f"Error invoking LLM chain: {e}")
            # Use 500 Internal Server Error for issues during LLM call
            return Response({"error": "Error generating response from LLM."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "historical_values": historical_values,
            "llm_response": llm_result.content
        }, status=status.HTTP_200_OK)
