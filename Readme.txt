1-to run this project you need to create a virtual environment :

       python -m venv <virtualenvironmentname>

2-activate the virtual environment :

        <virtualenvironmentname>\Scripts\activate

3-while in virtual environment run the following commande to install the packages:

        pip install -r requirements.txt

4-while in virtual environment run the following commande to run the server while terminal in the parent folder :

        python manage.py runserver








the api is devided into 3 parts (all are POST):
     - http://127.0.0.1:8000/setup/ is used to setup the payement .
     
     it takes in the body
      {   
 
    "price" : 420
    }


    - http://127.0.0.1:8000/execute/ to execute the payement 
   
    it takes in the body 

     {
            "PluginId" : "123456789",
            "Accountemail" : "njnjnjnjjnj",
            "paymentId" : "Check Url Params ON success ",
            "payerId" : "Check Url Params ON success"
          }
    

    - http://127.0.0.1:8000/payout/ to execute payout 

    it takes in the body 
    {
    "RecipientEmail" : "",
    "Price" : 
}

