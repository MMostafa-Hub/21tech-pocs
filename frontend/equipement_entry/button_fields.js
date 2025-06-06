Ext.define('EAM.custom.AddButtonOnFocus', {
    extend: 'EAM.custom.AbstractExtensibleFramework',

    // Store references to created buttons, mapping field name to button instance
    fieldButtons: {},

    getSelectors: function () {
        var self = this;
        return {
            // Target the form panel within the 'HDR' tab
            '[extensibleFramework] [tabName=HDR][isTabView=true]': {
                afterrender: function (formPanel) {
                    console.log('Form Panel rendered, processing fields and sections...');
                    // --- Existing logic for field focus/blur --- 
                    var form = formPanel.getForm();
                    var fieldNames = Ext.Array.map(form.getFields().items, function (field) {
                        return field.getName();
                    });
                    console.log('Form field names:', fieldNames);


                    form.getFields().each(function (field) {
                        field.on('focus', self.handleFieldFocus, self);
                        field.on('blur', self.handleFieldBlur, self);
                    });
                    // --- End of existing logic ---

                    // --- New Discovery Logic: Log all components within the form panel ---
                    console.log('--- Discovering components within form panel ---');
                    var allComponents = formPanel.query('component'); // Query ALL components
                    console.log('Found total components:', allComponents.length);
                    Ext.each(allComponents, function (component, index) {
                        // Log relevant properties like xtype, title, id, isFormField
                        console.log(
                            `Component ${index}: ` +
                            `xtype: ${component.xtype}, ` +
                            `id: ${component.id}, ` +
                            `title: ${component.title || 'N/A'}, ` +
                            `isFormField: ${component.isFormField || false}, ` +
                            `hasHeader: ${!!component.header}`
                        );

                        // --- Attempt to add button based on title (keep previous logic for now) ---
                        // Check if the component looks like a section (has a header and a title)
                        if (component.header && component.title) {
                            console.log('-> Potential section found based on header/title:', component.title);
                            var buttonText = component.title + ' Action';
                            self.addSectionHeaderButton(component, buttonText); // Pass the component directly
                        }
                        // --- End of button adding attempt ---
                    });
                    console.log('--- End of component discovery ---');
                    // --- End of new discovery logic ---
                }
            }
        };
    },

    handleFieldFocus: function (focusedField) {
        var self = this;
        var fieldName = focusedField.getName();
        var fieldId = focusedField.getId(); // Use field's Ext JS ID
        var fieldValue = focusedField.getValue(); // Get the current value of the field

        // Log the field name, ID, and its current value
        console.log('Focus on field:', fieldName, 'ID:', fieldId, 'Current Value:', fieldValue);

        // Don't add button for the main equipment field or if button already exists
        if (fieldName === 'equipmentno' || this.fieldButtons[fieldId]) {
            return;
        }

        // Use Ext.defer to allow the field's rendering/focus logic to complete
        Ext.defer(function () {
            var fieldEl = focusedField.inputEl || focusedField.el; // Get the input element or main element
            var componentEl = focusedField.getEl(); // Get the main component element (e.g., the x-form-item div)

            if (!fieldEl || !componentEl) {
                console.warn('Could not find element for field:', fieldName);
                return;
            }

            // Create the button
            var predictButton = Ext.create('Ext.button.Button', {
                text: 'Predict', // Or use an icon cls: 'x-fa fa-magic'
                tooltip: 'Get prediction for ' + (focusedField.fieldLabel || fieldName),
                // Render the button into the field's main component element
                // This should place it after the label and input body within the form item structure
                renderTo: componentEl.dom,
                style: {
                    // Adjust styling for side-by-side placement
                    marginLeft: '5px',
                    verticalAlign: 'top', // Align to the top relative to the field container
                    display: 'inline-block' // Ensure button takes space correctly
                },
                handler: function () {
                    self.onPredictButtonClick(focusedField);
                }
            });

            // Store the button instance using the field's ID as the key
            this.fieldButtons[fieldId] = predictButton;
            console.log('Button created for field:', fieldName, 'ID:', fieldId);

        }, 50, this); // Small delay (50ms)

    },

    handleFieldBlur: function (blurredField) {
        var fieldId = blurredField.getId();
        var button = this.fieldButtons[fieldId];

        console.log('Blur on field:', blurredField.getName(), 'ID:', fieldId);

        if (button) {
            // Use Ext.defer to avoid issues if blur triggers focus on another element immediately
            Ext.defer(function () {
                // Check if the button still exists before destroying
                if (button && !button.destroyed) {
                    button.destroy();
                    console.log('Button destroyed for field ID:', fieldId);
                }
                // Remove the reference
                delete this.fieldButtons[fieldId];
            }, 100, this); // Slightly longer delay for blur
        }
    },

    onPredictButtonClick: function (targetField) {
        var fieldName = targetField.getName();
        console.log('Predict button clicked for field:', fieldName);

        // 1. Get the asset number (equipmentno)
        var assetNameValue = null;
        var formPanel = EAM.Utils.getCurrentTab().getFormPanel(); // Get the form panel
        if (!formPanel) {
            console.error("Could not find the form panel.");
            console.error('Error: Could not find form.');
            return;
        }
        var form = formPanel.getForm();
        var equipmentField = form.findField('equipmentno');
        if (equipmentField && equipmentField.getValue()) {
            assetNameValue = equipmentField.getValue().trim();
        }

        if (!assetNameValue) {
            console.warn('Asset Name (equipmentno) is not set. Cannot call API.');
            console.warn('Please enter the Equipment Number first!');
            return;
        }

        // 2. Get other accepted field values
        var acceptedValues = {};
        form.getFields().each(function (field) {
            var currentFieldName = field.getName();
            // Exclude the target field itself and the asset number field
            if (currentFieldName !== fieldName && currentFieldName !== 'equipmentno' && field.getValue()) {
                acceptedValues[currentFieldName] = field.getValue();
            }
        });

        console.log('Calling API for field:', fieldName, 'with asset:', assetNameValue, 'and accepted values:', acceptedValues);

        // 3. Call the fetch API
        const BASE_URL = 'https://6542-197-132-78-174.ngrok-free.app'; // Ensure this is your correct backend URL
        // Corrected API URL with the proper prefix
        const API_URL = `${BASE_URL}/api/equipment-entries/generate/${encodeURIComponent(assetNameValue)}/`;

        const payload = {
            attribute: fieldName,
        };

        console.log('API Request:', {
            method: 'POST',
            url: API_URL,
            body: payload,
            timestamp: new Date().toISOString()
        });

        fetch(API_URL, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'ngrok-skip-browser-warning': 'true'
            },
            body: JSON.stringify(payload)
        })
            .then(async (response) => {
                const text = await response.text();
                console.log('API Raw Response:', text);

                if (!response.ok) {
                    console.error('API Error Response:', response.status, text);
                    console.error(`Error fetching prediction: ${response.statusText}`);
                    return;
                }

                try {
                    const data = JSON.parse(text);
                    console.log('API Parsed Response:', data);

                    if (data.llm_response) {
                        var currentFormPanel = EAM.Utils.getCurrentTab().getFormPanel();
                        if (currentFormPanel) {
                            var llmResponseStr = data.llm_response;
                            var fieldToUpdate = currentFormPanel.getForm().findField(fieldName);
                            var fieldLabel = (fieldToUpdate && !fieldToUpdate.destroyed) ? fieldToUpdate.fieldLabel : fieldName;

                            console.log(`Attempting to set value for ${fieldName} (xtype: ${fieldToUpdate ? fieldToUpdate.xtype : 'unknown'}) with response:`, llmResponseStr);

                            var valueToSet = llmResponseStr; // Default to raw string

                            if (fieldToUpdate) {
                                var fieldXtype = fieldToUpdate.xtype;
                                // Add 'uxdate' to the list of recognized date field xtypes
                                if (fieldXtype === 'datefield' || fieldXtype === 'xdatefield' || fieldXtype === 'uxdate') {
                                    var dateObject = new Date(llmResponseStr);
                                    if (!isNaN(dateObject.getTime())) {
                                        valueToSet = dateObject;
                                        console.log(`Field ${fieldName} is a date field (xtype: ${fieldXtype}). Parsed to Date object:`, dateObject);
                                    } else {
                                        console.warn(`Field ${fieldName} (xtype: ${fieldXtype}) received non-date string: \\"${llmResponseStr}\\". Setting raw string.`);
                                        // valueToSet remains llmResponseStr
                                    }
                                } else if (fieldXtype === 'numberfield' || fieldXtype === 'xnumberfield') {
                                    var parsedNumber = parseFloat(llmResponseStr);
                                    if (!isNaN(parsedNumber)) {
                                        valueToSet = parsedNumber;
                                        console.log(`Field ${fieldName} is a number field. Parsed to number:`, parsedNumber);
                                    } else {
                                        console.warn(`Field ${fieldName} (numberfield) received non-numeric string: \\"${llmResponseStr}\\". Setting raw string.`);
                                        // valueToSet remains llmResponseStr
                                    }
                                } else {
                                    console.log(`Field ${fieldName} is xtype ${fieldXtype}. Setting raw string value.`);
                                    // valueToSet remains llmResponseStr for other types
                                }
                                currentFormPanel.setFldValue(fieldName, valueToSet);
                                console.log(`Successfully attempted to update ${fieldLabel} via formPanel with value:`, valueToSet, `(typeof: ${typeof valueToSet})`);
                            } else {
                                console.warn(`Could not get fresh reference to field ${fieldName}. Setting raw string as fallback.`);
                                currentFormPanel.setFldValue(fieldName, llmResponseStr); // Fallback if fieldToUpdate is null
                            }
                        } else {
                            console.warn(`Could not find the current form panel to update field ${fieldName}.`);
                        }
                    } else {
                        console.log(`No prediction returned for ${fieldName}.`);
                    }
                } catch (e) {
                    console.error('JSON Parse Error:', e, 'Raw text:', text);
                }
            })
            .catch(error => {
                console.error('API Request Failed:', error);
            });
    }, // End of onPredictButtonClick

    /**
     * Adds a button next to a specified component's header title.
     * @param {Ext.Component} component The component (e.g., panel, fieldset).
     * @param {String} buttonText The text for the button.
     */
    addSectionHeaderButton: function (component, buttonText) {
        var self = this; // Keep reference to the framework instance
        var section = component;
        var sectionTitle = section.title || 'Section';
        var buttonCls = 'custom-section-btn-' + Ext.id(); // Unique class for this button instance
        var checkCls = 'custom-section-btn'; // General class to check for existence

        console.log('Attempting to add button for:', sectionTitle);

        // Check if header component exists, is rendered, and has a DOM element
        if (section.header && section.header.rendered && section.header.el) {
            var header = section.header;
            var headerEl = header.el;
            var titleCmp = header.down('title'); // Find the title component within the header

            console.log('Found header element for:', sectionTitle, headerEl.dom);

            var existingButton = header.down('button[cls~=' + checkCls + ']');
            if (existingButton) {
                console.log('Button with class ' + checkCls + ' already exists for:', sectionTitle);
                return; // Don't add duplicate button
            }

            if (titleCmp) {
                console.log('Found title component for:', sectionTitle, titleCmp.id);
                var titleIndex = header.items.indexOf(titleCmp);
                console.log('Title index:', titleIndex);

                if (titleIndex !== -1) {
                    var button = Ext.create('Ext.button.Button', {
                        text: buttonText,
                        cls: checkCls + ' ' + buttonCls,
                        style: {
                            marginLeft: '10px',
                            verticalAlign: 'middle',
                            display: 'inline-block'
                        },
                        // Add the event parameter 'e' to the handler
                        handler: function (button, e) {
                            // Stop the event from propagating to the header, preventing collapse/expand
                            e.stopEvent();

                            // --- Bulk Prediction Logic ---
                            console.log('Bulk predict button clicked for section:', sectionTitle);
                            var formPanel = EAM.Utils.getCurrentTab().getFormPanel();
                            if (!formPanel) {
                                console.error("Could not find the form panel for bulk prediction.");
                                EAM.Utils.toastMessage('Error: Could not find form for bulk prediction.');
                                return;
                            }
                            var form = formPanel.getForm();

                            // 1. Get Asset Name (equipmentno)
                            var assetNameValue = null;
                            var equipmentField = form.findField('equipmentno');
                            if (equipmentField && equipmentField.getValue()) {
                                assetNameValue = equipmentField.getValue().trim();
                            }
                            if (!assetNameValue) {
                                console.warn('Asset Name (equipmentno) is not set. Cannot call bulk API.');
                                EAM.Utils.toastMessage('Please enter the Equipment Number first!');
                                return;
                            }

                            // 2. Get field names within this section
                            var sectionFields = section.query('field'); // Query fields within the specific section component
                            var attributesToPredict = [];
                            var sectionFieldNames = new Set(); // Keep track of field names in this section
                            Ext.each(sectionFields, function (field) {
                                var fieldName = field.getName();
                                if (fieldName && fieldName !== 'equipmentno') { // Exclude equipmentno
                                    attributesToPredict.push(fieldName);
                                    sectionFieldNames.add(fieldName);
                                }
                            });

                            if (attributesToPredict.length === 0) {
                                console.log('No fields found within section:', sectionTitle);
                                EAM.Utils.toastMessage('No fields to predict in this section.');
                                return;
                            }
                            console.log('Fields to predict in section:', attributesToPredict);

                            // 3. Get accepted values from fields *outside* this section
                            var acceptedValues = {};
                            form.getFields().each(function (field) {
                                var currentFieldName = field.getName();
                                // Exclude fields in the current section, the asset number field, and empty fields
                                if (currentFieldName && currentFieldName !== 'equipmentno' && !sectionFieldNames.has(currentFieldName) && field.getValue()) {
                                    acceptedValues[currentFieldName] = field.getValue();
                                }
                            });
                            console.log('Accepted values from other sections:', acceptedValues);

                            // 4. Call the Bulk Prediction API
                            const BASE_URL = 'https://6542-197-132-78-174.ngrok-free.app'; // Ensure this is correct
                            const API_URL = `${BASE_URL}/api/equipment-entries/generate-bulk/${encodeURIComponent(assetNameValue)}/`;

                            const payload = {
                                attributes: attributesToPredict,
                                accepted_values: acceptedValues
                            };

                            console.log('Bulk API Request:', {
                                method: 'POST',
                                url: API_URL,
                                body: payload,
                                timestamp: new Date().toISOString()
                            });

                            fetch(API_URL, {
                                method: 'POST',
                                headers: {
                                    'Accept': 'application/json',
                                    'Content-Type': 'application/json',
                                    'ngrok-skip-browser-warning': 'true'
                                },
                                body: JSON.stringify(payload)
                            })
                                .then(async (response) => {
                                    const text = await response.text();
                                    console.log('Bulk API Raw Response:', text);

                                    if (!response.ok) {
                                        console.error('Bulk API Error Response:', response.status, text);
                                        console.error(`Error fetching bulk predictions: ${response.statusText}`);
                                        return;
                                    }

                                    try {
                                        const data = JSON.parse(text);
                                        console.log('Bulk API Parsed Response:', data);

                                        if (data.predictions) {
                                            let updatedCount = 0;
                                            let errorCount = 0;
                                            var currentFormPanel = EAM.Utils.getCurrentTab().getFormPanel();
                                            if (currentFormPanel) {
                                                Ext.Object.each(data.predictions, function (fieldName, value) {
                                                    try {
                                                        var llmResponseStr = value;
                                                        var fieldToUpdate = currentFormPanel.getForm().findField(fieldName);
                                                        var valueToSet = llmResponseStr; // Default to raw string

                                                        if (fieldToUpdate) {
                                                            var fieldXtype = fieldToUpdate.xtype;
                                                            console.log(`Bulk processing field ${fieldName} (xtype: ${fieldXtype}), value: \\"${llmResponseStr}\\"`)
                                                            // Add 'uxdate' to the list of recognized date field xtypes
                                                            if (fieldXtype === 'datefield' || fieldXtype === 'xdatefield' || fieldXtype === 'uxdate') {
                                                                var dateObject = new Date(llmResponseStr);
                                                                if (!isNaN(dateObject.getTime())) {
                                                                    valueToSet = dateObject;
                                                                    console.log(`Bulk update for ${fieldName} (xtype: ${fieldXtype}) with Date object:`, dateObject);
                                                                } else {
                                                                    console.warn(`Bulk update for ${fieldName} (xtype: ${fieldXtype}): Failed to parse \\"${llmResponseStr}\\" as date. Setting raw string.`);
                                                                    // valueToSet remains llmResponseStr
                                                                }
                                                            } else if (fieldXtype === 'numberfield' || fieldXtype === 'xnumberfield') {
                                                                var parsedNumber = parseFloat(llmResponseStr);
                                                                if (!isNaN(parsedNumber)) {
                                                                    valueToSet = parsedNumber;
                                                                    console.log(`Bulk update for ${fieldName} (numberfield) with number:`, parsedNumber);
                                                                } else {
                                                                    console.warn(`Bulk update for ${fieldName} (numberfield): Failed to parse \\"${llmResponseStr}\\" as number. Setting raw string.`);
                                                                    // valueToSet remains llmResponseStr
                                                                }
                                                            } else {
                                                                console.log(`Bulk update for ${fieldName} (xtype ${fieldXtype}). Setting raw string value.`);
                                                                // valueToSet remains llmResponseStr
                                                            }
                                                            currentFormPanel.setFldValue(fieldName, valueToSet);
                                                            console.log(`Bulk update for ${fieldName} (xtype: ${fieldXtype}) successful with value:`, valueToSet, `(typeof: ${typeof valueToSet})`);
                                                        } else {
                                                            console.warn(`Bulk update: Could not find field ${fieldName} to check xtype. Setting raw string: \\"${llmResponseStr}\\"`);
                                                            currentFormPanel.setFldValue(fieldName, llmResponseStr); // Fallback
                                                        }
                                                        updatedCount++;
                                                    } catch (fieldError) {
                                                        console.error(`Error bulk updating field ${fieldName}:`, fieldError);
                                                        errorCount++;
                                                    }
                                                });
                                                let message = `Applied ${updatedCount} bulk prediction(s) to ${sectionTitle}.`;
                                                if (errorCount > 0) message += ` ${errorCount} error(s) occurred.`;
                                                console.log(message);
                                            } else {
                                                console.error("Could not find form panel to apply bulk updates.");
                                            }
                                        } else {
                                            console.warn('No predictions object returned in bulk response.');
                                        }
                                    } catch (e) {
                                        console.error('Bulk JSON Parse Error:', e, 'Raw text:', text);
                                    }
                                })
                                .catch(error => {
                                    console.error('Bulk API Request Failed:', error);
                                });
                            // --- End of Bulk Prediction Logic ---
                        }
                    }); // End of Ext.create('Ext.button.Button', ...)

                    header.insert(titleIndex + 1, button);
                    console.log('Button inserted into header items after title for:', sectionTitle, 'with class:', buttonCls);
                } else {
                    console.warn('Could not find title component index within header items for:', sectionTitle);
                }
            } else {
                console.warn('Could not find title component within header for:', sectionTitle, '. Cannot insert button accurately.');
            }
        } else {
            // Log detailed reason if header/element is missing
            if (!section.header) {
                console.warn('Component ', sectionTitle, ' (' + section.id + ') does not have a header component.');
            } else if (!section.header.rendered) {
                console.warn('Header for ', sectionTitle, ' (' + section.id + ') is not rendered yet.');
                // Attempt to add button after layout, might help if rendering is delayed
                section.header.on('afterrender', function (header) { // Pass header argument
                    console.log('Header rendered late for:', sectionTitle, ', attempting button add again.');
                    // Ensure 'this' refers to the framework instance if needed, or use 'self'
                    this.addSectionHeaderButton(section, buttonText); // Retry adding the button
                }, this, { single: true }); // Use 'this' scope and run only once

            } else if (!section.header.el) {
                console.warn('Header for ', sectionTitle, ' (' + section.id + ') does not have a DOM element (el).');
            }
        }
    }, // <-- Added comma here

    // Optional: Clean up any remaining buttons if the framework instance is destroyed
    destroy: function () {
        Ext.Object.each(this.fieldButtons, function (fieldId, button) {
            if (button && !button.destroyed) {
                button.destroy();
            }
        });
        this.fieldButtons = {};
        this.callParent(arguments);
    } // <-- No comma after the last method
});
