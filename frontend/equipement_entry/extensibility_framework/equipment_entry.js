
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
                        field.on('focus', self.handleFieldFocus, self);
                    });
                }
            }
        };
    },

    handleFieldFocus: function (focusedField) {
        var fieldName = focusedField.getName();

        if (fieldName === 'equipmentno') {
            this.assetNameValue = focusedField.getValue().trim();
            console.log('Asset name stored:', this.assetNameValue);
            return;
        }

        if (this.assetNameValue) {
            this.callSampleAPI(fieldName, focusedField);
        } else {
            console.warn('Please enter Asset Name first!');
        }
    },

    callSampleAPI: function (attributeFieldName, targetField) {
        const BASE_URL = 'https://619e-102-191-34-120.ngrok-free.app';
        const API_URL = `${BASE_URL}/equipment-entry/generate/${encodeURIComponent(this.assetNameValue)}?attribute=${encodeURIComponent(attributeFieldName)}`;

        console.log('API Request:', {
            method: 'GET',
            url: API_URL,
            timestamp: new Date().toISOString()
        });

        fetch(API_URL, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'ngrok-skip-browser-warning': 'true'
            }
        })
            .then(async (response) => {
                const text = await response.text();
                console.log('API Raw Response:', text);

                try {
                    const data = JSON.parse(text);
                    console.log('API Parsed Response:', data);

                    // Set field value if response contains llm_response
                    if (data.llm_response) {
                        const formPanel = EAM.Utils.getCurrentTab().getFormPanel();
                        formPanel.setFldValue(attributeFieldName, data.llm_response);
                        console.log(`Updated ${attributeFieldName} with:`, data.llm_response);
                    }

                    return data;
                } catch (e) {
                    console.error('JSON Parse Error:', e);
                    return { error: 'Invalid JSON response' };
                }
            })
            .catch(error => {
                console.error('API Request Failed:', error);
            });
    }
});
