import os
from dotenv import load_dotenv
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# Updated imports to use the new common directory
from twenty_one_tech_pocs.common import PromptFactory, LLMFactory, LLMsEnum
from .vector_store.equipment_entry import EquipmentEntryElasticSearch

# Initialize vector store for asset entry
vector_store = EquipmentEntryElasticSearch()
llm_factory = LLMFactory() # Instantiate the factory


class GenerateAssetView(APIView):
    def options(self, request, asset_name, *args, **kwargs):
        """
        Handle OPTIONS preflight requests for CORS
        """
        response = Response(status=status.HTTP_200_OK)
        # Adjust the allowed origins, methods, and headers as needed
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Accept, Content-Type, ngrok-skip-browser-warning"
        return response

    def post(self, request, asset_name):
        attribute_key = request.data.get('attribute', None)
        accepted_values_dict = request.data.get(
            'accepted_values', {})

        if attribute_key is None:
            return Response({"error": "Please provide the 'attribute' in the request body"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate accepted_values format (should be a dictionary)
        if not isinstance(accepted_values_dict, dict):
            return Response({"error": "'accepted_values' must be a JSON object (dictionary) in the request body"}, status=status.HTTP_400_BAD_REQUEST)

        # Format accepted values for the prompt
        accepted_values_str = "\n".join(
            [f"- {key}: {value}" for key, value in accepted_values_dict.items()])
        if not accepted_values_str:
            accepted_values_str = "None provided."

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
        try:
            equipment_prompt = PromptFactory.get_prompt("asset_entry_prompt")
        except ValueError as e:
             print(f"Error getting prompt: {e}")
             return Response({"error": "Server configuration error: Could not load prompt."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        load_dotenv()
        # API key is now handled internally by LLMFactory if needed (e.g., for OpenAI)
        # api_key = os.environ.get("OPENAI_API_KEY_21T")
        # if not api_key:
        #     return Response({"error": "Server configuration error: OpenAI API key not found."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            # Get LLM instance from factory
            # Assuming GPT4O_MINI is desired here, adjust if needed
            model = llm_factory.get_llm(llm_name=LLMsEnum.GPT4O_MINI.value,
                                        temperature=1)
            chain = equipment_prompt | model
            llm_result = chain.invoke({
                "asset_name": asset_name,
                "historical_values": historical_values,
                "target_field": target_field,
                "field_description": field_description,
                "accepted_values": accepted_values_str
            })
        except ValueError as e: # Catch specific validation errors from factory
            print(f"LLM Configuration Error: {e}")
            return Response({"error": f"Invalid LLM configuration: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            # Log the exception e for debugging
            print(f"Error invoking LLM chain: {e}")
            # Use 500 Internal Server Error for issues during LLM call
            return Response({"error": "Error generating response from LLM."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "historical_values": historical_values,
            "llm_response": llm_result.content
        }, status=status.HTTP_200_OK)


class GenerateBulkAssetView(APIView):
    """
    API View for generating predictions for multiple asset attributes in bulk.
    """

    def options(self, request, asset_name, *args, **kwargs):
        """
        Handle OPTIONS preflight requests for CORS
        """
        response = Response(status=status.HTTP_200_OK)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Accept, Content-Type, ngrok-skip-browser-warning"
        return response

    def post(self, request, asset_name):
        """
        Handles POST requests to generate bulk predictions.
        Expects 'attributes' (list) and 'accepted_values' (dict) in the request body.
        """
        attributes_to_predict = request.data.get('attributes', None)
        accepted_values_dict = request.data.get('accepted_values', {})

        # --- Input Validation ---
        if attributes_to_predict is None:
            return Response({"error": "Please provide the 'attributes' list in the request body"}, status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(attributes_to_predict, list) or not attributes_to_predict:
            return Response({"error": "'attributes' must be a non-empty list in the request body"}, status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(accepted_values_dict, dict):
            return Response({"error": "'accepted_values' must be a JSON object (dictionary) in the request body"}, status=status.HTTP_400_BAD_REQUEST)

        # --- Setup ---
        predictions = {}
        load_dotenv()
        # API key handled by factory
        # api_key = os.environ.get("OPENAI_API_KEY_21T")
        # if not api_key:
        #     return Response({"error": "Server configuration error: OpenAI API key not found."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            # Get LLM and prompt once
            model = llm_factory.get_llm(llm_name=LLMsEnum.GPT4O_MINI.value,
                                        temperature=1)
            equipment_prompt = PromptFactory.get_prompt("asset_entry_prompt")
            chain = equipment_prompt | model
        except ValueError as e: # Catch specific validation errors from factory
            print(f"LLM/Prompt Configuration Error: {e}")
            return Response({"error": f"Invalid LLM/Prompt configuration: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            print(f"Error initializing LLM components: {e}")
            return Response({"error": "Error initializing LLM components."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Format accepted values once
        accepted_values_str = "\n".join([f"- {key}: {value}" for key, value in accepted_values_dict.items()])
        if not accepted_values_str:
            accepted_values_str = "None provided."

        # --- Prediction Loop ---
        for attribute_key in attributes_to_predict:
            target_field = vector_store.label_mapping.get(attribute_key)
            field_description = vector_store.field_descriptions.get(
                attribute_key, "No description available.")

            if target_field is None:
                print(
                    f"Warning: Invalid attribute '{attribute_key}' requested for asset '{asset_name}'. Skipping.")
                predictions[attribute_key] = None  # Indicate invalid attribute
                continue

            historical_values = vector_store.fuzzy_search(
                asset_name, attribute_key)

            if not historical_values:
                # Indicate no historical data
                predictions[attribute_key] = None
                continue

            # Invoke LLM for the current attribute
            try:
                llm_result = chain.invoke({
                    "asset_name": asset_name,
                    "historical_values": historical_values,
                    "target_field": target_field,
                    "field_description": field_description,
                    "accepted_values": accepted_values_str
                })
                predictions[attribute_key] = llm_result.content
            except Exception as e:
                print(
                    f"Error invoking LLM chain for attribute '{attribute_key}' on asset '{asset_name}': {e}")
                predictions[attribute_key] = None  # Indicate prediction error

        # --- Return Results ---
        return Response({"predictions": predictions}, status=status.HTTP_200_OK)
