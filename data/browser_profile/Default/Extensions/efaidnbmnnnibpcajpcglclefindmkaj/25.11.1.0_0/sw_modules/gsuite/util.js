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
export const getAccountSpecificRedirectUrl=(t,e,c)=>{let a="0";if(t)try{const e=new URL(t),c=e?.pathname?.match(/\/mail\/u\/(\d+)/);if(c&&c.length>1)a=c[1];else{const t=e?.searchParams?.get("authuser");t&&(a=t)}}catch(t){}return`${e}${c}u/${a}`};