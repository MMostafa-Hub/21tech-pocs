Ext.define('EAM.custom.external_bsdocu', {
    extend: 'EAM.custom.AbstractExtensibleFramework',

    getSelectors: function () {
        const efc = this;

        // Format response for maintenance document
        const formatMaintenanceResponse = (data) => {
            let message = 'API Call Successful!';
            if (data.extracted_data) {
                message += '\n\nPM Schedule:\n  ' + data.extracted_data.code;
                message += '\n\nTask Plans:';
                data.extracted_data.task_plans.forEach((taskPlan, index) => {
                    if (index > 0) message += '\n';
                    message += '\n  • ' + taskPlan.task_code;
                    (taskPlan.checklist || []).forEach(item => {
                        message += '\n    - ' + item.checklist_id;
                    });
                });
            } else {
                message += '\n\n' + (typeof data === 'object' ? JSON.stringify(data, null, 2) : data);
            }
            return message;
        };

        // Format response for service manual
        const formatServiceResponse = (data) => {
            let message = 'API Call Successful!';
            if (data.extracted_data) {
                message += '\n\nService Manuals:\n  ' + data.extracted_data.code;
                message += '\n\nTroubleshooting Guide:';
                data.extracted_data.task_plans.forEach((taskPlan, index) => {
                    if (index > 0) message += '\n';
                    message += '\n  • ' + taskPlan.task_code;
                    (taskPlan.checklist || []).forEach(item => {
                        message += '\n    - ' + item.checklist_id;
                    });
                });
            } else {
                message += '\n\n' + (typeof data === 'object' ? JSON.stringify(data, null, 2) : data);
            }
            return message;
        };

        return {
            // Form Panel loaded
            '[extensibleFramework] [tabName=HDR][isTabView=true]': {
                afterrender: function () {
                    console.log('Form Panel rendered, processing fields and sections...');
                },
                afterloaddata: function () {
                    // Data loaded into the form
                }
            },

            // Checkbox 1: Generate PM | Maintenance Document 
            '[extensibleFramework] [tabName=HDR][isTabView=true] [name=udfchkbox01]': {
                change: efc.createCheckboxHandler('/api/maintenance/process-document/', formatMaintenanceResponse)
            },

            // Checkbox 2: Generate Service Manuals | Service Manual Document
            '[extensibleFramework] [tabName=HDR][isTabView=true] [name=udfchkbox02]': {
                change: efc.createCheckboxHandler('/api/service-manuals/process-document/', formatServiceResponse)
            }
        };
    },

    // Pop-up error or success message
    popUpMsg: function (msg) {
        EAM.MsgBox.show({
            title: 'Message Box',
            msgs: [{
                type: 'error',
                msg: EAM.Lang.getCustomFrameworkMessage(msg)
            }],
            buttons: EAM.MsgBox.OK,
            fn: function () { },
            scope: this
        });
    },

    // Generic handler factory for checkbox APIs
    createCheckboxHandler: function (apiPath, formatResponseCallback) {
		debugger;
        const efc = this;
        const baseUrl = 'https://chief-unified-moccasin.ngrok-free.app';

        return function (checkbox, newVal) {
			debugger;
            if (newVal === true) {
                const p = EAM.Utils.getCurrentTab().getFormPanel();
                const vals = p.getFldValues(["documentcode", "filepath"]);
                const vDoccode = vals.documentcode;

                if (!vDoccode) {
                    efc.popUpMsg('Missing Data : Document Code is required to call the API.');
                    checkbox.setValue(false);
                    return;
                }

                checkbox.setDisabled(true); // Optional UX feedback
                efc.handleAPIcall(baseUrl, apiPath, vDoccode, formatResponseCallback, checkbox);
            }
        };
    },

    // Centralized API call handler
    handleAPIcall: function (baseUrl, apiPath, vDoccode, formatResponseCallback, checkbox) {
        debugger;
		const API_URL = `${baseUrl}${apiPath}`;
        const payload = {
            document_code: vDoccode,
            create_in_eam: false
        };

        console.log('API Request:', {
            method: 'POST',
            url: API_URL,
            body: payload,
            timestamp: new Date().toISOString()
        });

        const headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'ngrok-skip-browser-warning': 'true'
        };

        fetch(API_URL, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify(payload)
        })
            .then(response => {
                if (!response.ok) {
                    return response.text().then(text => {
                        let errorDetail = `API request failed with status ${response.status} (${response.statusText})`;
                        if (text) {
                            if (response.status === 400) {
                                errorDetail += ': Forbidden. Check credentials, EAM permissions, tenant/org, and API access rules.';
                            } else if (text.length < 200 && !text.toLowerCase().includes("<html")) {
                                errorDetail += ': ' + text;
                            } else {
                                errorDetail += '. Server returned a detailed error (see console for full response).';
                            }
                        }
                        console.error("Raw error response from server:", text);
                        throw new Error(errorDetail);
                    });
                }
                return response.json();
            })
            .then(data => {
                const messageContent = (typeof formatResponseCallback === 'function')
                    ? formatResponseCallback(data)
                    : 'API Call Successful.\n\n' + JSON.stringify(data, null, 2);

                this.popUpMsg(messageContent);
                console.log('API Success:', data);
            })
            .catch(error => {
                console.error('API Call Error Object:', error);
                const errorMessageToShow = (error && error.message)
                    ? error.message
                    : 'An unknown API error occurred. Check console for details.';
                this.popUpMsg(errorMessageToShow);
                if (checkbox) checkbox.setValue(false);
            })
            .finally(() => {
                if (checkbox) checkbox.setDisabled(false); // Re-enable checkbox
            });
    }
});

