import base64
import json
import logging
import requests
from datetime import datetime
from typing import Optional # Added for type hinting

logger = logging.getLogger(__name__)


class EAMApiService:
    """Service for communicating with the EAM API."""

    def __init__(self):
        self.base_url = "https://us1.eam.hxgnsmartcloud.com:443/axis/restservices"
        self.username = "MOHAMED.MOSTAFA@21TECH.COM"
        self.password = "Password0!"
        self.headers = {
            'Content-Type': 'application/json',
            'tenant': 'TWENTY1TECH_TST',
            'organization': '21T' # Organization can be specified per request or globally if always the same
        }
        self.hazard_type_to_eam_map = {
            "All Hazards": "GEN",
            "Biological Hazards": "BI",
            "Chemical Hazards": "CH",
            "Physical Hazards": "PH",
            "Radiological Hazards": "RA",
        }

    def _get_auth(self):
        """Get the basic authentication header value."""
        auth_str = f"{self.username}:{self.password}"
        auth_bytes = auth_str.encode('ascii')
        return f"Basic {base64.b64encode(auth_bytes).decode('ascii')}"

    def create_task_plan(self, task_plan):
        """Create a task plan in the EAM system."""
        url = f"{self.base_url}/tasks"

        headers = self.headers.copy()
        headers["Authorization"] = self._get_auth()
        headers["organization"] = "LAMETRO" # Example specific org for this call

        payload = self._transform_task_plan(task_plan)

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating task plan: {str(e)}")
            logger.error(f"Payload: {json.dumps(payload, indent=2)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            raise ValueError(f"Failed to create task plan: {str(e)}")

    def create_checklist(self, task_code, checklist_item, sequence=10):
        """Create a checklist item for a task plan in the EAM system."""
        url = f"{self.base_url}/tasks/checklists/"

        headers = self.headers.copy()
        headers["Authorization"] = self._get_auth()
        headers["organization"] = "LAMETRO"

        payload = self._transform_checklist(
            task_code, checklist_item, sequence)

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating checklist: {str(e)}")
            logger.error(f"Payload: {json.dumps(payload, indent=2)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            raise ValueError(f"Failed to create checklist: {str(e)}")

    def create_maintenance_schedule(self, maintenance_schedule):
        """Create a maintenance schedule in the EAM system."""
        url = f"{self.base_url}/pmschedulesforwork"

        headers = self.headers.copy()
        headers["Authorization"] = self._get_auth()
        headers["organization"] = "LAMETRO" 

        payload = self._transform_maintenance_schedule(maintenance_schedule)

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating maintenance schedule: {str(e)}")
            logger.error(f"Payload: {json.dumps(payload, indent=2)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            raise ValueError(
                f"Failed to create maintenance schedule: {str(e)}")

    def _transform_task_plan(self, task_plan):
        """Transform a task plan model to the API payload format."""
        current_date = datetime.now()
        # Assuming task_plan has task_code and description attributes
        return {
            "TASKLISTID": {
                "TASKCODE": task_plan.task_code,
                "TASKREVISION": 0,
                "ORGANIZATIONID": {"ORGANIZATIONCODE": "LAMETRO"},
                "DESCRIPTION": task_plan.description
            },
            "STATUS": {"STATUSCODE": "A"},
            "REVISIONCONTROL": {
                "REVISIONCONTROLID": {
                    "RCENTITYCODEID": {
                        "RCENTITYCODE": task_plan.task_code,
                        "REVISION": 0,
                    }
                },
                "REQUESTBY": {"USERCODE": self.username},
                "DATEREQUESTED": {
                    "YEAR": current_date.year,
                    "MONTH": current_date.month, # API might use 1-indexed, adjust if 0-indexed like example showed
                    "DAY": current_date.day,
                    # Time components might be optional or needed as 0 if not specific
                    "qualifier": "OTHER" # Default qualifier
                }
            },
            "OUTOFSERVICE": "false",
            "ACTIVECHECKLIST": "true",
            "WODESCRIPTION": task_plan.description,
            "WOTYPE": {"TYPECODE": "PMC"},
            # Other fields as per your previous example, ensuring they are valid for your EAM
        }

    def _transform_checklist(self, task_code, checklist_item, sequence):
        """Transform a checklist item model to the API payload format."""
        # Assuming checklist_item has description attribute
        return {
            "TASKLISTID": {
                "TASKCODE": task_code,
                "TASKREVISION": 0,
                "ORGANIZATIONID": {"ORGANIZATIONCODE": "LAMETRO"},
            },
            "CHECKLISTID": {"DESCRIPTION": checklist_item.description},
            "SEQUENCE": sequence,
            "TYPE": {"TYPECODE": "01"},
            "REQUIREDTOCLOSEDOC": {"USERDEFINEDCODE": "NO"},
            "EQUIPMENTLEVEL": {"USERDEFINEDCODE": "HDR"}
        }

    def _transform_maintenance_schedule(self, maintenance_schedule):
        """Transform a maintenance schedule model to the API payload format."""
        # Assuming maintenance_schedule has code, description, duration attributes
        return {
            "PPMID": {
                "PPMCODE": maintenance_schedule.code,
                "PPMREVISION": 0,
                "ORGANIZATIONID": {"ORGANIZATIONCODE": "LAMETRO"},
                "DESCRIPTION": maintenance_schedule.description
            },
            "PMSCHEDULETYPE": "F",
            "WORKORDERTYPE": {"TYPECODE": "PM"},
            "REVISIONSTATUS": {"STATUSCODE": "A"},
            "PMDURATION": maintenance_schedule.duration
        }

    # --- Methods for Safety Procedure Assistant --- 
    def create_hazard(self, hazard_data: dict, organization_code: str = "*", max_retries: int = 5):
        """Create a hazard in the EAM system using the new payload structure.
        If a record already exists, increment the revision number and retry.
        """
        url = f"{self.base_url}/hazard" 
        headers = self.headers.copy()
        headers["Authorization"] = self._get_auth()
        headers["organization"] = organization_code
        
        eam_hazard_type = self.hazard_type_to_eam_map.get(hazard_data.get("hazard_type"), "PH") # Default to PH if not mapped or GEN if preferred

        # Start with revision 0 and increment if needed
        for revision in range(max_retries):
            payload = {
                "HAZARDID": {
                    "HAZARDCODE": hazard_data.get("hazard_code"),
                    "REVISIONNUM": {"VALUE": revision, "NUMOFDEC": 0, "SIGN": "+", "UOM": "default", "qualifier": "OTHER"},
                    "ORGANIZATIONID": {"ORGANIZATIONCODE": organization_code},
                    "DESCRIPTION": hazard_data.get("description")
                },
                "STATUS": {"STATUSCODE": "U"}, 
                "TYPE": {"TYPECODE": eam_hazard_type},
                "CREATEDBY": {"USERCODE": self.username},
                "recordid": revision
            }
            
            logger.info(f"Attempting to create hazard: {hazard_data.get('hazard_code')} with revision {revision}")
            try:
                response = requests.post(url, json=payload, headers=headers)
                response.raise_for_status()
                logger.info(f"Hazard {hazard_data.get('hazard_code')} created successfully with revision {revision}: {response.json()}")
                result = response.json()
                result["revision_used"] = revision  # Add the revision that was successfully used
                return result
            except requests.exceptions.RequestException as e:
                response_text = e.response.text if hasattr(e, 'response') and e.response is not None else "No response text"
                
                # Check if it's an "already exists" error
                if hasattr(e, 'response') and e.response is not None:
                    try:
                        error_data = e.response.json()
                        error_alerts = error_data.get("ErrorAlert", [])
                        already_exists = any(
                            "already exists" in alert.get("Message", "").lower() 
                            for alert in error_alerts
                        )
                        
                        if already_exists and revision < max_retries - 1:
                            logger.warning(f"Hazard {hazard_data.get('hazard_code')} with revision {revision} already exists. Trying revision {revision + 1}")
                            continue  # Try next revision
                    except (json.JSONDecodeError, AttributeError):
                        pass  # If we can't parse the response, treat as regular error
                
                # If it's not an "already exists" error or we've exhausted retries
                logger.error(f"Error creating hazard {hazard_data.get('hazard_code')} with revision {revision}: {str(e)}")
                logger.error(f"Response content: {response_text}")
                return {
                    "error": str(e), 
                    "status": "failed", 
                    "hazard_code": hazard_data.get("hazard_code"), 
                    "final_revision_attempted": revision,
                    "payload_sent": payload, 
                    "response_text": response_text
                }
        
        # If we get here, all retries failed
        return {
            "error": f"Failed to create hazard after {max_retries} revision attempts", 
            "status": "failed", 
            "hazard_code": hazard_data.get("hazard_code"),
            "max_retries_reached": True
        }

    def create_precaution(self, precaution_data: dict, organization_code: str = "*", max_retries: int = 5):
        """Create a precaution in the EAM system using the new payload structure.
        If a record already exists, increment the revision number and retry.
        """
        url = f"{self.base_url}/precaution" 
        headers = self.headers.copy()
        headers["Authorization"] = self._get_auth()
        headers["organization"] = organization_code

        # Start with revision 0 and increment if needed
        for revision in range(max_retries):
            payload = {
                "PRECAUTIONID": {
                    "PRECAUTIONCODE": precaution_data.get("precaution_code"),
                    "REVISIONNUM": {"VALUE": revision, "NUMOFDEC": 0, "SIGN": "+", "UOM": "default", "qualifier": "OTHER"},
                    "ORGANIZATIONID": {"ORGANIZATIONCODE": organization_code},
                    "DESCRIPTION": precaution_data.get("description")
                },
                "STATUS": {"STATUSCODE": "U"}, 
                "recordid": revision
            }
            
            logger.info(f"Attempting to create precaution {precaution_data.get('precaution_code')} with revision {revision}")
            try:
                response = requests.post(url, json=payload, headers=headers)
                response.raise_for_status()
                logger.info(f"Precaution {precaution_data.get('precaution_code')} created successfully with revision {revision}: {response.json()}")
                result = response.json()
                result["revision_used"] = revision  # Add the revision that was successfully used
                return result
            except requests.exceptions.RequestException as e:
                response_text = e.response.text if hasattr(e, 'response') and e.response is not None else "No response text"
                
                # Check if it's an "already exists" error
                if hasattr(e, 'response') and e.response is not None:
                    try:
                        error_data = e.response.json()
                        error_alerts = error_data.get("ErrorAlert", [])
                        already_exists = any(
                            "already exists" in alert.get("Message", "").lower() 
                            for alert in error_alerts
                        )
                        
                        if already_exists and revision < max_retries - 1:
                            logger.warning(f"Precaution {precaution_data.get('precaution_code')} with revision {revision} already exists. Trying revision {revision + 1}")
                            continue  # Try next revision
                    except (json.JSONDecodeError, AttributeError):
                        pass  # If we can't parse the response, treat as regular error
                
                # If it's not an "already exists" error or we've exhausted retries
                logger.error(f"Error creating precaution {precaution_data.get('precaution_code')} with revision {revision}: {str(e)}")
                logger.error(f"Response content: {response_text}")
                return {
                    "error": str(e), 
                    "status": "failed", 
                    "precaution_code": precaution_data.get("precaution_code"), 
                    "final_revision_attempted": revision,
                    "payload_sent": payload, 
                    "response_text": response_text
                }
        
        # If we get here, all retries failed
        return {
            "error": f"Failed to create precaution after {max_retries} revision attempts", 
            "status": "failed", 
            "precaution_code": precaution_data.get("precaution_code"),
            "max_retries_reached": True
        }

    def create_safety_link_record(self, 
                                  eam_hazard_code: str, hazard_eam_type_code: str,
                                  eam_precaution_code: str,
                                  equipment_details: Optional[dict] = None, 
                                  organization_code: str = "*",
                                  hazard_revision: int = 0, 
                                  precaution_revision: int = 0,
                                  hazard_description: str = "",
                                  precaution_description: str = ""
                                  ):
        """Creates a safety matrix link record in EAM (SafetyMatrix entity).
        First approves the hazard and precaution, then creates the safety matrix link.
        """
        
        # Step 1: Update hazard status to RA
        logger.info(f"Step 1: Updating hazard {eam_hazard_code} (revision {hazard_revision}) status to RA")
        hazard_ra_result = self.update_hazard_status(eam_hazard_code, "RA", organization_code, hazard_revision)
        if "error" in hazard_ra_result:
            logger.error(f"Failed to update hazard {eam_hazard_code} to RA status. Cannot proceed with safety matrix creation.")
            return {"error": "Hazard RA status update failed", "hazard_ra_result": hazard_ra_result}
        
        # Step 2: Update hazard status to A
        logger.info(f"Step 2: Updating hazard {eam_hazard_code} (revision {hazard_revision}) status to A")
        hazard_approval_result = self.update_hazard_status(eam_hazard_code, "A", organization_code, hazard_revision)
        if "error" in hazard_approval_result:
            logger.error(f"Failed to approve hazard {eam_hazard_code}. Cannot proceed with safety matrix creation.")
            return {"error": "Hazard approval failed", "hazard_approval_result": hazard_approval_result}
        
        # Step 3: Update precaution status to RA
        logger.info(f"Step 3: Updating precaution {eam_precaution_code} (revision {precaution_revision}) status to RA")
        precaution_ra_result = self.update_precaution_status(eam_precaution_code, "RA", organization_code, precaution_revision)
        if "error" in precaution_ra_result:
            logger.error(f"Failed to update precaution {eam_precaution_code} to RA status. Cannot proceed with safety matrix creation.")
            return {"error": "Precaution RA status update failed", "precaution_ra_result": precaution_ra_result}
        
        # Step 4: Update precaution status to A
        logger.info(f"Step 4: Updating precaution {eam_precaution_code} (revision {precaution_revision}) status to A")
        precaution_approval_result = self.update_precaution_status(eam_precaution_code, "A", organization_code, precaution_revision)
        if "error" in precaution_approval_result:
            logger.error(f"Failed to approve precaution {eam_precaution_code}. Cannot proceed with safety matrix creation.")
            return {"error": "Precaution approval failed", "precaution_approval_result": precaution_approval_result}
        
        # Step 5: Create the safety matrix link
        logger.info(f"Step 5: Creating safety matrix link for approved hazard {eam_hazard_code} and precaution {eam_precaution_code}")
        url = f"{self.base_url}/safetymatrix" 
        headers = self.headers.copy()
        headers["Authorization"] = self._get_auth()
        headers["organization"] = organization_code

        payload = {
            "SAFETYMATRIXID": {
                "SAFETYMATRIXPK": None, 
                "ORGANIZATIONID": {"ORGANIZATIONCODE": organization_code}
            },
            "SAFETYHAZARDID": {
                "HAZARDCODE": eam_hazard_code,
                "ORGANIZATIONID": {"ORGANIZATIONCODE": organization_code},
                "REVISIONNUM": {"VALUE": hazard_revision, "NUMOFDEC": 0, "SIGN": "+", "UOM": "default", "qualifier": "OTHER"},
                "DESCRIPTION": hazard_description
            },
            "HAZARDTYPE": {"TYPECODE": hazard_eam_type_code},
            "SAFETYPRECAUTIONID": {
                "PRECAUTIONCODE": eam_precaution_code,
                "ORGANIZATIONID": {"ORGANIZATIONCODE": organization_code},
                "REVISIONNUM": {"VALUE": precaution_revision, "NUMOFDEC": 0, "SIGN": "+", "UOM": "default", "qualifier": "OTHER"},
                "DESCRIPTION": precaution_description
            },
            "SEQUENCENUM": {"VALUE": 20, "NUMOFDEC": 0, "SIGN": "+", "UOM": "default", "qualifier": "OTHER"},
            "STANDARDWO": {
                "STDWOCODE": None,
                "ORGANIZATIONID": {"ORGANIZATIONCODE": None},
                "DESCRIPTION": None
            },
            "TASKLISTID": {
                "TASKCODE": "BOILERINSP01",
                "TASKREVISION": 0,
                "ORGANIZATIONID": {"ORGANIZATIONCODE": "*", "DESCRIPTION": None},
                "DESCRIPTION": None
            },
            "EQUIPMENTCLASSID": {
                "CLASSCODE": equipment_details.get("class_code") if equipment_details and equipment_details.get("class_code") else None,
                "ORGANIZATIONID": {"ORGANIZATIONCODE": "*"},
                "DESCRIPTION": "string"
            },
            "CATEGORYID": {
                "CATEGORYCODE": None,
                "DESCRIPTION": None
            },
            "EQUIPMENTID": {
                "EQUIPMENTCODE": None,
                "ORGANIZATIONID": {"ORGANIZATIONCODE": None},
                "DESCRIPTION": None
            },
            "recordid": 0
        }
        
        logger.info(f"Attempting to create safety link record (safetymatrix) for Hazard: {eam_hazard_code}, Precaution: {eam_precaution_code} with payload: {json.dumps(payload, indent=2)}")
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            logger.info(f"Safety link record created successfully: {response.json()}")
            return {
                "status": "success",
                "safety_matrix_result": response.json(),
                "hazard_ra_result": hazard_ra_result,
                "hazard_approval_result": hazard_approval_result,
                "precaution_ra_result": precaution_ra_result,
                "precaution_approval_result": precaution_approval_result
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating safety link record: {str(e)}")
            response_text = e.response.text if hasattr(e, 'response') and e.response is not None else "No response text"
            logger.error(f"Response content: {response_text}")
            return {
                "error": str(e), 
                "status": "failed", 
                "payload_sent": payload, 
                "response_text": response_text,
                "hazard_ra_result": hazard_ra_result,
                "hazard_approval_result": hazard_approval_result,
                "precaution_ra_result": precaution_ra_result,
                "precaution_approval_result": precaution_approval_result
            }

    def get_equipment_categories(self, organization_code: str = "*"):
        """Get equipment categories from the EAM system."""
        url = f"{self.base_url}/categories"
        headers = self.headers.copy()
        headers["Authorization"] = self._get_auth()
        headers["organization"] = organization_code
        
        logger.info(f"Attempting to retrieve equipment categories from: {url}")
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            categories = []
            result_data = data.get("Result", {}).get("ResultData", {})
            data_records = result_data.get("DATARECORD", [])
            
            for record in data_records:
                category_info = record.get("CATEGORYID", {})
                category_code = category_info.get("CATEGORYCODE")
                category_description = category_info.get("DESCRIPTION")
                
                if category_code:
                    # Include both code and description for better context
                    if category_description:
                        categories.append(f"{category_code} - {category_description}")
                    else:
                        categories.append(category_code)
            
            # Remove duplicates while preserving order
            categories = list(dict.fromkeys(categories))
            logger.info(f"Successfully retrieved {len(categories)} equipment categories")
            return categories
        except requests.exceptions.RequestException as e:
            logger.error(f"Error retrieving equipment categories: {str(e)}")
            response_text = e.response.text if hasattr(e, 'response') and e.response is not None else "No response text"
            logger.error(f"Response content: {response_text}")
            # Return a fallback list if API call fails
            return ["BUS - Bus Equipment", "HVAC - HVAC Systems", "TOOL - Tools", "SAFETY - Safety Equipment"]

    def get_equipment_classes(self, organization_code: str = "*"):
        """Get equipment classes from the EAM system."""
        url = f"{self.base_url}/categories"
        headers = self.headers.copy()
        headers["Authorization"] = self._get_auth()
        headers["organization"] = organization_code
        
        logger.info(f"Attempting to retrieve equipment classes from: {url}")
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            classes = []
            result_data = data.get("Result", {}).get("ResultData", {})
            data_records = result_data.get("DATARECORD", [])
            
            for record in data_records:
                class_info = record.get("CLASSID", {})
                class_code = class_info.get("CLASSCODE")
                class_description = class_info.get("DESCRIPTION")
                
                if class_code:
                    # Include both code and description for better context
                    if class_description:
                        classes.append(f"{class_code} - {class_description}")
                    else:
                        classes.append(class_code)
            
            # Remove duplicates while preserving order
            classes = list(dict.fromkeys(classes))
            logger.info(f"Successfully retrieved {len(classes)} equipment classes")
            return classes
        except requests.exceptions.RequestException as e:
            logger.error(f"Error retrieving equipment classes: {str(e)}")
            response_text = e.response.text if hasattr(e, 'response') and e.response is not None else "No response text"
            logger.error(f"Response content: {response_text}")
            # Return a fallback list if API call fails
            return ["BUS - Bus", "HVAC - HVAC", "TOOL - Tool", "SAFETY - Safety"]

    def extract_class_code(self, class_string: str) -> str:
        """Extract the class code from a formatted class string like 'BUS - Bus Description'."""
        if not class_string:
            return None
        # Split on ' - ' and take the first part (the code)
        return class_string.split(" - ")[0].strip()

    def extract_category_code(self, category_string: str) -> str:
        """Extract the category code from a formatted category string like 'CAT001 - Category Description'."""
        if not category_string:
            return None
        # Split on ' - ' and take the first part (the code)
        return category_string.split(" - ")[0].strip()

    def update_hazard_status(self, hazard_code: str, status_code: str = "A", organization_code: str = "*", revision: int = 0):
        """Update a hazard status. Default status is 'A' (Approved)."""
        # URL encode the hazard identifier: HAZARDCODE#REVISION#ORGANIZATION
        hazard_id = f"{hazard_code}%23{revision}%23{organization_code}"
        url = f"{self.base_url}/hazard/{hazard_id}"
        
        headers = self.headers.copy()
        headers["Authorization"] = self._get_auth()
        headers["organization"] = organization_code
        
        payload = {
            "HAZARDID": {
                "HAZARDCODE": hazard_code,
                "REVISIONNUM": {"VALUE": revision, "NUMOFDEC": 0, "SIGN": "+", "UOM": "default", "qualifier": "OTHER"},
                "ORGANIZATIONID": {"ORGANIZATIONCODE": organization_code}
            },
            "STATUS": {
                "STATUSCODE": status_code
            }
        }
        
        logger.info(f"Attempting to update hazard {hazard_code} (revision {revision}) status to {status_code} with payload: {json.dumps(payload, indent=2)}")
        try:
            response = requests.patch(url, json=payload, headers=headers)
            response.raise_for_status()
            logger.info(f"Hazard {hazard_code} status updated to {status_code} successfully: {response.json()}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error updating hazard {hazard_code} status to {status_code}: {str(e)}")
            response_text = e.response.text if hasattr(e, 'response') and e.response is not None else "No response text"
            logger.error(f"Response content: {response_text}")
            return {"error": str(e), "status": "failed", "hazard_code": hazard_code, "status_code": status_code, "payload_sent": payload, "response_text": response_text}

    def update_precaution_status(self, precaution_code: str, status_code: str = "A", organization_code: str = "*", revision: int = 0):
        """Update a precaution status. Default status is 'A' (Approved)."""
        # URL encode the precaution identifier: PRECAUTIONCODE#REVISION#ORGANIZATION
        precaution_id = f"{precaution_code}%23{revision}%23{organization_code}"
        url = f"{self.base_url}/precaution/{precaution_id}"
        
        headers = self.headers.copy()
        headers["Authorization"] = self._get_auth()
        headers["organization"] = organization_code
        
        payload = {
            "PRECAUTIONID": {
                "PRECAUTIONCODE": precaution_code,
                "REVISIONNUM": {"VALUE": revision, "NUMOFDEC": 0, "SIGN": "+", "UOM": "default", "qualifier": "OTHER"},
                "ORGANIZATIONID": {"ORGANIZATIONCODE": organization_code}
            },
            "STATUS": {
                "STATUSCODE": status_code
            }
        }
        
        logger.info(f"Attempting to update precaution {precaution_code} (revision {revision}) status to {status_code} with payload: {json.dumps(payload, indent=2)}")
        try:
            response = requests.patch(url, json=payload, headers=headers)
            response.raise_for_status()
            logger.info(f"Precaution {precaution_code} status updated to {status_code} successfully: {response.json()}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error updating precaution {precaution_code} status to {status_code}: {str(e)}")
            response_text = e.response.text if hasattr(e, 'response') and e.response is not None else "No response text"
            logger.error(f"Response content: {response_text}")
            return {"error": str(e), "status": "failed", "precaution_code": precaution_code, "status_code": status_code, "payload_sent": payload, "response_text": response_text}

    def create_qualification(self, qualification_data: dict, organization_code: str = "*", class_code: str = "*"):
        """Create a qualification in the EAM system.
        
        Args:
            qualification_data: Dictionary containing qualification_code and qualification_description
            organization_code: Organization code (default: "*")
            class_code: Class code for the qualification (default: "*")
            
        Returns:
            Dictionary containing the result of the qualification creation
        """
        url = f"{self.base_url}/qualifications"
        headers = self.headers.copy()
        headers["Authorization"] = self._get_auth()
        headers["organization"] = organization_code
        
        qualification_code = qualification_data.get("qualification_code")
        qualification_description = qualification_data.get("qualification_description")
        
        payload = {
            "QUALIFICATIONID": {
                "QUALIFICATIONCODE": qualification_code,
                "ORGANIZATIONID": {
                    "ORGANIZATIONCODE": organization_code,
                },
                "DESCRIPTION": qualification_description
            },
            "CLASSID": {
                "CLASSCODE": class_code,
                "ORGANIZATIONID": {
                    "ORGANIZATIONCODE": organization_code,
                },
            },
            "ACTIVEFLAG": "true",
            "TRAININGRECORD": "false",
        }
        
        logger.info(f"Attempting to create qualification: {qualification_code} with payload: {json.dumps(payload, indent=2)}")
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            logger.info(f"Qualification {qualification_code} created successfully: {result}")
            return {
                "status": "success",
                "qualification_code": qualification_code,
                "eam_response": result
            }
        except requests.exceptions.RequestException as e:
            response_text = e.response.text if hasattr(e, 'response') and e.response is not None else "No response text"
            logger.error(f"Error creating qualification {qualification_code}: {str(e)}")
            logger.error(f"Response content: {response_text}")
            return {
                "status": "failed",
                "error": str(e),
                "qualification_code": qualification_code,
                "payload_sent": payload,
                "response_text": response_text
            }

