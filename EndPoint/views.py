from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import requests
import json
from django.views.decorators.csrf import csrf_exempt

@api_view(['Post'])
def setupPayement(request):
    #first request to get accesstoken
    data = {
    'grant_type': 'client_credentials',
    }
    AccesTokenresponse = requests.post('https://api-m.sandbox.paypal.com/v1/oauth2/token', data=data, auth=('AZd-N_p1KIwEBwZ_viHjaficWO551hVNQZbQ_uyktV3qQy9zB29hUJbqV__VJ--2BD6hxFwBu8_5yoGj', 'EGI_cB2Bn40X9uj92IP2ewl-KcNJJQMqxDj0A2iTvAYEf_KDpiXPnfyAZ8UI3Hep6S1kJpEfXW_ga9zA'))
    responseToken = json.loads(AccesTokenresponse.text)
    token_type = responseToken["token_type"]
    access_token = responseToken["access_token"]
    #second request to get url for payement
    RequestBody =  json.loads(request.body)
    payement = {
          "intent": "sale",
          "payer": {
             "payment_method": "paypal"
          },
          "transactions": [
              {
                 "amount": {
                      "total": RequestBody["price"],
                      "currency": "USD"
                  },
                  "description": "Payment description"
              }
          ],
          "redirect_urls": {
              "return_url": "http://localhost:3000/success",
              "cancel_url": "http://localhost:3000/cancel"
          }
        }
    headers = {
         'Content-Type': 'application/json',
         'Authorization': f'Bearer {access_token}'
     }

    Payementresponse = requests.post('https://api-m.sandbox.paypal.com/v1/payments/payment', headers=headers,json=payement)
    responsePayement = json.loads(Payementresponse.text)
    ResponseBody = {
     'initUrl' : responsePayement["links"][1]["href"]
    }
    return Response(json.dumps(ResponseBody))

@csrf_exempt
@api_view(['Post'])
def executepayement(request):
    
    requestBody = json.loads(request.body)
    json_data = {
    'payer_id': requestBody["payerId"],
    }
    executeUrl = 'https://api.sandbox.paypal.com/v1/payments/payment/' + requestBody["paymentId"] + '/execute'
    response = requests.post(
    executeUrl,
    json=json_data,
    auth=('AZd-N_p1KIwEBwZ_viHjaficWO551hVNQZbQ_uyktV3qQy9zB29hUJbqV__VJ--2BD6hxFwBu8_5yoGj', 'EGI_cB2Bn40X9uj92IP2ewl-KcNJJQMqxDj0A2iTvAYEf_KDpiXPnfyAZ8UI3Hep6S1kJpEfXW_ga9zA')
    )
    return Response(json.loads(response.text))

@csrf_exempt
@api_view(['Post'])
def testing(request):

    return Response("heelo")
   


