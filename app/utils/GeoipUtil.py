import geoip2.database

reader = geoip2.database.Reader(r"C:\Users\djibi\Downloads\gentech\app\GeoIp\GeoLite2-City.mmdb")

def get_location (ip : str):

    try: 
        local_ips = ["127.0.0.1", "localhost", "::1"]
    
        if ip in local_ips:
            return {
            "Country": "United States",
            "City": None,
            "Longitude": None,
            "Latitude": None
            }
        
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