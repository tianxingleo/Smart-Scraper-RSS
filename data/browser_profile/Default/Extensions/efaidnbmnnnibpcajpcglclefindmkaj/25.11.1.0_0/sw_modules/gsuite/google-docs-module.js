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
import{viewerModuleUtils as o}from"../viewer-module-utils.js";import{dcLocalStorage as t}from"../../common/local-storage.js";import{util as e}from"../util.js";import{floodgate as n}from"../floodgate.js";import{loggingApi as a}from"../../common/loggingApi.js";import{removeExperimentCodeForAnalytics as r,setExperimentCodeForAnalytics as c}from"../../common/experimentUtils.js";const i=o=>{try{return JSON.parse(n.getFeatureMeta(o))}catch(t){return a.error({context:"Google Docs",message:`Failure in parsing FeatureFlag ${o}`,error:t.message||t.toString()}),{validPaths:["document","spreadsheets","presentation"],selectors:{touchPointContainer:["docs-titlebar-buttons"],docTitle:["docs-title-input"]}}}},s=({isEnLocaleEnabled:o,isNonEnLocaleEnabled:e})=>{const n="en-US"===t.getItem("locale")||"en-GB"===t.getItem("locale");return n&&o||!n&&e};async function l(a,l,g){await o.initializeViewerVariables(g);const m="false"===t.getItem("acrobat-touch-points-in-other-surfaces"),u=await n.hasFlag("dc-cv-google-docs-convert-to-pdf-touch-point"),d=await n.hasFlag("dc-cv-google-docs-convert-to-pdf-touch-point-control"),p=u&&i("dc-cv-google-docs-convert-to-pdf-touch-point"),T=d&&i("dc-cv-google-docs-convert-to-pdf-touch-point-control"),f=s(p)&&!m&&u,h=s(T)&&!m&&d;f?(c("GDCT"),r("GDCC")):h&&(c("GDCC"),r("GDCT"));const v=e.getTranslation("gmailConvertToPdf"),F=e.getTranslation("convertToPDFTouchPointTooltip"),P={enableGoogleDocsConvertToPDFTouchPoint:f,...p,text:{acrobatTouchPointTooltip:F,acrobatTouchPointText:v}};a?.surfaceNameTranslationKey&&(P.text.touchPointFTE={title:e.getTranslation("convertToPDFFTEHeading"),description:e.getTranslation("convertToPDFFTEBody",e.getTranslation(a?.surfaceNameTranslationKey)),button:e.getTranslation("closeButton")}),l(P)}export{l as googleDocsInit};