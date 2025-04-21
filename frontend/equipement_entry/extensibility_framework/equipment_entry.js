Ext.define('EAM.custom.FieldFocusAPIExample', {
    extend: 'EAM.custom.AbstractExtensibleFramework',

    assetNameValue: null,

    getSelectors: function () {
        var self = this;
        return {
            '[extensibleFramework] [tabName=HDR][isTabView=true]': {
                afterrender: function (formPanel) {
                    var form = formPanel.getForm();
                    form.getFields().each(function (field) {
                        // Trigger API call on blur instead of focus to ensure other field values are potentially set
                        field.on('blur', self.handleFieldBlur, self);
                        // Still capture asset name on focus or change
                        if (field.getName() === 'equipmentno') {
                            field.on('change', function (fld, newValue) {
                                this.assetNameValue = newValue ? newValue.trim() : null;
                                console.log('Asset name stored:', this.assetNameValue);
                            }, self);
                            field.on('focus', function (fld) { // Also capture on focus if needed
                                this.assetNameValue = fld.getValue() ? fld.getValue().trim() : null;
                            }, self);
                        }
                    });
                }
            }
        };
    },

    handleFieldBlur: function (blurredField) {
        var fieldName = blurredField.getName();

        // Don't trigger API for the asset name field itself
        if (fieldName === 'equipmentno') {
            return;
        }

        // Ensure asset name is available
        if (!this.assetNameValue) {
            console.warn('Asset Name is not set. Cannot call API.');
            // Optionally show a user message: EAM.Utils.toastMessage('Please enter Asset Name first!');
            return;
        }

        // Gather accepted values from other fields in the form
        var acceptedValues = {};
        var formPanel = EAM.Utils.getCurrentTab().getFormPanel(); // Get the form panel
        if (formPanel) {
            var form = formPanel.getForm();
            form.getFields().each(function (field) {
                var currentFieldName = field.getName();
                // Exclude the field that just lost focus and the asset number field
                if (currentFieldName !== fieldName && currentFieldName !== 'equipmentno' && field.getValue()) {
                    acceptedValues[currentFieldName] = field.getValue();
                }
            });
        } else {
            console.error("Could not find the form panel.");
            return;
        }

        console.log('Calling API for field:', fieldName, 'with accepted values:', acceptedValues);
        this.callPredictionAPI(fieldName, acceptedValues, blurredField);

    },

    callPredictionAPI: function (attributeFieldName, acceptedValuesMap, targetField) {
        // Ensure assetNameValue is current
        if (!this.assetNameValue) {
            console.error('Asset Name not available for API call.');
            return;
        }

        const BASE_URL = 'https://619e-102-191-34-120.ngrok-free.app'; // Ensure this is your correct backend URL
        // Updated URL structure for POST request
        const API_URL = `${BASE_URL}/equipment-entry/generate/${encodeURIComponent(this.assetNameValue)}/`;

        const payload = {
            attribute: attributeFieldName,
            accepted_values: acceptedValuesMap
        };

        console.log('API Request:', {
            method: 'POST',
            url: API_URL,
            body: payload,
            timestamp: new Date().toISOString()
        });

        fetch(API_URL, {
            method: 'POST', // Changed to POST
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'ngrok-skip-browser-warning': 'true'
            },
            body: JSON.stringify(payload)
        })
            .then(async (response) => {
                // ... existing response handling logic ...
                const text = await response.text();
                console.log('API Raw Response:', text);

                if (!response.ok) {
                    console.error('API Error Response:', response.status, text);
                    // Optionally show error to user: EAM.Utils.toastMessage(`Error: ${response.statusText}`);
                    return { error: `Request failed with status ${response.status}` };
                }

                try {
                    const data = JSON.parse(text);
                    console.log('API Parsed Response:', data);

                    // Set field value if response contains llm_response and it's not null/empty
                    if (data.llm_response) {
                        // Check if the target field still exists and is part of a form
                        if (targetField && targetField.ownerCt && targetField.ownerCt.getForm) {
                            const formPanel = targetField.ownerCt; // Get the form panel containing the field
                            formPanel.setFldValue(attributeFieldName, data.llm_response);
                            console.log(`Updated ${attributeFieldName} with:`, data.llm_response);
                        } else {
                            console.warn(`Target field ${attributeFieldName} no longer available or not in a form.`);
                        }
                    } else {
                        console.log(`No prediction returned for ${attributeFieldName}.`);
                    }

                    return data;
                } catch (e) {
                    console.error('JSON Parse Error:', e, 'Raw text:', text);
                    // Optionally show error to user: EAM.Utils.toastMessage('Error processing server response.');
                    return { error: 'Invalid JSON response' };
                }
            })
            .catch(error => {
                console.error('API Request Failed:', error);
                // Optionally show error to user: EAM.Utils.toastMessage('Network error or API unreachable.');
            });
    }
});
