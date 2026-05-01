from user_agents import parse

async def getUserAgent (user_agent:str):

    try: 
        ua = parse(user_agent)

        return {
            "Device" : f"{ua.device.brand} {ua.device.model}",
            "os" : ua.os.family,
            "browser" : ua.browser.family
        }
    
    except Exception:
        return {
            "Device" : None,
            "os" : None,
            "browser" : None
        }