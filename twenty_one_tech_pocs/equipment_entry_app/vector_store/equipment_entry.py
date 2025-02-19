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

    def __init__(self, es_host: str = "http://localhost:9201", index_name: str = "assets_index"):
        super().__init__(es_host, index_name)

    def fuzzy_search(self, user_input: str, label_key: str):
        # Get the Elasticsearch attribute for the provided label key
        attribute = self.label_mapping.get(label_key)
        if attribute is None:
            return []

        query = {
            "query": {
                "match": {
                    "ASSETID.EQUIPMENTCODE": {
                        "query": user_input,
                        "fuzziness": "AUTO",  # Adjusts fuzziness based on input length
                        "operator": "and"
                    }
                }
            },
            "_source": [attribute]
        }

        response = self.search(query)
        filtered_response = []
        for hit in response["hits"]["hits"]:
            source = hit["_source"]
            attr_parts = attribute.split('.')
            value = source
            for part in attr_parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    value = None
                    break
            if value is not None:
                filtered_response.append(value)
        return filtered_response
