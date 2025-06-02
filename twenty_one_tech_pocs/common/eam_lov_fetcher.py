import requests
import json
# Assuming ConfigManager is in the same directory or accessible in PYTHONPATH
# If it's in the same directory, the relative import is fine:
# from .config_manager import ConfigManager # Import will be used by actual app

class EAMLOVFetcher:
    def __init__(self, base_url, eamid, tenant, session=None):
        self.base_url = base_url.rstrip('/')
        self.eamid = eamid
        self.tenant = tenant
        self.session = session if session else requests.Session()
        # Set common headers for the session
        self.session.headers.update({
            'Content-Type': 'application/x-www-form-urlencoded'
        })

    def _make_request(self, endpoint, payload):
        """
        Internal method to make a POST request to the EAM endpoint.
        It adds eamid and tenant to the payload.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        request_payload = payload.copy()
        request_payload['eamid'] = self.eamid
        request_payload['tenant'] = self.tenant
        
        try:
            response = self.session.post(url, data=request_payload)
            response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred while requesting {url}: {http_err}")
            print(f"Response status: {response.status_code}")
            response_text_snippet = "No response text."
            if hasattr(response, 'text'):
                response_text_snippet = response.text[:1000] # Log more of the response
            print(f"Response text snippet: {response_text_snippet}...")
            return None
        except requests.exceptions.RequestException as req_err:
            print(f"Request error occurred while requesting {url}: {req_err}")
            return None
        except json.JSONDecodeError as json_err:
            response_text_snippet = "N/A"
            if 'response' in locals() and hasattr(response, 'text'):
                response_text_snippet = response.text[:500]
            print(f"Error decoding JSON response from {url}: {json_err}. Response text snippet: {response_text_snippet}...")
            return None

    def fetch_category_values(self, organization, class_code, class_organization):
        """
        Fetches category values based on organization, class, and class organization.
        Returns a list of category strings (e.g., ["ATD55-AR-3H1"]).
        """
        payload = {
            "GRID_NAME": "LVCAT",
            "REQUEST_TYPE": "LIST.HEAD_DATA.STORED",
            "LOV_ALIAS_NAME_1": "control.org",
            "LOV_ALIAS_VALUE_1": organization,
            "LOV_ALIAS_TYPE_1": "text",
            "LOV_ALIAS_NAME_2": "parameter.class",
            "LOV_ALIAS_VALUE_2": class_code,
            "LOV_ALIAS_TYPE_2": "text",
            "LOV_ALIAS_NAME_3": "parameter.classorg",
            "LOV_ALIAS_VALUE_3": class_organization,
            "LOV_ALIAS_TYPE_3": "text",
            "LOV_ALIAS_NAME_4": "parameter.onlymatchclass",
            "LOV_ALIAS_VALUE_4": "",  # As per JS example
            "LOV_ALIAS_TYPE_4": "text"
        }
        
        response_data = self._make_request("GRIDDATA", payload)
        
        categories = []
        if response_data:
            try:
                # Path based on the provided successful JSON response structure
                data_items = response_data["pageData"]["grid"]["GRIDRESULT"]["GRID"]["DATA"]
                for item in data_items:
                    if "category" in item:
                        categories.append(item["category"])
            except KeyError as e:
                print(f"Error parsing category data: Key {e} not found in response.")
                # print(f"Response structure for debugging: {json.dumps(response_data, indent=2)}")
            except TypeError as e: 
                print(f"Error parsing category data: Type error ({e}) encountered, possibly due to unexpected response structure.")
                # print(f"Response structure for debugging: {json.dumps(response_data, indent=2)}")

        if not categories and response_data: # If categories list is empty but we got a response
             print("Could not extract category data, or no categories found for the given parameters.")
        elif not response_data: # If no response was received at all
             print("No response received from server when fetching categories.")
        return categories

    def fetch_cost_code_values(self, organization, usage_type, current_tab_name, user_function_name="OSOBJA", lov_tag_name="costcode", **kwargs):
        """
        Fetches cost code values. 
        Parameters are based on the initial description for the cost code LOV.
        Returns a list of cost code strings.
        """
        payload = {
            "popup": "true", 
            "GRID_NAME": "LVOBJCOST",
            "GRID_TYPE": "LOV",
            "REQUEST_TYPE": "LOV.HEAD_DATA.STORED", 
            "LOV_TAGNAME": lov_tag_name, 
            "usagetype": usage_type, 
            "USER_FUNCTION_NAME": user_function_name, 
            "CURRENT_TAB_NAME": current_tab_name, 
            "LOV_ALIAS_NAME_1": "control.org",
            "LOV_ALIAS_VALUE_1": organization,
            "LOV_ALIAS_TYPE_1": "text",
        }
        # Add any additional kwargs to the payload if they start with LOV_ALIAS_ or are other known params
        for key, value in kwargs.items():
            if key.startswith("LOV_ALIAS_") or key in ["param.flcust", "param.fleetcustorg"]: # Add other known keys if necessary
                payload[key] = value
            # For specific named LOV_ALIAS parameters from initial description
            elif key == "flcust":
                payload["LOV_ALIAS_NAME_2"] = "param.flcust"
                payload["LOV_ALIAS_VALUE_2"] = value
                payload["LOV_ALIAS_TYPE_2"] = "text"
            elif key == "fleetcustorg":
                payload["LOV_ALIAS_NAME_3"] = "param.fleetcustorg"
                payload["LOV_ALIAS_VALUE_3"] = value
                payload["LOV_ALIAS_TYPE_3"] = "text"


        # The endpoint for this is LOVPOP as per the initial description for cost codes
        response_data = self._make_request("LOVPOP", payload) 
        
        cost_codes = []
        if response_data:
            try:
                # Adjust parsing based on the actual structure of LVOBJCOST response
                # This is a generic placeholder, assuming a similar structure to LVCAT
                data_items = response_data["pageData"]["grid"]["GRIDRESULT"]["GRID"]["DATA"]
                for item in data_items:
                    # The field containing the cost code value might be different.
                    # Common names could be 'costcode', 'code', 'value'.
                    # Update "costcode" if the actual field name in the response is different.
                    if "costcode" in item: 
                        cost_codes.append(item["costcode"]) 
                    elif "code" in item: # Check for an alternative common name
                       cost_codes.append(item["code"])
                    # Add more checks if other field names are possible
            except KeyError as e:
                print(f"Error parsing cost code data: Key {e} not found in response.")
                # print(f"Full response for debugging cost codes: {json.dumps(response_data, indent=2)}")
            except TypeError:
                print("Error parsing cost code data: Unexpected structure in response.")
                # print(f"Full response for debugging cost codes: {json.dumps(response_data, indent=2)}")
        
        if not cost_codes and response_data:
             print("Could not extract cost_code data, or no cost_codes found for the given parameters.")
        elif not response_data:
             print("No response received from server when fetching cost_codes.")
        return cost_codes


def get_all_lov_data(config, params_map):
    """
    Fetches various LOV data based on the params_map and returns a dictionary.
    'config' should be an instance of a config provider (like ConfigManager) or a dict.
    'params_map' is a dictionary where keys are desired data types (e.g., "categories")
    and values are dicts of parameters for fetching that data.

    Example params_map:
    {
        "categories": {"organization": "*", "class_code": "TIRE", "class_organization": "*"},
        "cost_codes": {
            "organization": "*", 
            "usage_type": "lov", 
            "current_tab_name": "HDR",
            "user_function_name": "OSOBJA", 
            "lov_tag_name": "costcode",
            "flcust": "", # Example of specific param for cost codes
            "fleetcustorg": "" # Example of specific param for cost codes
        } 
    }
    """
    # Determine if config is a ConfigManager-like object or a dict
    if hasattr(config, 'get_value') and callable(getattr(config, 'get_value')):
        base_url = config.get_value("EAM_BASE_URL")
        eamid = config.get_value("EAM_ID")
        tenant = config.get_value("TENANT_ID")
    elif isinstance(config, dict):
        base_url = config.get("EAM_BASE_URL")
        eamid = config.get("EAM_ID")
        tenant = config.get("TENANT_ID")
    else:
        print("Error: Invalid configuration object provided.")
        return None

    if not all([base_url, eamid, tenant]):
        print("Error: EAM configuration (EAM_BASE_URL, EAM_ID, TENANT_ID) is missing or incomplete.")
        return None

    fetcher = EAMLOVFetcher(base_url=base_url, eamid=eamid, tenant=tenant)
    all_data = {}

    if "categories" in params_map:
        cat_params = params_map["categories"]
        all_data["categories"] = fetcher.fetch_category_values(
            cat_params.get("organization"),
            cat_params.get("class_code"),
            cat_params.get("class_organization")
        )
    
    if "cost_codes" in params_map:
        cc_params = params_map["cost_codes"]
        # Pass all parameters from cc_params to fetch_cost_code_values
        # The method will pick the ones it knows (organization, usage_type, etc.)
        # and use **kwargs for others (like flcust, fleetcustorg, or direct LOV_ALIAS_... )
        all_data["cost_codes"] = fetcher.fetch_cost_code_values(**cc_params)
            
    return all_data

# Example of how to use this module:
if __name__ == '__main__':
    print("Running EAMLOVFetcher example...")
    
    # This is a mock ConfigManager for demonstration.
    # In your actual application, ConfigManager would load from a file or environment.
    class MockConfigManager:
        def __init__(self, config_dict):
            self.config = config_dict
        def get_value(self, key):
            return self.config.get(key)

    # IMPORTANT: Replace placeholder values with your actual EAM details
    # The EAM_BASE_URL should point to the directory containing GRIDDATA, LOVPOP etc.
    # e.g. if full URL is https://us1.eam.hxgnsmartcloud.com/web/base/GRIDDATA
    # then EAM_BASE_URL is https://us1.eam.hxgnsmartcloud.com/web/base
    mock_config_values = {
        "EAM_BASE_URL": "https://us1.eam.hxgnsmartcloud.com/web/base", # Replace if different
        "EAM_ID": "YOUR_EAM_ID_HERE",  # Replace with your actual EAM ID
        "TENANT_ID": "YOUR_TENANT_ID_HERE" # Replace with your actual Tenant ID
    }
    cfg = MockConfigManager(mock_config_values)

    # Check if placeholder values are still present
    if "YOUR_EAM_ID_HERE" in cfg.get_value("EAM_ID") or \
       "YOUR_TENANT_ID_HERE" in cfg.get_value("TENANT_ID"):
        print("\nWARNING: Please replace placeholder EAM_ID and TENANT_ID in the script to run the example.")
        print("Skipping API calls due to placeholder configuration.")
    else:
        # Parameters for fetching categories
        category_params_to_fetch = {
            "organization": "*", 
            "class_code": "TIRE", 
            "class_organization": "*"
        }
        
        # Parameters for fetching cost codes (example)
        cost_code_params_to_fetch = {
            "organization": "*", 
            "usage_type": "lov", 
            "current_tab_name": "HDR",
            "user_function_name": "OSOBJA", 
            "lov_tag_name": "costcode",
            "flcust": "", # Value for param.flcust
            "fleetcustorg": "" # Value for param.fleetcustorg
            # Alternatively, you could pass LOV_ALIAS directly if preferred by your EAM setup:
            # "LOV_ALIAS_NAME_2": "param.flcust", "LOV_ALIAS_VALUE_2": "", "LOV_ALIAS_TYPE_2": "text",
        }

        # Define what data you want to fetch
        lov_params_to_fetch_map = {
            "categories": category_params_to_fetch,
            "cost_codes": cost_code_params_to_fetch 
        }

        fetched_data_dictionary = get_all_lov_data(cfg, lov_params_to_fetch_map)
        
        if fetched_data_dictionary is not None:
            print("\nFetched data dictionary:")
            print(json.dumps(fetched_data_dictionary, indent=4))
            
            if "categories" in fetched_data_dictionary and not fetched_data_dictionary.get("categories"):
                print("\nNote: Categories list is empty. This might be due to incorrect parameters, EAM configuration, or no matching data in EAM.")
            if "cost_codes" in fetched_data_dictionary and not fetched_data_dictionary.get("cost_codes"):
                print("\nNote: Cost Codes list is empty. This might be due to incorrect parameters, EAM configuration, or no matching data in EAM.")
        else:
            print("\nFailed to fetch data, likely due to missing EAM configuration or other errors during request.")

        # Example of direct fetcher usage (categories)
        print("\n--- Direct Fetcher Usage Example (Categories) ---")
        direct_fetcher = EAMLOVFetcher(
            base_url=cfg.get_value("EAM_BASE_URL"),
            eamid=cfg.get_value("EAM_ID"),
            tenant=cfg.get_value("TENANT_ID")
        )
        categories_list = direct_fetcher.fetch_category_values(
            organization=category_params_to_fetch["organization"],
            class_code=category_params_to_fetch["class_code"],
            class_organization=category_params_to_fetch["class_organization"]
        )
        if categories_list is not None: 
            print(f"Directly fetched categories list: {categories_list}")
            if not categories_list:
                 print("(Direct fetch returned an empty list for categories)")
        else:
            print("Direct fetch for categories failed (returned None).")

        # Example of direct fetcher usage (cost_codes)
        print("\n--- Direct Fetcher Usage Example (Cost Codes) ---")
        cost_codes_list = direct_fetcher.fetch_cost_code_values(
            organization=cost_code_params_to_fetch["organization"],
            usage_type=cost_code_params_to_fetch["usage_type"],
            current_tab_name=cost_code_params_to_fetch["current_tab_name"],
            user_function_name=cost_code_params_to_fetch["user_function_name"],
            lov_tag_name=cost_code_params_to_fetch["lov_tag_name"],
            flcust=cost_code_params_to_fetch["flcust"],
            fleetcustorg=cost_code_params_to_fetch["fleetcustorg"]
        )
        if cost_codes_list is not None:
            print(f"Directly fetched cost codes list: {cost_codes_list}")
            if not cost_codes_list:
                print("(Direct fetch returned an empty list for cost codes)")
        else:
            print("Direct fetch for cost codes failed (returned None).")
