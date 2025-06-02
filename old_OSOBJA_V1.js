/*
 * Extensible framework on OSOBJS - Systems Screen
 * 01 OCT 2018 - Initial Coding: © 2018 21Tech, LLC
 */

var VINClass = ['BUS'];

function VINLabel(iFormPanel) {
	var vClass = iFormPanel.getFldValue('class');

	if (VINClass.indexOf(vClass) > -1) {
		iFormPanel.getForm().findField('serialnumber').setFieldLabel('VIN');
	} else {
		iFormPanel.getForm().findField('serialnumber').setFieldLabel('Serial Number');
		//vFormPanel.setFldValue('serialnumber','Populated by EF', true);
	};
};

function validateVIN(vin) {
	return validate(vin);

	function transliterate(c) {
		return '0123456789.ABCDEFGH..JKLMN.P.R..STUVWXYZ'.indexOf(c) % 10;
	}

	function get_check_digit(vin) {
		var map = '0123456789X';
		var weights = '8765432X098765432';
		var sum = 0;
		for (var i = 0; i < 17; ++i)
			sum += transliterate(vin[i]) * map.indexOf(weights[i]);
		return map[sum % 11];
	}

	function validate(vin) {
		if (vin.length !== 17) return false;
		return get_check_digit(vin) === vin[8];
	}
};

function VINStyle() {
	vVIN = document.getElementsByName('serialnumber');
	vVIN[0].removeAttribute('style');
	vVINvalue = document.getElementsByName('serialnumber')[0].value;
	vClass = document.getElementsByName('class')[0].value;

	if (VINClass.indexOf(vClass) > -1 && !validateVIN(vVINvalue)) {
		vVIN[0].style['background-color'] = 'pink';
	}
};

Ext.define('EAM.custom.external_osobja', {
	extend: 'EAM.custom.AbstractExtensibleFramework',
	getSelectors: function () {
		return {
			'[extensibleFramework] [tabName=HDR][isTabView=true]': {
				afterloaddata: function (field, lastValues) {
					vFormPanel = this.getFormPanel();
					VINLabel(vFormPanel);
					VINStyle();
				},
				afterrender: function (field, lastValues) {
					vFormPanel = this.getFormPanel();
					VINLabel(vFormPanel);
					VINStyle();
				},
				aftersaverecord: function (field, lastValues) {
					vFormPanel = this.getFormPanel();
					VINLabel(vFormPanel);
					VINStyle();
				}
			},
			'[extensibleFramework] [tabName=HDR][isTabView=true] [name=class]': {
				blur: function (field, lastValues) {
					vFormPanel = this.getFormPanel();
					VINLabel(vFormPanel);
					VINStyle();
				}
			},
			'[extensibleFramework] [tabName=HDR][isTabView=true] [name=serialnumber]': {
				blur: function (field, lastValues) {
					VINStyle();
				}
			}
		}
	}
});