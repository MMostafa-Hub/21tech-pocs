/*
    EF that Handles attachement Documents | BSDOCU.js
    It Fire when checkbox "Generate PM" is checked and Call the Webservice " Document attachement"
    By @Lucky |  21Tech | 5/7/2025

    Modified by @Mohamed.Mostafa | 21Tech | 5/12/2025
    - Added simplified success message in popup instead of showing full API response
    - Improved error handling and messaging
    - Added ngrok URL to the API call
*/
Ext.define('EAM.custom.external_bsdocu', {
    extend: 'EAM.custom.AbstractExtensibleFramework',
    getSelectors: function () {
        var efc = this;
        return {
            '[extensibleFramework] [tabName=HDR][isTabView=true]': {
                afterrender: function (formPanel) {
                    debugger;
                    console.log('Form Panel rendered, processing fields and sections...');
                },
                afterloaddata: function () {
                    debugger;
                }
            },
            '[extensibleFramework] [tabName=HDR][isTabView=true] [name=udfchkbox01]': {
                change: function (checkbox, newVal, oldVal) {
                    debugger;

                    var p = EAM.Utils.getCurrentTab().getFormPanel();
                    if (newVal === true) {
                        debugger;
                        var vals = p.getFldValues(["documentcode", "filepath"]);
                        var vDoccode = vals.documentcode;

                        if (!vDoccode) {
                            efc.popUpMsg('Missing Data : Document Code is required to call the API.');
                            checkbox.setValue(false);
                            return;
                        }

                        // --- Prepare for New API Call ---
                        const BASE_URL = 'https://224b-102-191-231-78.ngrok-free.app'; // ensure this is your correct backend URL
                        // Corrected API URL with the proper prefix
                        const API_URL = `${BASE_URL}/api/maintenance/process-document/`;

                        const payload = {
                            document_code: vDoccode,
                            create_in_eam: true
                        };

                        console.log('API Request:', {
                            method: 'POST',
                            url: API_URL,
                            body: payload,
                            timestamp: new Date().toISOString()
                        });

                        var headers = {
                            'Accept': 'application/json',
                            'Content-Type': 'application/json',
                            'ngrok-skip-browser-warning': 'true'
                        };

                        // --- Make the API call using Fetch API ---
                        fetch(API_URL, {
                            method: 'POST',
                            headers: headers,
                            body: JSON.stringify(payload)
                        })
                            .then(response => {
                                if (!response.ok) {
                                    // Try to get error message from response body
                                    return response.text().then(text => {
                                        // Construct a more detailed error message
                                        let errorDetail = `API request failed with status ${response.status} (${response.statusText})`;
                                        if (text) {
                                            if (response.status === 400) {
                                                errorDetail += ': Forbidden. Check credentials, EAM permissions, tenant/org, and API access rules.';
                                            } else if (text.length < 200 && !text.toLowerCase().includes("<html")) { // Show short plain text errors
                                                errorDetail += ': ' + text;
                                            } else {
                                                errorDetail += '. Server returned a detailed error (see console for full response).';
                                            }
                                        }
                                        // Log the raw server response for debugging
                                        console.error("Raw error response from server:", text);
                                        throw new Error(errorDetail);
                                    });
                                }
                                return response.json(); // Or response.text() if it's not JSON
                            })
                            .then(data => {
                                let messageContent = 'API Call Successful!';
                                if (data.extracted_data) {
                                    messageContent += '\n\nPM Schedule:';
                                    messageContent += '\n  ' + data.extracted_data.code;

                                    messageContent += '\n\nTask Plans:';
                                    data.extracted_data.task_plans.forEach((taskPlan, taskIndex) => {
                                        if (taskIndex > 0) { // Add a blank line between task plans for separation
                                            messageContent += '\n';
                                        }
                                        messageContent += '\n  • ' + taskPlan.task_code; // Task plan code
                                        if (taskPlan.checklist && taskPlan.checklist.length > 0) {
                                            // Checklist items listed directly under the task plan, indented
                                            taskPlan.checklist.forEach(checklistItem => {
                                                messageContent += '\n    - ' + checklistItem.checklist_id; // Indented checklist item
                                            });
                                        }
                                    });
                                } else {
                                    // Fallback for unexpected data structure, with basic pretty-printing for objects
                                    messageContent += '\n\n' + (typeof data === 'object' ? JSON.stringify(data, null, 2) : data);
                                }
                                efc.popUpMsg(messageContent);
                                console.log('API Success:', data);
                            })
                            .catch(error => {
                                console.error('API Call Error Object:', error); // Log the full error object
                                // Use the message from the error thrown in the .then(response => ...) block
                                var errorMessageToShow = (error && error.message) ? error.message : 'An unknown API error occurred. Check console for details.';
                                efc.popUpMsg(errorMessageToShow);
                                checkbox.setValue(false);
                            });
                    }
                }
            }
        }
    },
    //--- Functions definition 
    popUpMsg: function (msg) {
        EAM.MsgBox.show({
            title: 'Message Box',
            msgs: [{
                type: 'error',
                msg: EAM.Lang.getCustomFrameworkMessage(msg)
            }],
            buttons: EAM.MsgBox.OK,
            fn: function (y) { },
            scope: this
        });
    }
});