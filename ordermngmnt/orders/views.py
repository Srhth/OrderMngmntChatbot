from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.template import loader

import json
from ibm_watson import AssistantV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator


def watson_assistant():
	authenticator = IAMAuthenticator("U0vlZq4sfvSDTCEM_QRFmlA7k7175LymwLDjV0heOFs9")
	assistant = AssistantV2(
		version="2021-02-09",
		authenticator=authenticator
	)
	assistant.set_service_url("https://api.kr-seo.assistant.watson.cloud.ibm.com")
	#ASSISTANT ID
	return assistant

def index(request):
    t = loader.get_template('ordermngmnt/orders/main.html')
    return HttpResponse(t.render({},request))

#AUTHENTICATION
def authenticate_start_session(request):
	assistant=watson_assistant()
	#ASSISTANT ID
	request.session["asst_id"]= "158e9e4b-1430-4912-ab77-32f2aa28e4dc"
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

	asst_response=(json.dumps(response, indent=2))
	print(asst_response)
	asst_response=json.loads(asst_response)
	asst_response = asst_response["output"]["generic"]
	response=""
	for i in asst_response:
		response+=" \n " + i["text"]

	return HttpResponse(response)

#DELETING THE SESSION
def delete_session(request):
	assistant=watson_assistant()
	response = assistant.delete_session(
		assistant_id= request.session.get("asst_id"),
		session_id= request.session.get("watson_session_id")
	).get_result()
	return HttpResponse("Session clossed")
      
