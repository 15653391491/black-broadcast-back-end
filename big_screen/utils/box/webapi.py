import requests

key = "efe4e9291a4a665ff691c55e3a3b871d"
url = "https://restapi.amap.com/v3/geocode/regeo?"


def getaddress(location):
    params = {
        "key": key,
        "location": location
    }
    headers = {
        "Content-type": "application/json",
        'Upgrade': 'HTTP/1.1'
    }
    ret = requests.get(url=url, headers=headers, params=params)
    con = eval(ret.text)
    info = con["regeocode"]
    district = info["addressComponent"]["district"]
    formatted_address = info["formatted_address"]
    content = {
        "district": district,
        "formatted_address": formatted_address
    }
    return content


