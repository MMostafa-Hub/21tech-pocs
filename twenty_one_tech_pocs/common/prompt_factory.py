from langchain.prompts import PromptTemplate


class PromptFactory:
    @staticmethod
    def get_prompt(name: str) -> PromptTemplate:
        # Currently only supporting "asset_entry_prompt"
        if name == "asset_entry_prompt":
            return PromptTemplate(
                input_variables=[
                    "asset_description",
                    "historical_values",
                    "target_field",
                    "field_description",
                    "accepted_values",
                    "expected_values",
                ],
                template="""You are a universal equipment pattern analyzer.
IF a list of Expected Values is provided for {target_field}, your task is to select the MOST LIKELY value from THIS LIST ONLY.
   - Use historical values and accepted field values as context to inform your choice *from the Expected Values list*.
   - If historical patterns suggest a value NOT present in the Expected Values, you MUST disregard that pattern and select a value from the Expected Values list.
   - Your output MUST be one of the values from the Expected Values list. Do NOT attempt to generate a new value based on historical patterns if Expected Values are available.
OTHERWISE (if no Expected Values are provided), generate ONLY the next logical raw value for {target_field} following the exact format and pattern of historical values, considering any already accepted values for other fields.

Pattern Analysis Guidelines (when generating a new value, or selecting from expected values if applicable):
1. Identify value type(s) and pattern (numerical, categorical, codes, mixed)
2. Detect progression rules (incremental, cyclical, status-based, etc.)
3. Maintain exact format (including symbols, units, casing)
4. Continue sequence logic without conversions
5. For mixed formats: Preserve original value types
6. Consider the context provided by already accepted field values.

Output Rules:
- Return ONLY the selected or generated raw value as it would appear in the database.
- If Expected Values were provided, your output MUST be one of those values.
- No explanations, formatting, or additional text.
- Preserve original value style and structure.
- Follow identified sequence logic exactly (especially when generating, or if it helps narrow down choices from expected values).
- If {target_field} is a date field, the output MUST be in the format 'Day Mon DD YYYY HH:MM:SS GMT+ZZZZ (Time Zone Name)', for example: 'Mon Aug 05 2024 00:00:00 GMT+0300 (Eastern European Summer Time)'. Ensure the day of the week is correct for the given date. This applies whether selecting from expected values or generating a new one.

Examples:
Target Field: state
Historical Values: ["Good", "Good", "Defective", "Good"]
Expected Values: ["CN complete", "CN in process", "CN pending", "Defective", "Good"]
Output: Good

Target Field: category_code
Historical Values: ["COMP-01-A", "COMP-01-B", "COMP-02-A"]
Expected Values: ["COMP-02-B", "COMP-03-A", "MISC-01-A"]
Output: COMP-02-B

Target Field: next_inspection_date
Historical Values: ["Mon Jul 01 2024 00:00:00 GMT+0000 (Coordinated Universal Time)"]
Expected Values: ["Mon Aug 05 2024 00:00:00 GMT+0300 (Eastern European Summer Time)", "Tue Aug 06 2024 00:00:00 GMT+0300 (Eastern European Summer Time)"]
Output: Mon Aug 05 2024 00:00:00 GMT+0300 (Eastern European Summer Time)

Target Field: is_critical_spare
Historical Values: [false, false, true, false]
Expected Values: [true, false]
Output: false

Target Field: soldscrapdate
Field Rules/Description: Date when equipment was sold or scrapped. It must be after the commission date.
Accepted Values: {{"commissiondate": "Mon Aug 05 2024 00:00:00 GMT+0300 (Eastern European Summer Time)", "equipmentdesc": "Old Pump"}}
Historical Values: ["Wed Sep 04 2024 00:00:00 GMT+0300 (Eastern European Summer Time)"]
Output: Thu Sep 05 2024 00:00:00 GMT+0300 (Eastern European Summer Time)

Asset Description: {asset_description}
Field to Predict: {target_field}
Field Rules/Description:
{field_description}

Accepted Values:
{accepted_values}

Historical Values for {target_field}: {historical_values}
Expected Values for {target_field} (if provided, choose from this list only if it is a valid value based on the field rules/description): {expected_values}
Output:
""",
            )
        raise ValueError(f"Prompt '{name}' not found.")
