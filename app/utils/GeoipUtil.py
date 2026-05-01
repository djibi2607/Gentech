import geoip2.database

reader = geoip2.database.Reader(r"C:\Users\djibi\Downloads\gentech\app\GeoIp\GeoLite2-City.mmdb")

async def get_location (ip : str):

    try: 
        response = reader.city(ip)

        return {
            "Country" : response.country.name,
            "City" : response.city.name,
            "Longitude" : response.location.longitude,
            "Latitude" : response.location.latitude
        }
    
    except Exception:
        return {
            "Country" : None,
            "City" : None,
            "Longitude" : None,
            "Latitude" : None
        }