from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import requests
import json
from django.conf import settings
import environ
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime
if not firebase_admin._apps:
    # Initialize Firebase with your credentials JSON file
    cred = credentials.Certificate('C:\TechTaskFullApp\PaypalAPI\MyPaypal\EndPoint\ServiceAccount.json')
    firebase_admin.initialize_app(cred)

# Get a reference to the Firestore database
db = firestore.client()
Paypal_Client_ID = 'AZd-N_p1KIwEBwZ_viHjaficWO551hVNQZbQ_uyktV3qQy9zB29hUJbqV__VJ--2BD6hxFwBu8_5yoGj'
Paypal_Client_Key = 'EGI_cB2Bn40X9uj92IP2ewl-KcNJJQMqxDj0A2iTvAYEf_KDpiXPnfyAZ8UI3Hep6S1kJpEfXW_ga9zA'
def add_data_to_firestore(collection_name, data):
    doc_ref = db.collection(collection_name).document()
    doc_ref.set(data)

@api_view(['Post'])
def setupPayement(request):
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
            "intent": "Sale",
            
            
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
        print(responsePayement)
        ResponseBody = {
        'initUrl' : responsePayement["links"][1]["href"]
        }
        if 'links' in responsePayement and len(responsePayement['links']) >= 2:
            initUrl = responsePayement['links'][1]['href']
            #return Response(json.dumps({'initUrl': initUrl}))
            return Response(Payementresponse.json())
        else:
            return Response({'error': 'Invalid PayPal response'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['Post'])
def executepayement(request):
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
        
        #if 'state' in ResponseBody and ResponseBody['state'] == 'approved':
        if response.ok and ResponseBody['state'] == 'approved' :
            PluginId = requestBody['PluginId']
            AccountEmail = requestBody['Accountemail']
            PayementEmail = ResponseBody['payer']['payer_info']['email']
            TotalPrice = ResponseBody['transactions'][0]['amount']['total']
            Currency = ResponseBody['transactions'][0]['amount']['currency']
            PayementId = ResponseBody['id']
            PayementFee = ResponseBody['transactions'][0]['related_resources'][0]['sale']['transaction_fee']['value']
            ExchangeRate = ResponseBody['transactions'][0]['related_resources'][0]['sale']['exchange_rate']
            AmountReceived = ResponseBody['transactions'][0]['related_resources'][0]['sale']['receivable_amount']['value']
            AmountReceivedCurrency = ResponseBody['transactions'][0]['related_resources'][0]['sale']['receivable_amount']['currency']
            PayementData = {
                'PluginId' : PluginId,
                'AccountEmail' : AccountEmail,
                'PayementEmail' : PayementEmail,
                'TotalPrice' : TotalPrice,
                'Currency' : Currency,
                'PayementID' : PayementId,
                'PayementFee' : PayementFee,
                'ExchangeRate' : ExchangeRate,
                'AmountReceived' : AmountReceived,
                'AmountReceivedCurrency' : AmountReceivedCurrency

            }
            add_data_to_firestore('Payement', PayementData)
            # return Response({'message': 'Payment executed successfully'})
            return Response(response.json())
        else:
            return Response({'error': 'Invalid PayPal response'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['Post'])
def createpayouts(request):
    RequestBody =  json.loads(request.body)
    RecepientEmail = RequestBody["RecipientEmail"]
    Price = RequestBody["Price"]
    #PluginId = RequestBody["PluginId"]
    data = {
        'grant_type': 'client_credentials',
        }
    AccesTokenresponse = requests.post('https://api-m.sandbox.paypal.com/v1/oauth2/token', data=data, auth=(Paypal_Client_ID, Paypal_Client_Key))
    responseToken = json.loads(AccesTokenresponse.text)
    token_type = responseToken["token_type"]
    access_token = responseToken["access_token"]
    headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    
    json_data = { "sender_batch_header": { 
       # "sender_batch_id": "Payouts_2020_100007", 
        "email_subject": "You have a payout!", 
        "email_message": "You have received a payout! Thanks for using our service!" }, 
        "items": [ 
            { "recipient_type": "EMAIL", 
                "amount": {
                 "value": Price, 
                 "currency": "USD" 
                 }, 
                "receiver": RecepientEmail } ] 
        }
    ExecutePayout = requests.post('https://api-m.sandbox.paypal.com/v1/payments/payouts', headers=headers, json=json_data)
    
    if ExecutePayout.ok:
        ExecutePayoutBody = json.loads(ExecutePayout.text)
        PayoutBatchID = ExecutePayoutBody['batch_header']['payout_batch_id']
        params = (
             ('page', '1'),
            )
        PayoutInfo = requests.get('https://api-m.sandbox.paypal.com/v1/payments/payouts/'+ PayoutBatchID, headers=headers, params=params)
        PayoutInfoData = json.loads(PayoutInfo.text)
        Amount = PayoutInfoData['batch_header']['amount']['value']
        AmountCurrency = PayoutInfoData['batch_header']['amount']['currency']
        Fee = PayoutInfoData['batch_header']['fees']['value']
        FeeCurrency = PayoutInfoData['batch_header']['fees']['currency']

        PayoutDate = datetime.today().strftime('%Y-%m-%d')
        PayoutData = {
            'PayoutBatchID' : PayoutBatchID,
            'RecepientEmail' : RecepientEmail,
            'PayoutDate' : PayoutDate,
            'Fee' : Fee,
            'FeeCurrency' : FeeCurrency,
            'Amount' : Amount,
            'AmountCurrency' : AmountCurrency
        }
       # return Response(response.json())  # or do something with the successful response
        add_data_to_firestore('Payout', PayoutData)
        return Response(PayoutInfo.json())
    else:
        return Response({"statuscode:":  response.status_code, "text" : response.text})
    
@api_view(['Post'])
def testingFB(request) :
    example_data = {
    'name': 'John Doe',
    'email': 'johndoe@example.com',
    'age': 30
    }
    add_data_to_firestore('tetsing', example_data)




   


