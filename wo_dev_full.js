//-- current config 
/* 
   11/08/2024 nikhil.deshmukh@21tech.com - Make fields required based on Dept, WO type and Equipment type
   11/21/2024 nikhil.deshmukh@21tech.com - Raise error to book labor/hours for activities 
   01/10/2025 hugo - updated to handle all changes in a function and to handle Track Sections
   02/24/2025 lucky.djomo@21tech.com - Override the built-in calibration report with a custom report
*/

//* to cop
Ext.define('tech.custom.AjaxInterceptor', {
	//--@lucky -- 2/24/2025
	interceptors: new Ext.util.HashMap(),
	doIntercept: function (req) {
		debugger;
		var keys = this.interceptors.getKeys();
		for (i = 0; i < keys.length; i++) {
			//invoke the condition function
			if (this.interceptors.get([keys[i]])['conditionFn'](req)) {
				if (typeof this.interceptors.get([keys[i]])['injectFn'] === 'function') {
					this.interceptors.get([keys[i]])['injectFn'](req);
				}
				if (typeof this.interceptors.get([keys[i]])['successFn'] === 'function') {
					if (req.onSuccess) {
						//set the onSuccess interceptor and break
						req.onSuccess = Ext.Function.createInterceptor(req.onSuccess, this.interceptors.get([keys[i]])['successFn']);
					} else {
						//set the onSuccess method directly and break
						req.onSuccess = this.interceptors.get([keys[i]])['successFn'];
					}
					break;
				}
			}
		}
	},
	registerInterceptor: function (key, fns) {
		//verify functions are defined in Object
		if (fns && typeof fns.conditionFn === 'function' && (typeof fns.successFn === 'function' || typeof fns.injectFn === 'function')) {
			this.interceptors.replace(key, fns);
		} else {
			console.log('Interceptor registration failed', [key, fns]);
		}
	}
});

