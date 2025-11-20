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
import state from"./state.js";import{sendAnalytics,sendErrorLog}from"../utils/util.js";const IMPLICIT_TOAST_CONTAINER_ID="acrobat-gmail-implicit-toast-container",IMPLICIT_TOAST_CLOSE_BUTTON_ID="acrobat-gmail-implicit-toast-close",IMPLICIT_TOAST_CLOSE_ICON_ID="acrobat-gmail-implicit-toast-close-icon",IMPLICIT_TOAST_MESSAGE_ID="acrobat-gmail-implicit-toast-message",TOAST_AUTO_DISMISS_DELAY=5e3;let autoDismissTimeout=null,isToastShowing=!1;const removeImplicitToast=()=>{const t=document.getElementById(IMPLICIT_TOAST_CONTAINER_ID);t&&t.remove(),autoDismissTimeout&&(clearTimeout(autoDismissTimeout),autoDismissTimeout=null),isToastShowing=!1},addToastDismissListeners=t=>{const i=t.querySelector(`#${IMPLICIT_TOAST_CLOSE_BUTTON_ID}`);i?.addEventListener("click",()=>{removeImplicitToast(),sendAnalytics([["DCBrowserExt:Gmail:ImplicitDV:Toast:Dismissed"]])}),autoDismissTimeout=setTimeout(()=>{removeImplicitToast()},5e3)},setToastText=t=>{const i=t.querySelector(`#${IMPLICIT_TOAST_MESSAGE_ID}`);i&&(i.textContent=state?.gmailImplicitDefaultViewershipConfig?.toastMessage)},setToastIcons=t=>{const i=t.querySelector(`#${IMPLICIT_TOAST_CLOSE_ICON_ID}`);i&&(i.src=chrome.runtime.getURL("browser/images/SDC_Close_22_N.svg"))},addImplicitDefaultViewershipToast=async()=>{const t=document.createElement("div");t.id=IMPLICIT_TOAST_CONTAINER_ID;const i=await fetch(chrome.runtime.getURL("resources/gmail/implicit-toast.html")),s=await i.text();t.innerHTML=s,setToastIcons(t),setToastText(t),document.body.appendChild(t),addToastDismissListeners(t)},showImplicitDefaultViewershipToast=async()=>{try{if(isToastShowing)return;isToastShowing=!0,await addImplicitDefaultViewershipToast(),sendAnalytics([["DCBrowserExt:Gmail:ImplicitDV:Toast:Shown"]])}catch(t){isToastShowing=!1,sendErrorLog("GmailImplicitDV","Failure in showImplicitDefaultViewershipToast")}};export{showImplicitDefaultViewershipToast};