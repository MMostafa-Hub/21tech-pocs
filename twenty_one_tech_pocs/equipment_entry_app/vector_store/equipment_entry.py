from .elasticsearch_vector_store import ElasticSearchVectorStore


class EquipmentEntryElasticSearch(ElasticSearchVectorStore):
    # Include label mappings
    label_mapping = {
        "equipmentno": "ASSETID.EQUIPMENTCODE",
        "equipmentdesc": "ASSETID.DESCRIPTION",
        "department": "DEPARTMENTID.DEPARTMENTCODE",
        "eqtype": "TYPE.TYPECODE",
        "organization": "ASSETID.ORGANIZATIONID.ORGANIZATIONCODE",
        "assetstatus": "STATUS.STATUSCODE",
        "operationalstatus": "OPERATIONALSTATUS",
        "loanedtodepartment": "LOANEDTODEPARTMENTID",
        "pmwodepartment": "PMWODEPARTMENTID",
        "category": "CATEGORYID.CATEGORYCODE",
        "class": "CLASSID.CLASSCODE",
        "costcode": "COSTCODEID",
        "production": "INPRODUCTION",
        "safety": "SAFETY",
        "profile": "PROFILEID",
        "outofservice": "OUTOFSERVICE",
        "preventwocompletion": "PREVENTWOCOMPLETION",
        "commissiondate": "COMMISSIONDATE",
        "transferdate": "TRANSFERDATE",
        "withdrawaldate": "WITHDRAWALDATE",
        "equipmentvalue": "ASSETVALUE",
        "assignedto": "ASSIGNEDTO",
        "meterunit": "METERUNIT",
        "criticality": "CRITICALITYID",
        "state": "EQUIPMENTSTATEID",
        "cnnumber": "CNID",
        "cgmp": "CGMP",
        "trackresource": "RESOURCEENABLED",
        "inventoryverificationdate": "INVENTORYVERIFICATIONDATE",
        "lotodatereviewrequired": "LOTODATEREVIEWREQUIRED",
        "lotoreviewedby": "LOTOREVIEWEDBY",
        "originalreceiptdate": "ORIGINALRECEIPTDATE",
        "latestreceiptdate": "LATESTRECEIPTDATE",
        "originalinstalldate": "ORIGINALINSTALLDATE",
        "latestinstalldate": "LATESTINSTALLDATE",
        "documotobookid": "DOCUMOTOBOOKID",
        "imageurl": "URL",
        "consist": "CONSISTID",
        "consistposition": "CONSISTPOSITION",
        "temperaturemonitored": "TEMPMONITORED",
        "driver": "DRIVER",
        "phonenumber": "PHONENUMBER",
        "accessible": "ACCESSIBLE",
        "nonsmoking": "NONSMOKING",
        "pidno": "PIDNUMBER",
        "piddrawing": "PIDDRAWING",
        "hardwareversion": "HARDWAREVER",
        "softwareversion": "SOFTWAREVER",
        "purchasingassetid": "PURCHASINGASSET",
        "biomedicalassetid": "BIOMEDICALASSET",
        "umdnscode": "UMDNS",
        "oemsitesystemid": "OEMSITE",
        "vendor": "VENDOR",
        "coveragetype": "COVERAGETYPE",
        "lockouttagout": "LOCKOUT",
        "personalprotectiveequipment": "PERSONALPROTECTIVEEQUIP",
        "confinedspace": "CONFINEDSPACE",
        "statementofconditions": "STATEMENTOFCOND",
        "buildingmaintenanceprogram": "BUILDMAINTPROGRAM",
        "hipaaconfidentiality": "HIPAACONFIDENTIALITY",
        "disposaltype": "DISPOSALTYPE",
        "checklistfilter": "CHECKLISTFILTER",
        "sizefortolerance": "TOLERANCESIZE",
        "primaryfuel": "FUELID",
        "profilepicture": "PROFILEPICTURE",
        "purchaseorder": "PURCHASEORDERCODE",
        "purchasedate": "PURCHASEDATE",
        "purchasecost": "PURCHASECOST",
        "vehicle": "FleetVehicleInfo",
        "vehiclestatus": "VEHICLESTATUS",
        "vehicletype": "VEHICLETYPE",
        "reservationcalendarownerslist": "RESERVATIONCALENDAROWNERSLIST",
        "reservationcalendarowner": "RESERVATIONCALENDAROWNER",
        "rentalequipment": "RENTALEQUIPMENT",
        "contractequipment": "CONTRACTEQUIPMENT",
        "customer": "CUSTOMER",
        "availabilitystatus": "AVAILABILITYSTATUS",
        "issuedto": "ISSUEDTO",
        "calendargroup": "CALENDARGROUP",
        "minimumpenalty": "MINIMUMPENALTY",
        "penaltyfactor": "PENALTYFACTOR",
        "sdmflag": "SDMFLAG",
        "vmrsdesc": "VMRSCODE",
        "currentworkspace": "WORKSPACEID",
        "componentlocation": "PARTLOCATIONCODE",
        "alias": "EQUIPMENTALIAS",
        "safetydatereviewrequired": "SAFETYDATEREVIEWREQUIRED",
        "safetyreviewedby": "SAFETYREVIEWEDBY",
        "permitdatereviewrequired": "PERMITDATEREVIEWREQUIRED",
        "permitreviewedby": "PERMITREVIEWEDBY",
        "equipmentconfiguration": "EQUIPMENTCONFIGURATIONID",
        "setcode": "SETID",
        "setposition": "SETPOSITION",
        "xcoordinate": "XLOCATION",
        "ylocation": "YLOCATION",
        "rcmlevel": "RCMLEVELID",
        "riskprioritynumber": "RISKPRIORITYNUMBER",
        "facilityconditionindex": "FacilityConditionIndex",
        "conditionindex": "CONDITIONINDEX",
        "conditionscore": "CONDITIONSCORE"
    }

    # Add field descriptions
    field_descriptions = {
        "equipmentno": "Unique identifier for the equipment/asset.",
        "equipmentdesc": "A brief description of the equipment.",
        "department": "The department responsible for the equipment.",
        "eqtype": "The type or category of the equipment.",
        "organization": "The organization the equipment belongs to.",
        "assetstatus": "The current status of the asset (e.g., Active, Inactive).",
        "operationalstatus": "The operational status (e.g., Operating, Down).",
        "loanedtodepartment": "Department the equipment is currently loaned to.",
        "pmwodepartment": "Department responsible for preventive maintenance work orders.",
        "category": "A broader classification category for the equipment.",
        "class": "A specific class within the category.",
        "costcode": "Associated cost code for financial tracking.",
        "production": "Indicates if the equipment is used in production.",
        "safety": "Indicates if the equipment has specific safety considerations.",
        "profile": "Associated profile ID.",
        "outofservice": "Indicates if the equipment is currently out of service.",
        "preventwocompletion": "Flag to prevent work order completion.",
        "commissiondate": "Date the equipment was commissioned.",
        "transferdate": "Date the equipment was transferred.",
        "withdrawaldate": "Date the equipment was withdrawn from service.",
        "equipmentvalue": "The monetary value of the equipment.",
        "assignedto": "Person or entity the equipment is assigned to.",
        "meterunit": "Unit of measurement for the equipment's meter.",
        "criticality": "Criticality level of the equipment.",
        "state": "Current state or condition of the equipment.",
        "cnnumber": "Associated CN (Change Notice) number.",
        "cgmp": "Indicates compliance with Current Good Manufacturing Practices.",
        "trackresource": "Flag indicating if the equipment is tracked as a resource.",
        "inventoryverificationdate": "Date of the last inventory verification.",
        "lotodatereviewrequired": "Indicates if Lockout/Tagout date review is required.",
        "lotoreviewedby": "Person who reviewed the Lockout/Tagout procedures.",
        "originalreceiptdate": "Date the equipment was originally received.",
        "latestreceiptdate": "Date the equipment was most recently received.",
        "originalinstalldate": "Date the equipment was originally installed.",
        "latestinstalldate": "Date the equipment was most recently installed.",
        "documotobookid": "Associated Documoto book ID.",
        "imageurl": "URL of an image of the equipment.",
        "consist": "Consist ID if part of a larger assembly.",
        "consistposition": "Position within the consist.",
        "temperaturemonitored": "Indicates if temperature is monitored for this equipment.",
        "driver": "Assigned driver (if applicable, e.g., vehicles).",
        "phonenumber": "Associated phone number.",
        "accessible": "Indicates if the equipment is accessible.",
        "nonsmoking": "Indicates if it's a non-smoking asset (e.g., vehicle, room).",
        "pidno": "Piping and Instrumentation Diagram (P&ID) number.",
        "piddrawing": "P&ID drawing reference.",
        "hardwareversion": "Hardware version of the equipment.",
        "softwareversion": "Software version installed on the equipment.",
        "purchasingassetid": "Identifier used in the purchasing system.",
        "biomedicalassetid": "Identifier used for biomedical assets.",
        "umdnscode": "Universal Medical Device Nomenclature System code.",
        "oemsitesystemid": "OEM site system identifier.",
        "vendor": "The vendor or supplier of the equipment.",
        "coveragetype": "Type of warranty or service coverage.",
        "lockouttagout": "Indicates if Lockout/Tagout procedures apply.",
        "personalprotectiveequipment": "Required Personal Protective Equipment (PPE).",
        "confinedspace": "Indicates if it involves a confined space.",
        "statementofconditions": "Reference to the Statement of Conditions.",
        "buildingmaintenanceprogram": "Indicates inclusion in the building maintenance program.",
        "hipaaconfidentiality": "Indicates HIPAA confidentiality requirements.",
        "disposaltype": "Method or type of disposal.",
        "checklistfilter": "Filter criteria for associated checklists.",
        "sizefortolerance": "Size specification for tolerance checks.",
        "primaryfuel": "Primary fuel type used by the equipment.",
        "profilepicture": "Profile picture associated with the asset.",
        "purchaseorder": "Purchase order number used to acquire the equipment.",
        "purchasedate": "Date the equipment was purchased.",
        "purchasecost": "Original purchase cost of the equipment.",
        "vehicle": "Information specific to fleet vehicles.",
        "vehiclestatus": "Current status of the vehicle.",
        "vehicletype": "Type of vehicle.",
        "reservationcalendarownerslist": "List of owners for the reservation calendar.",
        "reservationcalendarowner": "Primary owner of the reservation calendar.",
        "rentalequipment": "Indicates if the equipment is for rental.",
        "contractequipment": "Indicates if the equipment is under contract.",
        "customer": "Associated customer.",
        "availabilitystatus": "Current availability status.",
        "issuedto": "Person or entity the equipment is currently issued to.",
        "calendargroup": "Group for scheduling or calendar purposes.",
        "minimumpenalty": "Minimum penalty associated with the equipment (if applicable).",
        "penaltyfactor": "Factor used to calculate penalties.",
        "sdmflag": "Service Delivery Management flag.",
        "vmrsdesc": "Vehicle Maintenance Reporting Standards code description.",
        "currentworkspace": "The current workspace or location identifier.",
        "componentlocation": "Location code of the component part.",
        "alias": "An alternative name or alias for the equipment.",
        "safetydatereviewrequired": "Indicates if safety date review is required.",
        "safetyreviewedby": "Person who reviewed the safety procedures.",
        "permitdatereviewrequired": "Indicates if permit date review is required.",
        "permitreviewedby": "Person who reviewed the permits.",
        "equipmentconfiguration": "Identifier for the equipment's configuration.",
        "setcode": "Code identifying the set the equipment belongs to.",
        "setposition": "Position within the set.",
        "xcoordinate": "X-coordinate for location mapping.",
        "ylocation": "Y-coordinate for location mapping.",
        "rcmlevel": "Reliability Centered Maintenance (RCM) level ID.",
        "riskprioritynumber": "Calculated Risk Priority Number (RPN).",
        "facilityconditionindex": "Index representing the facility's condition.",
        "conditionindex": "General condition index score.",
        "conditionscore": "Numerical score representing the equipment's condition."
    }

    def __init__(self, es_host: str = "http://localhost:9201", index_name: str = "assets_index"):
        super().__init__(es_host, index_name)

    def fuzzy_search(self, user_input: str, label_key: str):
        # Get the Elasticsearch attribute for the provided label key
        attribute = self.label_mapping.get(label_key)
        if attribute is None:
            print(f"Warning: Invalid label_key '{label_key}' provided.")
            return []

        # Split the user input into terms
        search_terms = user_input.split()
        if not search_terms:
            return []

        # Build the boolean query with should clauses for each term
        should_clauses = []
        for term in search_terms:
            should_clauses.append({
                "match": {
                    "ASSETID.EQUIPMENTCODE": {  # Use the mapped attribute here
                        "query": term,
                        "fuzziness": "AUTO",
                        "operator": "and"  # Keep operator 'and' if needed per term, or remove/change if not
                    }
                }
            })

        query = {
            "query": {
                "bool": {
                    "should": should_clauses,
                    "minimum_should_match": 1  # Match documents containing at least one term
                }
            },
            "_source": [attribute]  # Request only the target attribute
        }

        print(f"Executing ES Query: {query}")  # Optional: for debugging
        response = self.search(query)

        # Use a set to store unique results
        unique_results = set()

        if response and "hits" in response and "hits" in response["hits"]:
            for hit in response["hits"]["hits"]:
                source = hit.get("_source", {})
                # Navigate nested structure if attribute contains dots
                attr_parts = attribute.split('.')
                value = source
                try:
                    for part in attr_parts:
                        if isinstance(value, dict) and part in value:
                            value = value[part]
                        else:
                            value = None  # Attribute path not found in this hit
                            break
                    if value is not None:
                        # Add the found value to the set
                        unique_results.add(value)
                except Exception as e:
                    # Log errors during processing
                    print(f"Error processing hit: {hit}, Error: {e}")

        # Convert the set back to a list before returning
        return list(unique_results)
