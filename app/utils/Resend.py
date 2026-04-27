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


def sendDepositEmail(name:str, amount: Decimal):
    params: resend.Emails.SendParams = {
        "from" : "Acme <onboarding@resend.dev>",
        "to" : ["djibi26072018@gmail.com"],
        "subject" : "Deposit Transaction",
         "html": f"""
            <h1>Your deposit has been successful, {name}!</h1>
            <p>Your deposit of ${amount} is now available in your account.</p>
            <br/>
            <p>The Gentech Team</p>"""
        }
    
    response : resend.Emails.SendResponse = resend.Emails.send(params)

    return response

def sendWithdrawEmail(name:str, amount: Decimal):
    params: resend.Emails.SendParams = {
        "from" : "Acme <onboarding@resend.dev>",
        "to" : ["djibi26072018@gmail.com"],
        "subject" : "Withdraw Transaction",
         "html": f"""
            <h1>Your withdrawal has been successful, {name}!</h1>
            <p>Your withdraw of ${amount} has now been withdrawn from your account.</p>
            <br/>
            <p>The Gentech Team</p>"""
        }
    
    response : resend.Emails.SendResponse = resend.Emails.send(params)

    return response

def sendTransferEmailReceiver (receiver_name: str, amount: Decimal,sender_name:str, sender_email: str | None = None, sender_phone : str | None = None):
    params: resend.Emails.SendParams = {
        "from" : "Acme <onboarding@resend.dev>",
        "to" : ["djibi26072018@gmail.com"],
        "subject" : "Transfer Transaction",
         "html": f"""
            <h1>You received a transfer transaction from {sender_name} / {sender_email} / {sender_phone}, {receiver_name}!</h1>
            <p>The amount of ${amount} has now been added to your balance and available to use. </p>
            <br/>
            <p>The Gentech Team</p>"""
        }
    
    response : resend.Emails.SendResponse = resend.Emails.send(params)

    return response

def sendTransferEmailSender (sender_name: str, amount: Decimal, receiver_name: str, receiver_email: str | None = None, receiver_phone : str | None = None):
    params: resend.Emails.SendParams = {
        "from" : "Acme <onboarding@resend.dev>",
        "to" : ["djibi26072018@gmail.com"],
        "subject" : "Transfer Transaction",
         "html": f"""
            <h1>Your transfer of ${amount} to {receiver_name} / {receiver_email}/ {receiver_phone} has been successful, {sender_name}!</h1>
            <p>The amount of {amount} has been deducted from your account! </p>
            <br/>
            <p>The Gentech Team</p>"""
        }
    
    response : resend.Emails.SendResponse = resend.Emails.send(params)

    return response
