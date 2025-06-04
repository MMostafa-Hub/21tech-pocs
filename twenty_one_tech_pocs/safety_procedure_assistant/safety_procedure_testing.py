from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_openai import ChatOpenAI

system_prompt = """
You are an AI expert in workplace safety incident analysis. Your task is to thoroughly analyze an incident report and structure the findings into two main components:
1.  A comprehensive list of all hazards identified or inferred, each with a detailed list of ALL its relevant precautions.
2.  A list of specific links between equipment mentioned in the incident, a KEY precaution related to that equipment and incident, and the hazard this precaution addresses.

Output Requirements:
Generate a single JSON object. This object must have two top-level keys: "identified_hazards" and "equipment_safety_links".

1.  `identified_hazards`: This must be a LIST of Hazard objects.
    -   Each Hazard object must have:
        -   `hazard_code`: A unique, LLM-proposed code (e.g., "HAZ-INC001-BURN").
        -   `description`: Detailed description of the hazard.
        -   `hazard_type`: Must be one of: "Physical Hazards", "Chemical Hazards", "Biological Hazards", "Ergonomic Hazards", "Psychological Hazards".
        -   `precautions`: A LIST of Precaution objects. This list should include ALL precautions relevant to THIS hazard.
            -   Each Precaution object must have:
                -   `precaution_code`: A unique, LLM-proposed code (e.g., "PREC-HAZ001-001").
                -   `description`: Detailed description of the precaution.
                -   `timing` (optional): Must be one of: "Pre Work", "During", "Post Work".

2.  `equipment_safety_links`: This must be a LIST of EquipmentSafetyLink objects.
    -   This list should only be populated if the incident clearly describes specific equipment involved in a safety lapse related to a specific precaution for an identified hazard.
    -   Each EquipmentSafetyLink object must have:
        -   `equipment_details`: An object with:
            -   `equipment_id`: (Mandatory) Specific name/model of the equipment (e.g., "Blowtorch Model X23").
            -   `class_code` (optional): Must be one of: "HWEQ", "HWEQ-001", "HWEQ-002" if specified.
            -   `category` (optional): Must be one of: "Welding Tools", "Welding Equipment" if specified.
        -   `linked_precaution`: A Precaution object. This precaution MUST BE an exact copy of one of the precautions listed under the corresponding hazard in the `identified_hazards` list.
        -   `parent_hazard_code`: The `hazard_code` of the hazard (from the `identified_hazards` list) to which the `linked_precaution` belongs.

Example JSON structure:
{{
    "identified_hazards": [
        {{
            "hazard_code": "HAZ-BTORCH-001",
            "description": "Risk of burn injury from direct flame or heated parts of the blowtorch.",
            "hazard_type": "Physical Hazards",
            "precautions": [
                {{"precaution_code": "PREC-BT001-PPE01", "description": "Wear appropriate heat-resistant gloves and face shield.", "timing": "Pre Work"}},
                {{"precaution_code": "PREC-BT001-AREA02", "description": "Clear work area of flammable materials before starting.", "timing": "Pre Work"}},
                {{"precaution_code": "PREC-BT001-OPER03", "description": "Never leave a lit blowtorch unattended.", "timing": "During"}}
            ]
        }},
        {{
            "hazard_code": "HAZ-GASLEAK-002",
            "description": "Risk of explosion or fire due to gas leak from faulty blowtorch connection.",
            "hazard_type": "Chemical Hazards",
            "precautions": [
                {{"precaution_code": "PREC-GL002-INSP01", "description": "Inspect hose and connections for leaks before each use with soapy water.", "timing": "Pre Work"}},
                {{"precaution_code": "PREC-GL002-SHUTOFF02", "description": "Ensure gas cylinder valve is closed when not in use.", "timing": "Post Work"}}
            ]
        }}
    ],
    "equipment_safety_links": [
        {{
            "equipment_details": {{
                "equipment_id": "SuperFlame Blowtorch SF-5000",
                "class_code": "HWEQ",
                "category": "Welding Tools"
            }},
            "linked_precaution": {{
                "precaution_code": "PREC-BT001-PPE01", 
                "description": "Wear appropriate heat-resistant gloves and face shield.", 
                "timing": "Pre Work"
            }},
            "parent_hazard_code": "HAZ-BTORCH-001",
        }}
    ]
}}

Ensure all codes are unique and descriptive. If no specific equipment links are clear from the report, `equipment_safety_links` can be an empty list. However, `identified_hazards` should always be populated if any hazards can be inferred.
Strictly adhere to this JSON structure. Do not use markdown formatting for the JSON output.
"""

human_prompt = """
Please analyze the following incident report document and extract the structured safety analysis based on the requirements provided.
Incident Report Text:
{text}

Respond with ONLY the JSON object adhering to the schema described in the system prompt.
"""


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

chat_prompt_template = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(system_prompt),
    HumanMessagePromptTemplate.from_template(human_prompt)
])

chain = chat_prompt_template | llm

