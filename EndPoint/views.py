from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import requests
import json
from django.conf import settings
import environ


@api_view(['Post'])
def setupPayement(request):
    Paypal_Client_ID = 'AZd-N_p1KIwEBwZ_viHjaficWO551hVNQZbQ_uyktV3qQy9zB29hUJbqV__VJ--2BD6hxFwBu8_5yoGj'
    Paypal_Client_Key = 'EGI_cB2Bn40X9uj92IP2ewl-KcNJJQMqxDj0A2iTvAYEf_KDpiXPnfyAZ8UI3Hep6S1kJpEfXW_ga9zA'
    try:
        #first request to get accesstoken
        data = {
        'grant_type': 'client_credentials',
        }
        AccesTokenresponse = requests.post('https://api-m.sandbox.paypal.com/v1/oauth2/token', data=data, auth=(Paypal_Client_ID, Paypal_Client_Key))
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
        if 'links' in responsePayement and len(responsePayement['links']) >= 2:
            initUrl = responsePayement['links'][1]['href']
            return Response(json.dumps({'initUrl': initUrl}))
        else:
            return Response({'error': 'Invalid PayPal response'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['Post'])
def executepayement(request):
    Paypal_Client_ID = 'AZd-N_p1KIwEBwZ_viHjaficWO551hVNQZbQ_uyktV3qQy9zB29hUJbqV__VJ--2BD6hxFwBu8_5yoGj'
    Paypal_Client_Key = 'EGI_cB2Bn40X9uj92IP2ewl-KcNJJQMqxDj0A2iTvAYEf_KDpiXPnfyAZ8UI3Hep6S1kJpEfXW_ga9zA'
    try:
        requestBody = json.loads(request.body)
        json_data = {
        'payer_id': requestBody["payerId"],
        }
        executeUrl = 'https://api.sandbox.paypal.com/v1/payments/payment/' + requestBody["paymentId"] + '/execute'
        response = requests.post(
        executeUrl,
        json=json_data,
        auth=(Paypal_Client_ID, Paypal_Client_Key),
        )
        ResponseBody = json.loads(response.text)
        if 'state' in ResponseBody and ResponseBody['state'] == 'approved':
            return Response({'message': 'Payment executed successfully'})
        else:
            return Response({'error': 'Invalid PayPal response'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


   


