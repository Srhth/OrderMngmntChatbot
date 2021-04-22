from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, JsonResponse

from django.views.decorators.csrf import ensure_csrf_cookie
from django.template import loader

import json
import requests

from ibm_watson import AssistantV2, ApiException
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

from .models import *

def watson_assistant():
	authenticator = IAMAuthenticator("U0vlZq4sfvSDTCEM_QRFmlA7k7175LymwLDjV0heOFs9")
	assistant = AssistantV2(
		version="2021-02-09",
		authenticator=authenticator
	)
	assistant.set_service_url("https://api.kr-seo.assistant.watson.cloud.ibm.com")
	return assistant

def index(request):
    t = loader.get_template('ordermngmnt/orders/main.html')
    return HttpResponse(t.render({},request))

def secondPage(request):
	t = loader.get_template('ordermngmnt/orders/second.html')
	return HttpResponse(t.render({},request))

def show_results(request):
	t = loader.get_template('ordermngmnt/orders/results.html')
	return HttpResponse(t.render({},request))

#AUTHENTICATION
def authenticate_start_session(request):
	assistant=watson_assistant()
	#ASSISTANT ID
	request.session["asst_id"] = "158e9e4b-1430-4912-ab77-32f2aa28e4dc"
	request.session["promptSuggestion"]=False
	#STARTING THE SESSION
	print("Session starting")
	response = assistant.create_session(
		assistant_id = request.session.get("asst_id")
	).get_result()  
	session=(json.dumps(response, indent=2))
	#print(session)
	session=json.loads(session)
	request.session["watson_session_id"]=session["session_id"]
	return HttpResponse("Session started")

#SENDING INPUT TEXT TO ASSISTANT
#notes:session id and user id are same -
def get_response(request):
	input_text=request.POST['text']
	assistant=watson_assistant()
	promptSuggestion = request.session.get('promptSuggestion')
	if not promptSuggestion:
		try:
			response = assistant.message(
				assistant_id= request.session.get("asst_id"),
				session_id= request.session.get("watson_session_id"),
				input={
					'message_type': 'text',
					'text': input_text,
					'options': {
						'return_context': True
					}
				},
				context={
					'global': {
						'system': {
							'user_id': 'my_user_id'
						}
					},
					'skills': {
						'main skill': {
							'user_defined': {
								'account_number': '123456'
							}
						}
					}
				}
			).get_result()
		except ApiException as ex:
			if ex.message=="Invalid Session":
				return JsonResponse(ex.message, safe=False)
			return JsonResponse("Error "+str(ex.code)+"-"+ex.message, safe=False)
	else:
		request.session['promptSuggestion'] = False
		suggestions = request.session.get('suggestions')
		try:
			response = assistant.message(
				assistant_id= request.session.get("asst_id"),
				session_id= request.session.get("watson_session_id"),
				input= suggestions[str(int(input_text)-1)],
				context={
					'global': {
						'system': {
							'user_id': 'my_user_id'
						}
					},
					'skills': {
						'main skill': {
							'user_defined': {
								'account_number': '123456'
							}
						}
					}
				}
			).get_result()
		except ApiException as ex:
			if ex.message=="Invalid Session":
				return JsonResponse(ex.message, safe=False)
			return JsonResponse("Error "+str(ex.code)+"-"+ex.message, safe=False)

	asst_response=(json.dumps(response, indent=2))
	print(asst_response)
	asst_response=json.loads(asst_response)
	generic_response = asst_response["output"]["generic"][0]
	if generic_response["response_type"] == "text":
		confidence = None
		if asst_response["output"]["intents"]!=[]:
			confidence = asst_response["output"]["intents"][0]["confidence"]
			odata_response = None
			if asst_response["output"]["intents"][0]["intent"]=="yes":
				odata_response=trigger_db(asst_response)
				#request.session["tdata"]=response_data
				#print(odata_response)
		asst_response = asst_response["output"]["generic"]
		#print("CONFIDENCE", confidence)
		response=[]
		for i in asst_response:
			try:
				if i["text"] == "ODATA":
					response.append(odata_response)
				else:
					response.append(i["text"])
			except:
				for j in i["suggestions"][0]["output"]["generic"]:
					response.append(i["text"])
		#print("response", response)
		if confidence!=None:
			if confidence<0.7:
				print("inserting into QATABLE")
				print(add_exchange(input_text,response[0]))
		#print(response)
		return JsonResponse(response, safe=False)
	elif generic_response["response_type"]=="suggestion":
		response=[]
		response.append("I apologize, I need more clarity to help you.")
		response.append("Please input the option beside the query you require.")
		response.append(generic_response['title'])
		suggestions={}
		request.session['promptSuggestion']=True
		for i in range(len(generic_response['suggestions'])):
			current_suggestion = generic_response['suggestions'][i]
			response.append(str(i+1)+". "+current_suggestion['label'])
			suggestions[i]=current_suggestion['value']['input']
		request.session['suggestions']=suggestions
		return JsonResponse(response, safe=False)
	return JsonResponse("RESPONSE TYPE NOT SUPPORTED", safe=False)