document_text = """
Safety Incident Report Safety Incident Report

Date of Report: Date of Report: May 23, 2025 Date/Time of Incident: By:By: Mohamed Mostafa, Safety Officer Job Title of Injured Party:

Date/Time of Incident: May 22, 2025 at 2:45 PM Location of Incident:

Reported Location of Incident: Warehouse 4, Section B, XYZ Industrial Park, Cairo, Egypt Reported

Job Title of Injured Party: Forklift Operator Name of Injured Party:

Name of Injured Party: Ahmed Saleh

1. Description of Incident: 1. Description of Incident:

At approximately 2:45 PM on May 22, 2025, Ahmed Saleh, a certified forklift operator, was operating a Toyota 8FGCU25 LPG-powered forklift equipped with a dual- stage mast and side-shift attachment. He was transporting a pallet of metal automotive components (total weight ~500 kg) from Receiving to the Assembly Area.

While turning the corner at Section B in Warehouse 4, Ahmed misjudged the clearance between the turning radius and a shelving rack system (Model: MECO Pallet Rack 42" D x 12\' H). This system was recently restocked with oversized industrial fittings stacked above the recommended shelf limit. The shelving unit had previously been flagged for inspection due to noticeable tilt, which was not addressed.

Upon collision, the left side of the forklift’s overhead guard struck the lower portion of the shelving rack, destabilizing the top two tiers. Several unsecured metal fittings (each ~15 kg) fell from the top shelf. One of these components struck Ahmed\'s left shoulder while he remained seated in the forklift. Due to the impact, the forklift’s emergency brake was engaged automatically.

Co-workers heard the noise and rushed to the site. Ahmed was conscious but reported acute pain and limited arm mobility. Onsite first responders from the safety team used a portable trauma kit to stabilize the injury before emergency medical services arrived.

2. Injuries Sustained: 2. Injuries Sustained:

Suspected fracture and contusion to the left shoulder (humerus/scapula region) Superficial abrasions on left forearm and hand due to sharp contact with falling debris Elevated stress response and minor shock symptoms (dizziness, pale complexion)

Ahmed was transported to Cairo General Hospital where initial imaging (X-ray and CT) confirmed a proximal humeral fracture. He is currently in orthopedic care with a recovery prognosis of 6–8 weeks.

3. Witnesses: 3. Witnesses:

Sara Kamal, Line Supervisor (direct witness from ~5 meters away) Hossam Youssef, Logistics Coordinator (arrived ~30 seconds after incident) Nada El Mahdy, Quality Assurance Intern (reviewed prior shelf inspection log)

4. Immediate Actions Taken: 4. Immediate Actions Taken:

Isolated Section B and halted all forklift traffic pending investigation Deactivated the compromised shelving rack and secured surrounding area with safety barriers Collected initial witness statements and reviewed CCTV footage Checked forklift logbook and verified recent maintenance (last serviced May 10, 2025)

5. Root Cause Analysis: 5. Root Cause Analysis:

The primary cause was an infrastructural failure due to improper pallet rack loading practices and lack of corrective follow-up from a previously logged inspection warning. Secondary causation includes operator misjudgment due to limited visibility and inadequate spatial indicators around corners.

6. Contributing Factors: 6. Contributing Factors:

Absence of high-visibility reflective floor markings and overhead warning signage Missing corner-mounted convex mirrors for blind spot navigation Overloaded shelving units beyond design weight limit (by approx. 15%) Lack of real-time monitoring for rack load compliance

7. Corrective and Preventive Actions (CAPA): 7. Corrective and Preventive Actions (CAPA):

Immediate re-inspection and re-certification of all pallet racks (due by May 31, 2025) Installation of high-visibility corner indicators and convex safety mirrors by June 10, 2025 Procurement of a digital shelf-load monitoring system for all storage units Mandatory forklift spatial awareness retraining program for all drivers (to be completed by June 15, 2025) Revision and strict enforcement of material stacking protocols

8. Pieces of Equipment Involved: 8. Pieces of Equipment Involved:

Toyota Forklift Model 8FGCU25 (Serial #FGCU25123456) MECO Pallet Rack System (12\' high, steel alloy) Palletized load of 500 kg metal fittings (batch #IND-COM-2205) Standard trauma response kit from Safety Locker #2 In-house CCTV System (Camera ID WH4-B07)

9. Attachments: 9. Attachments:

Photographs from incident scene (before and after shelf collapse) Forklift maintenance and usage logs Shelf unit inspection records and deviation logs Ahmed Saleh\'s hospital intake and imaging report

CCTV footage screenshot sequence (pending approval)

10. Follow-Up Required: 10. Follow-Up Required:

Daily updates on Ahmed Saleh’s medical status during recovery period Compliance verification of corrective actions by Safety Committee Full safety briefing session scheduled with warehouse staff for June 5, 2025 Final audit report on incident due by July 5, 2025

Report Prepared By: Mohamed Mostafa Safety Officer XYZ Industrial Services Report Prepared By:

Signature: _______________________ Date: Signature:

Date: May 23, 2025
"""

response = chain.invoke(document_text)
print(response.content)
