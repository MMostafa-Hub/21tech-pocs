import base64
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class EAMApiService:
    """Service for communicating with the EAM API."""

    def __init__(self):
        self.base_url = "https://us1.eam.hxgnsmartcloud.com:443/axis/restservices"
        self.username = "MOHAMED.MOSTAFA@21TECH.COM"
        self.password = "Abcd123456!"
        self.headers = {
            'Content-Type': 'application/json',
            'tenant': 'TWENTY1TECH_TST',
            'organization': '21T'
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

        return {
            "TASKLISTID": {
                "TASKCODE": task_plan.task_code,
                "TASKREVISION": 0,
                "ORGANIZATIONID": {
                    "ORGANIZATIONCODE": "LAMETRO",
                    "DESCRIPTION": None
                },
                "DESCRIPTION": task_plan.description
            },
            "STATUS": {
                "STATUSCODE": "A",
                "DESCRIPTION": None
            },
            "REVISIONCONTROL": {
                "REVISIONCONTROLID": {
                    "ENTITY": None,
                    "RCENTITYCODEID": {
                        "RCENTITYCODE": task_plan.task_code,
                        "REVISION": 0,
                        "ORGANIZATIONID": None,
                        "DESCRIPTION": None
                    }
                },
                "REQUESTBY": {
                    "USERCODE": self.username,
                    "DESCRIPTION": None
                },
                "DATEREQUESTED": {
                    "YEAR": int(datetime(current_date.year, 1, 1).timestamp() * 1000),
                    "MONTH": current_date.month - 1,  # API uses 0-indexed months
                    "DAY": current_date.day,
                    "HOUR": 0,
                    "MINUTE": 0,
                    "SECOND": 0,
                    "SUBSECOND": 0,
                    "TIMEZONE": "-0500",
                    "qualifier": "OTHER"
                }
            },
            "OUTOFSERVICE": "false",
            "ACTIVECHECKLIST": "true",
            "ISOLATIONMETHOD": "false",
            "CHECKLISTPERFORMEDBYREQUIRED": "false",
            "CHECKLISTREVIEWEDBYREQUIRED": "false",
            "WODESCRIPTION": task_plan.description,
            "WOTYPE": {
                "TYPECODE": "PMC",
                "DESCRIPTION": None
            },
            "MATERIALLISTID": {
                "MTLCODE": "MHVAC-01",
                "MTLREVISION": None,
                "ORGANIZATIONID": None,
                "DESCRIPTION": None
            },
            "MULTIPLETRADES": "false",
            "ENABLEENHANCEDPLANNING": "true",
            "CASEMANAGEMENTCHECKLIST": "false",
            "DEFAULTTAG": "false",
            "NONCONFORMITYCHECKLIST": "false",
            "DISCONNECTEDCHKLIST": "false",
            "PREVENTPERFORMEDBYSIGNATURE": "false",
            "PREVENTREVIEWEDBYSIGNATURE": "false"
        }

    def _transform_checklist(self, task_code, checklist_item, sequence):
        """Transform a checklist item model to the API payload format."""
        return {
            "TASKLISTID": {
                "TASKCODE": task_code,
                "TASKREVISION": 0,
                "ORGANIZATIONID": {
                    "ORGANIZATIONCODE": "LAMETRO",
                    "DESCRIPTION": None
                },
                "DESCRIPTION": f"Task plan for {task_code}"
            },
            "CHECKLISTID": {
                "CHECKLISTCODE": None,
                "DESCRIPTION": checklist_item.description
            },
            "SEQUENCE": sequence,
            "TYPE": {
                "TYPECODE": "01",
                "DESCRIPTION": None,
                "entity": None
            },
            "REQUIREDTOCLOSEDOC": {
                "ENTITY": None,
                "USERDEFINEDCODE": "NO",
                "DESCRIPTION": None
            },
            "EQUIPMENTLEVEL": {
                "ENTITY": None,
                "USERDEFINEDCODE": "HDR",
                "DESCRIPTION": None
            }
        }

    def _transform_maintenance_schedule(self, maintenance_schedule):
        """Transform a maintenance schedule model to the API payload format."""
        return {
            "PPMID": {
                "PPMCODE": maintenance_schedule.code,
                "PPMREVISION": 0,
                "ORGANIZATIONID": {
                    "ORGANIZATIONCODE": "LAMETRO",
                    "DESCRIPTION": None
                },
                "DESCRIPTION": maintenance_schedule.description
            },
            "PMSCHEDULETYPE": "F",
            "WORKORDERTYPE": {
                "TYPECODE": "PM",
                "DESCRIPTION": None
            },
            "REVISIONSTATUS": {
                "STATUSCODE": "A",
                "DESCRIPTION": None
            },
            "PMDURATION": maintenance_schedule.duration
        }
