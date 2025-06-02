Ext.define('tech.custom.AjaxInterceptor', {
	//--@MMostafa -- 3/31/2025
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

Ext.define('EAM.custom.external_OSOBJA', {
	extend: 'EAM.custom.AbstractExtensibleFramework',

	getSelectors: function () {
		var vG = this;
		//--@MMostafa -- 3/31/2025
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
		interceptor.registerInterceptor('OSOBJA.DOC', {
			conditionFn: function (b) {
				debugger;
				return true;
			},
			injectFn: function (req) {
				// check what's the pattern in the url params to inject
				if (req && req.params && req.url == "BSUPLD.checkfile") {
					// send a request to the server to check the file
					// and include the cookey from the browser in the request
					var cookie = document.cookie;
					var fileName = req.params.fileName;
					var eamid = EAM.SessionStorage.getEamId();
					var tenant = EAM.SessionStorage.getTenant();
					var doccode = req.params.documentcode;

					// print all
					console.log('cookie', cookie);
					console.log('fileName', fileName);
					console.log('eamid', eamid);
					console.log('doccode', doccode);
					console.log('tenant', tenant);

					// the name of the document must have a certain document code
					// to be uploaded to the server
					if (doccode != 'MAIN-DOC') {
						return true;
					}
					// send the request to the server
					url = "http://localhost:8080/BSUPLD/checkfile";
					// the URL to send the request to
					var params = {
						fileName: fileName,
						eamid: eamid,
						doccode: doccode
					};
					// send the request to the server
					EAM.data.Ajax.request({
						url: url,
						method: 'POST',
						params: params,
						headers: {
							'Content-Type': 'application/json',
							'Cookie': cookie
						},
						success: function (response) {
							console.log('Success', response);
						},
						failure: function (response) {
							console.log('Failure', response);
						}
					});
				}
				return true;
			},
			successFn: function (respSuccess, resp, respData) {
				debugger;
				var url = resp.request.url;
			}
		});

		var selectors = {
			'[extensibleFramework] [tabName=DOC][isTabView=true]': {
				customonblur: function () {
					console.log('HI');
				}
			}
		};
		return selectors;
	}

});