#DELETING THE SESSION
def delete_session(request):
	assistant=watson_assistant()
	response = assistant.delete_session(
		assistant_id= request.session.get("asst_id"),
		session_id= request.session.get("watson_session_id")
	).get_result()
	return HttpResponse("Session clossed")
#-------------------------------------------------------------------

def add_exchange(umsg,bmsg):
	#dialogue=QATable.objects.create(question=umsg, answer=bmsg)
	#dialogue.save()
	return "Inserted"


def trigger_db(asst_response):
	headers_dict = {'Accept': 'application/json'}
	auth_cred = ('168932744', 'Kindergart0321!')
	odata_url="https://sapydlci.bhdev1.ibm.com:8885/sap/opu/odata/sap/ZYTMR_CHATBOT_QUERY_SRV/HWDBCombinedSet/?&$filter=(USER_ID eq '168932744' and "
	#odata_response = requests.get("https://sapydlci.bhdev1.ibm.com:8885/sap/opu/odata/sap/ZYTMR_CHATBOT_QUERY_SRV/HWDBCombinedSet/?&$filter=(USER_ID eq '168932744' and ZZY_QUOTE_ID_H eq '8500023230' and STATUS_NUMBER_H eq '0002')", auth = auth_cred, verify = False, headers = headers_dict)
	#print(odata_response.json())

	intent= asst_response["context"]["skills"]["main skill"]["user_defined"]["lastintent"]
	response_data = []

	if intent == "QUOTE_STATUS": #R1
		quoteno = asst_response["context"]["skills"]["main skill"]["user_defined"]["quoteno"]
		odata_response = requests.get(odata_url+"ZZY_QUOTE_ID_H eq '"+quoteno+"')", auth = auth_cred, verify = False, headers = headers_dict)
		#print(odata_response.url)
		odata_response = odata_response.json()
		odata_response = odata_response['d']['results']
		#print(odata_response)
		if odata_response != []:
			odata_response = odata_response[0]
			response_data = "For Quote No - " + quoteno + " - the status number is " +  odata_response['STATUS_NUMBER_H'] + " and the short status is " + odata_response['STATUS_SHORT_H'] + "."
		else:
			response_data = "There are no records with Quote No - " + quoteno 
		#qstatus = quotes.objects.filter(quote_id = quoteno).values_list('quote_status')
		#t_qstatus = list(zip(*qstatus))
		#print(t_qstatus)
		#t_qstatus = [odata_response['STATUS_NUMBER_H'], odata_response['STATUS_SHORT_H']]
	
	if intent == "ORDER_STATUS": #R1
		orderno = asst_response["context"]["skills"]["main skill"]["user_defined"]["orderno"]
		odata_response = requests.get(odata_url + "VBELN_H eq '" + orderno + "')", auth = auth_cred, verify = False, headers = headers_dict)
		#print(odata_response.url)
		odata_response = odata_response.json()
		odata_response = odata_response['d']['results']
		#print(odata_response)
		if odata_response != []:
			odata_response = odata_response[0]
			response_data = "For Order No - " + orderno + " - the status number is " +  odata_response['STATUS_NUMBER_H'] + " and the short status is " + odata_response['STATUS_SHORT_H'] 
		else:
			response_data = "There are no records with Order No - " + orderno 
			
	if intent == "QUOTE_COUNTRY": #R1
		quoteno = asst_response["context"]["skills"]["main skill"]["user_defined"]["quoteno"]
		#qcountry = quotes.objects.filter(quote_id = quoteno).values_list('quote_country','sales_office')
		odata_response = requests.get(odata_url+"ZZY_QUOTE_ID_H eq '"+quoteno+"')", auth = auth_cred, verify = False, headers = headers_dict)
		#print(odata_response.url)
		odata_response = odata_response.json()
		#print(odata_response)
		odata_response = odata_response['d']['results']
		#print(odata_response)
		if odata_response != []:
			odata_response = odata_response[0]
			#t_qcountry = list(zip(*qcountry))
			#print(t_qcountry)
			#t_qcountry = [odata_response['ZZY_VKBUR_DESC_H'], odata_response['LAND1_H'], odata_response['VKBUR_H']]
			response_data = "For Quote No - " + quoteno + " - the country is "+ odata_response['ZZY_VKBUR_DESC_H'] + " , the country code is " + odata_response['LAND1_H'] + " and the sales office number is " + odata_response['VKBUR_H'] + "."
		else:
			response_data = "There are no records with Quote No - " + quoteno 


	if intent == "ORDER_COUNTRY": #R1
		orderno = asst_response["context"]["skills"]["main skill"]["user_defined"]["orderno"]
		odata_response = requests.get(odata_url+"VBELN_H eq '"+str(orderno)+"')", auth = auth_cred, verify = False, headers = headers_dict)
		odata_response = odata_response.json()
		#t_ocountry = [odata_response['ZZY_VKBUR_DESC_H'], odata_response['LAND1_H'], odata_response['VKBUR_H']]
		odata_response = odata_response['d']['results']
		#print(odata_response)
		if odata_response != []:
			odata_response = odata_response[0]
			response_data = "For Order No - " + orderno + " - the country is "+ odata_response['ZZY_VKBUR_DESC_H'] + " , the country code is " + odata_response['LAND1_H'] + " and the sales office number is " + odata_response['VKBUR_H'] + "."
		else:
			response_data = "There are no records with Order No - " + quoteno 

	if intent == "QUOTE_TRACK": #R1
		quoteno = asst_response["context"]["skills"]["main skill"]["user_defined"]["quoteno"]
		odata_response = requests.get(odata_url+"ZZY_QUOTE_ID_H eq '"+quoteno+"')", auth = auth_cred, verify = False, headers = headers_dict)
		odata_response = odata_response.json()
		odata_response = odata_response['d']['results']
		if odata_response != []:
			odata_response = odata_response[0]
			response_data = "Quote No - " + quoteno + " ; Sold-to = " + odata_response['ZZY_CUST_NAME_H'] + "; End User = " + odata_response["ZZY_END_CUST_H"] + " ; Status = " + odata_response["STATUS_SHORT_H"] + "; CRM Status = " + odata_response["ZZY_CRM_STATUS_H"] + " ; FOP Status = " + odata_response["ZZY_FOP_STATUS_H"] + "; Create Date = " + odata_response["ZZY_DOC_CREATE_DATE_H"] + "; CRAD = " + odata_response["CRAD_H"] + "; Quoted Price = " + odata_response["ZZY_QUOTE_PRICE_H"] + " " + odata_response["WAERK_H"] + "; Squad Name = " + odata_response["ZZY_IGFTCFNM_URL_H"] + "; User = " + odata_response["ZZY_BID_MANAGER_H"]
		else:
			response_data = "There are no records with Quote No - " + quoteno 
		#t_qtrack = [odata_response['ZZY_CUST_NAME_H'], odata_response['ZZY_END_CUST_H'], odata_response['STATUS_SHORT_H'], odata_response['ZZY_CRM_STATUS_H'], odata_response['ZZY_FOP_STATUS_H'], odata_response['ZZY_DOC_CREATE_DATE'], odata_response['CRAD_H'], odata_response['ZZY_QUOTE_PRICE_H'], odata_response['WAERK_H'], odata_response['ZZY_IGFTCFNM_URL_H'], odata_response['ZZY_BID_MANAGER']]

	if intent == "ORDER_TRACK": #R1
		orderno = asst_response["context"]["skills"]["main skill"]["user_defined"]["orderno"]
		odata_response = requests.get(odata_url + "VBELN_H eq '" + orderno + "')", auth = auth_cred, verify = False, headers = headers_dict)
		odata_response = odata_response.json()
		odata_response = odata_response['d']['results']
		if odata_response != []:
			odata_response = odata_response[0]
			response_data = "Sales Order No - " + orderno + " ; Sold-to = " + odata_response['ZZY_CUST_NAME_H'] + "; End User = " + odata_response["ZZY_END_CUST_H"] + " ; Status = " + odata_response["STATUS_SHORT_H"] + "; Create Date = " + odata_response["ZZY_DOC_CREATE_DATE_H"] + "; CRAD = " + odata_response["CRAD_H"] + "; Quoted Price = " + odata_response["ZZY_QUOTE_PRICE_H"] + " " + odata_response["WAERK_H"] + "; Squad Name = " + odata_response["ZZY_IGFTCFNM_URL_H"] + "; User = " + odata_response["ZZY_BID_MANAGER_H"]
		else:
			response_data = "There are no records with Order No - " + orderno 

	if intent == "EPRICER_PO": #R1
		epricerid = asst_response["context"]["skills"]["main skill"]["user_defined"]["epricerid"]
		odata_response = requests.get(odata_url + "ZZY_EPRICR_QTID_H eq '" + epricerid + "')", auth = auth_cred, verify = False, headers = headers_dict)
		odata_response = odata_response.json()
		odata_response = odata_response['d']['results']
		if odata_response != []:
			odata_response = odata_response[0]
			response_data = "The PO (Purchase Order) that belongs to ePricer ID - " + epricerid + " is " + odata_response["ZZY_EXT_REF_H"] 
		else:
			response_data = "There are no records with ePricer ID - " + epricerid 

	if intent == "PLNTORDER_ORDER": #R1
		pono = asst_response["context"]["skills"]["main skill"]["user_defined"]["pono"]
		odata_response = requests.get(odata_url + "ZZFV_PLTORD_I eq '" + pono + "')", auth = auth_cred, verify = False, headers = headers_dict)
		odata_response = odata_response.json()
		#print(odata_response)
		odata_response = odata_response['d']['results']
		if odata_response != []:
			odata_response = odata_response[0]
			if odata_response["ZZY_QUOTE_ID_H"] == "":
				response_data = "The Sales Order to which Plant Order " + pono + " belongs is " + odata_response["VBELN_H"]
			elif odata_response["VBELN_H"] == "":
				response_data =  "The Quote to which Plant Order " + pono + " belongs is " + odata_response["ZZY_QUOTE_ID_H"]
			else:
				response_data =  "The Sales Order and Quote to which Plant Order " + pono + " belongs are " + odata_response["VBELN_H"] + " and " + odata_response["ZZY_QUOTE_ID_H"]
		else:
			response_data = "There is no Sales Order or Quote related to Plant Order No - " + pono 

	if intent == "ORDER_EPRICER": #R1
		oqno = asst_response["context"]["skills"]["main skill"]["user_defined"]["oqno"]
		etype = asst_response["context"]["skills"]["main skill"]["user_defined"]["etype"]
		#print(oqno, etype)
		if etype == "Quote":
			odata_response = requests.get(odata_url + "ZZY_QUOTE_ID_H eq '" + oqno + "')", auth = auth_cred, verify = False, headers = headers_dict)
			odata_response = odata_response.json()
			#print(odata_response)
			odata_response = odata_response['d']['results']
			if odata_response != []:
				odata_response = odata_response[0]
				response_data =  "The ePricer ID for Quote Number " + oqno + " is " + odata_response["ZZY_EPRICR_QTID_H"] 
			else:
				response_data = "There is no ePricer ID related to Quote number " + oqno
		elif etype == "Order":
			odata_response = requests.get(odata_url + "VBELN_H eq '" + oqno + "')", auth = auth_cred, verify = False, headers = headers_dict)
			odata_response = odata_response.json()
			#print(odata_response)
			odata_response = odata_response['d']['results']
			if odata_response != []:
				odata_response = odata_response[0]
				response_data =  "The ePricer ID for Order Number " + oqno + " is " + odata_response["ZZY_EPRICR_QTID_H"] 
			else:
				response_data = "There is no ePricer ID related to Order number " + oqno
		else:
			response_data = "There is no ePricer ID for the inputted ID - " + oqno

	if intent == "PLNTORDER_INV": #R1
		pono = asst_response["context"]["skills"]["main skill"]["user_defined"]["pono"]
		odata_response = requests.get(odata_url + "ZZFV_PLTORD_I eq '" + pono + "')", auth = auth_cred, verify = False, headers = headers_dict)
		odata_response = odata_response.json()
		odata_response = odata_response['d']['results']
		if odata_response != []:
			odata_response = odata_response[0]
			response_data = "The Invoice related to Plant Order ID - " + pono + " is " + odata_response["ZZY_INVOICE_I"] 
		else:
			response_data = "There are no records with Plant order Number - " + pono 

	if intent == "INV_ORDER": #R1
		invoiceno = asst_response["context"]["skills"]["main skill"]["user_defined"]["invoiceno"]
		odata_response = requests.get(odata_url + "ZZY_INVOICE_I eq '" + invoiceno + "')", auth = auth_cred, verify = False, headers = headers_dict)
		odata_response = odata_response.json()
		odata_response = odata_response['d']['results']
		if odata_response != []:
			odata_response = odata_response[0]
			response_data = "The Order Number that belongs to Invoice ID - " + invoiceno + " is " + odata_response["VBELN_H"] 
		else:
			response_data = "There are no records with Invoice ID - " + invoiceno 

	#if intent == "TRANS_OWNER": #R1
	#	transno = asst_response["context"]["skills"]["main skill"]["user_defined"]["transno"]
	#	transuser = transactions.objects.filter(transaction_id = transno).values_list('user')
	#	t_transuser = list(zip(*transuser))
	#	print(t_transuser)
	#	response_data = t_transuser[0]

	if intent == "FOP_STATUS_ORDER": #R1 
		quoteno = asst_response["context"]["skills"]["main skill"]["user_defined"]["quoteno"]
		odata_response = requests.get(odata_url + "ZZY_QUOTE_ID_H eq '" + quoteno + "')", auth = auth_cred, verify = False, headers = headers_dict)
		odata_response = odata_response.json()
		odata_response = odata_response['d']['results']
		if odata_response != []:
			odata_response = odata_response[0]
			response_data = "The FOP Status for Quote ID - " + quoteno + " is " + odata_response["ZZY_FOP_STATUS_H"] 
		else:
			response_data = "There are no records with Quote ID - " + quoteno 

	if intent == "CRM_STATUS_ORDER": #R1 
		quoteno = asst_response["context"]["skills"]["main skill"]["user_defined"]["quoteno"]
		odata_response = requests.get(odata_url + "ZZY_QUOTE_ID_H eq '" + quoteno + "')", auth = auth_cred, verify = False, headers = headers_dict)
		odata_response = odata_response.json()
		odata_response = odata_response['d']['results']
		if odata_response != []:
			odata_response = odata_response[0]
			response_data = "The CRM Status for Quote ID - " + quoteno + " is " + odata_response["ZZY_CRM_STATUS_H"] 
		else:
			response_data = "There are no records with Quote ID - " + quoteno 

	if intent == "INV_PO": #R1
		invoiceno = asst_response["context"]["skills"]["main skill"]["user_defined"]["invoiceno"]
		odata_response = requests.get(odata_url + "ZZY_INVOICE_I eq '" + invoiceno + "')", auth = auth_cred, verify = False, headers = headers_dict)
		odata_response = odata_response.json()
		odata_response = odata_response['d']['results']
		if odata_response != []:
			odata_response = odata_response[0]
			response_data = "The Purchase Order for Invoice ID - " + invoiceno + " is " + odata_response["ZZY_EXT_REF_H"] 
		else:
			response_data = "There are no records with Invoice ID - " + invoiceno

	if intent == "PLNTORDER_EPRICER": #R1
		pono = asst_response["context"]["skills"]["main skill"]["user_defined"]["pono"]
		odata_response = requests.get(odata_url + "ZZFV_PLTORD_I eq '" + pono + "')", auth = auth_cred, verify = False, headers = headers_dict)
		odata_response = odata_response.json()
		odata_response = odata_response['d']['results']
		if odata_response != []:
			odata_response = odata_response[0]
			response_data = "The ePricer ID which belongs to Plant Order" + pono + "based on the Quote / Sales Order it is associated with" + odata_response["ZZY_EPRICR_QTID_H"] 
		else:
			response_data = "There are no records with Plant order Number - " + pono 

	
	return response_data


