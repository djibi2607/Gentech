import os, resend
from typing import Dict

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