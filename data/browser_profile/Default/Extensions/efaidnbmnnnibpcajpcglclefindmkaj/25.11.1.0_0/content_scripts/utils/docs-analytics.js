/*************************************************************************
* ADOBE CONFIDENTIAL
* ___________________
*
*  Copyright 2015 Adobe Systems Incorporated
*  All Rights Reserved.
*
* NOTICE:  All information contained herein is, and remains
* the property of Adobe Systems Incorporated and its suppliers,
* if any.  The intellectual and technical concepts contained
* herein are proprietary to Adobe Systems Incorporated and its
* suppliers and are protected by all applicable intellectual property laws,
* including trade secret and or copyright laws.
* Dissemination of this information or reproduction of this material
* is strictly forbidden unless prior written permission is obtained
* from Adobe Systems Incorporated.
**************************************************************************/
let utils;(async()=>{try{if(!await chrome.runtime.sendMessage({main_op:"getFloodgateFlag",flag:"dc-cv-docs-analytics-visited"}))return;utils||(utils=await import(chrome.runtime.getURL("content_scripts/utils/util.js")));const{pathname:t}=window.location;let s=null;if(t.startsWith("/document/")?s="Document":t.startsWith("/spreadsheets/")?s="Spreadsheet":t.startsWith("/presentation/")&&(s="Presentation"),!s)return;const e=`DCBrowserExt:DocsGoogle:Visited:${s}`;utils?.isAnalyticsSentInTheMonthOrSession(e)||utils?.sendAnalyticsOncePerMonth(e)}catch(t){utils?.sendErrorLog("Docs analytics error",t)}})();