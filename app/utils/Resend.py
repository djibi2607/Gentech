import os, resend
from typing import Dict
from decimal import Decimal

resend.api_key = os.getenv("RESEND_API_KEY")
if not resend.api_key: 
    raise ValueError ("Resend key not found")

def sendWelcomeEmail(name: str) -> Dict:
    params: resend.Emails.SendParams = {
        "from": "Acme <onboarding@resend.dev>",
        "to": ["djibi26072018@gmail.com"],
        "subject": "Account Creation",
        "html": f"""
            <h1>Welcome to Gentech, {name}!</h1>
            <p>Your account has been successfully created.</p>
            <p>You can now login and start making transactions.</p>
            <br/>
            <p>The Gentech Team</p>"""
    }
    response: resend.Emails.SendResponse = resend.Emails.send(params)
    return response  

def sendWelcomeEmail(name: str) -> Dict:
    params: resend.Emails.SendParams = {
        "from": "Acme <onboarding@resend.dev>",
        "to": ["djibi26072018@gmail.com"],
        "subject": "Account Creation",
        "html": f"""
            <h1>Welcome to Gentech, {name}!</h1>
            <p>Your account has been successfully created.</p>
            <p>You can now login and start making transactions.</p>
            <br/>
            <p>The Gentech Team</p>"""
    }
    response: resend.Emails.SendResponse = resend.Emails.send(params)
    return response  

def send sendDepositEmail(name:str, amount: Decimal)
    params: resend.Emails.SendParams = {
        "from" : "Acme <onboarding@resend.dev",
        "to" : ["djibi26072018@gmail.com"],
        "subject" : "Deposit Transaction",
         "html": f"""
            <h1>Your deposit has been successful, {name}!</h1>
            <p>Your deposit of {amount} is now available in your account.</p>
            <br/>
            <p>The Gentech Team</p>"""
        }
    
    response : resend.Emails.SendParams = resend.Emails.send(params)

    return response

def send sendWithdrawEmail(name:str, amount: Decimal)
    params: resend.Emails.SendParams = {
        "from" : "Acme <onboarding@resend.dev",
        "to" : ["djibi26072018@gmail.com"],
        "subject" : "Withdraw Transaction",
         "html": f"""
            <h1>Your withdrawal has been successful, {name}!</h1>
            <p>Your withdraw of {amount} has now been withdrawn from your account.</p>
            <br/>
            <p>The Gentech Team</p>"""
        }
    
    response : resend.Emails.SendParams = resend.Emails.send(params)

    return response