from langchain.prompts import PromptTemplate

class PromptFactory:
    @staticmethod
    def get_prompt(name: str) -> PromptTemplate:
        # Currently only supporting "asset_entry_prompt"
        if name == "asset_entry_prompt":
            return PromptTemplate(
                input_variables=["asset_name", "historical_values", "target_field", "field_description", "accepted_values"],
                template="""You are a universal equipment pattern analyzer. Generate ONLY the next logical raw value for {target_field} following the exact format and pattern of historical values, considering any already accepted values for other fields.

Pattern Analysis Guidelines:
1. Identify value type(s) and pattern (numerical, categorical, codes, mixed)
2. Detect progression rules (incremental, cyclical, status-based, etc.)
3. Maintain exact format (including symbols, units, casing)
4. Continue sequence logic without conversions
5. For mixed formats: Preserve original value types
6. Consider the context provided by already accepted field values.

Output Rules:
- Return ONLY the raw next value as it would appear in the database
- No explanations, formatting, or additional text
- Preserve original value style and structure
- Follow identified sequence logic exactly

Examples:
Historical: ["Low", "Medium", "High"]
Output: Critical

Historical: ["A-101", "A-102", "B-101"]
Output: B-102

Historical: [108, 112, 115, 118]
Output: 121

Historical: ["NORMAL", "NORMAL", "WARNING", "NORMAL"]
Output: Normal

Asset: {asset_name}
Field to Predict: {target_field}
Field Description:
{field_description}

Accepted Values:
{accepted_values}

Historical Values for {target_field}: {historical_values}
Output:
"""
            )
        raise ValueError(f"Prompt '{name}' not found.")