Ext.define('EAM.custom.external_WSJOBS', {
	extend: 'EAM.custom.AbstractExtensibleFramework',

	getSelectors: function () {
		var vG = this;
		//--@lucky -- 2/24/2025
		vG.ExtSrvcByEQ = [];
		if (!window.console) {
			window.console = {
				log: function () { }
			};
		}
		var appData = EAM.AppData.getAppData();
		if (!appData.interceptor) {
			appData.interceptor = new tech.custom.AjaxInterceptor();
			EAM.data.Ajax.request = Ext.Function.createInterceptor(EAM.Ajax.request, appData.interceptor.doIntercept, appData.interceptor);
		}
		var interceptor = appData.interceptor;
		interceptor.registerInterceptor('WSJOBS.ETP', {
			conditionFn: function (b) {
				debugger;
				return ((b.url.indexOf("COGWEB") > -1) && (b.params.reportname === "WZCALR") && b.url.indexOf("pageaction") == -1);
			},
			injectFn: function (req) {
				if (req && req.params && req.url === "COGWEB" && req.params.reportname === "WZCALR") {
					var currentTab = EAM.Utils.getCurrentTab();
					if (currentTab) {
						debugger;
						req.params.reportname = "WZNLFD";
						req.params.USER_FUNCTION_NAME = "WZNLFD";
					}
				}
				return true;
			},
			successFn: function (respSuccess, resp, respData) {
				debugger;
				var url = resp.request.url;
			}
		});
		
		interceptor.registerInterceptor('BSUPLD.CAPTURE', {
			// Variable to store the captured request data
			capturedRequestData: null,
			
			// Check if the request URL contains BSUPLD.upload
			conditionFn: function (req) {
				return (req.url.indexOf("BSUPLD.upload") > -1);
			},
			
			// Extract and save all request data
			injectFn: function (req) {
				// Store a copy of the complete request data
				this.capturedRequestData = Ext.clone(req);
				console.log('BSUPLD.upload request intercepted:', this.capturedRequestData);
				
				// You can access the stored data through appData.interceptor.interceptors.get('BSUPLD.CAPTURE').capturedRequestData
				
				// Let the request proceed normally
				return true;
			},
			
			// Optional: process the response if needed
			successFn: function (respSuccess, resp, respData) {
				console.log('BSUPLD.upload response received:', resp);
			}
		});
		
		var selectors = {
			'[extensibleFramework] [tabName=HDR][isTabView=true] [name=department]': {
				customonblur: function () {
					console.log('department custom on blur');
					vG.FuncUpdateUI();
				}
			},
			'[extensibleFramework] [tabName=HDR][isTabView=true] [name=fromrefdesc]': {
				blur: function () {
					console.log('fromrefdesc on blur');
					vG.FuncUpdateUI();
				}
			},
			'[extensibleFramework] [tabName=HDR][isTabView=true] [name=torefdesc]': {
				blur: function () {
					console.log('torefdesc on blur');
					vG.FuncUpdateUI();
				}
			},
			'[extensibleFramework] [tabName=HDR][isTabView=true] [name=fromreferencepoint]': {
				customonblur: function () {
					console.log('fromreferencepoint on blur');
					vG.FuncUpdateUI();
				}
			},
			'[extensibleFramework] [tabName=HDR][isTabView=true] [name=toreferencepoint]': {
				customonblur: function () {
					console.log('toreferencepoint on blur');
					vG.FuncUpdateUI();
				}
			},
			'[extensibleFramework] [tabName=HDR][isTabView=true] uxcombobox[name=workorderstatus]': {
				select: async function () {
					try {
						var vFormPanel = EAM.Utils.getCurrentTab().getFormPanel(),
							vWoType = vFormPanel.getFldValue("workorderrtype"),
							vWoType2 = vFormPanel.getFldValue("workordertype");
						var vWStatus = vFormPanel.getFldValue("workorderstatus");
						var vWAct = vFormPanel.getFldValue("activity");
						var vErrMsg = "A Booked Labor Record is Required on this Work Order.";
						var vIncludedUser = ['TECHNICIAN', 'MNTTECHNOLOG', 'SYSTECH10', 'SERVICEPER', 'SYSADMIN'];
						var userGroup = vG.FuncUserGroup(EAM.AppData.getInstallParams().get('dbname'));
						console.log('Current user group: '.concat(userGroup));
						if (vWStatus == 'WC' && !Ext.isEmpty(vWAct) && Ext.Array.contains(vIncludedUser, userGroup)) {
							var vWCode = vFormPanel.getFldValue("workordernum");
							var vWOrg = vFormPanel.getFldValue("organization");
							var vCount = await vG.function2(vWCode, vWOrg, vWoType);
							var gridData = await vG.function4(vWCode, vWOrg, vWoType);
							var hireFound = false;
							//console.log('IN');
							for (var i = 0; i < gridData.length; i++) {
								if (gridData[i].hired == -1) {
									hireFound = true;
									break;
								}
							}
							if (vCount == 0 && hireFound == false) {
								EAM.Messaging.showError({
									msg: vErrMsg
								});

								//vFormPanel.reset();
								vFormPanel.getForm().findField('workorderstatus').reset();
								return false;
							}


						}

					} catch (error) {
						console.error('Error making fields required:', error);
					}
				}
			},
			'[extensibleFramework] [tabName=HDR][isTabView=true]': {
				afterloaddata: function () {
					console.log('After load data');
					vG.FuncUpdateUI();
				},
				afterrecordchange: function () {
					console.log('After record change');
					vG.FuncUpdateUI();
				},
				beforesaverecord: function () {
					console.log('Before save record');
					vG.FuncUpdateUI();
				},
				before_eam_beforesaverecord: function () {
					console.log('Before EAM before save record');
					vG.FuncUpdateUI();
				}
			},
			//--@lucky -- 2/24/2025
			'[extensibleFramework] [tabName=ETP][isTabView=true] [action=runcalibreport]': {
				click: function (event, btn) {
					debugger;
					console.log('Run Custom Calibration Report ...');
					return false;
				}
			}
		};
		return selectors;
	},
	//-- functions definitions --
	function2: function (vWCode, vWOrg, vWType) {
		var vResponse = EAM.Ajax.request({
			url: "WSJOBS.BOO",
			params: {
				SYSTEM_FUNCTION_NAME: 'WSJOBS',
				USER_FUNCTION_NAME: 'WSJOBS',
				CURRENT_TAB_NAME: 'BOO',
				workordernum: vWCode,
				organization: vWOrg,
				workorderrtype: vWType
			},
			async: false,
			method: "POST"
		});
		var vGridResult = vResponse.responseData.pageData.grid.GRIDRESULT.GRID.DATA.length;
		return vGridResult;
	},
	function4: function (vWCode, vWOrg, vWType) {
		var vResponse = EAM.Ajax.request({
			url: "WSJOBS.ACT",
			params: {
				SYSTEM_FUNCTION_NAME: 'WSJOBS',
				USER_FUNCTION_NAME: 'WSJOBS',
				CURRENT_TAB_NAME: 'ACT',
				workordernum: vWCode,
				organization: vWOrg,
				workorderrtype: vWType
			},
			async: false,
			method: "POST"
		});
		var vGridResult = vResponse.responseData.pageData.grid.GRIDRESULT.GRID.DATA;
		return vGridResult;
	},
	FuncUserGroup: function (inputString) {
		var openParenIndex = inputString.indexOf('(');
		var usergroup = inputString.substring(openParenIndex + 1, inputString.length - 1).trim();
		return usergroup;
	},
	FuncUpdateUI: function () {
		console.log('FuncUpdateUI');
		try {
			var vFormPanel = EAM.Utils.getCurrentTab().getFormPanel(),
				vDept = vFormPanel.getFldValue("department"),
				//vEqType = vFormPanel.getFldValue("equipmenttype"),
				vWoType = vFormPanel.getFldValue("workorderrtype"),
				vWoType2 = vFormPanel.getFldValue("workordertype"),
				vEqLen = vFormPanel.getFldValue("equipmentlength"),
				//vLinUom = vFormPanel.getFldValue("linearreferenceuom"),
				vExcludedTypes = ['PM', 'RP', 'IS', 'MEC', 'CAL'],
				vFromRefDesc = vFormPanel.getFldValue("fromrefdesc"),
				vToRefDesc = vFormPanel.getFldValue("torefdesc"),
				vWCode = vFormPanel.getFldValue("workordernum"),
				vFldBtn = vFormPanel.getForm().getFieldsAndButtons();
			console.log('CustomOnBlur: '.concat(vWCode));
			if (vWoType2 != 'CAL') {
				if (!Ext.Array.contains(vExcludedTypes, vWoType)) {
					if (!Ext.isEmpty(vEqLen)) {
						if (!Ext.isEmpty(vDept) && vDept == 'RA' && vWCode == '<Auto-Generated>' && Ext.isEmpty(vFromRefDesc) && Ext.isEmpty(vToRefDesc)) {
							EAM.Builder.setFieldState({
								'fromreferencepoint': 'required'
							}, vFldBtn);
							EAM.Builder.setFieldState({
								'toreferencepoint': 'required'
							}, vFldBtn);
						} else {
							EAM.Builder.setFieldState({
								'fromreferencepoint': 'optional'
							}, vFldBtn);
							EAM.Builder.setFieldState({
								'toreferencepoint': 'optional'
							}, vFldBtn);

							vFormPanel.getForm().clearInvalid();
						}
					}
				}
			}

		} catch (error) {
			console.error('Error making fields required:', error);
		}
	}

});