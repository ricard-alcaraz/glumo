from glumo.api.api_nightscout import NightscoutAPI
from glumo.api.api_linkup import LinkUPAPI

#DEFAULT_API_BASE_URL = "https://api-eu.libreview.io"  # or "https://api-eu.libreview.io" for Europe

#API_NIGHTCOUT = "https://cd4c.ns.gluroo.com/api/v1/entries?token=cd4cd1bc-bb1f-4f2c-a97b-ab55bbdc66a1"
"""DEFAULT_HEADER = {
            'accept-encoding': 'gzip',
            'cache-control': 'no-cache',
            'connection': 'Keep-Alive',
            'content-type': 'application/json',
            'product': 'llu.android',
            'version': '4.7'
        }
"""

def get_api_instance(api_type):
    """Returns an instance of the specified API class.
    Args:
        api_type (str): The type of API to return.
    Returns:
        BaseAPI: An instance of the specified API class.
    """
    if api_type == 'LinkUP':
        return LinkUPAPI()
    elif api_type == 'Nightscout':
        return NightscoutAPI()
    else:
        raise ValueError("Unsupported API type")
    
def get_header(api_type):
    """Returns the headers for the specified API.
    Args:
        api_type (str): The type of API to return the headers for.
    Returns:
        dict: The headers for the specified API.
    """
    if api_type == 'LinkUP':
        header = {
            'accept-encoding': 'gzip',
            'cache-control': 'no-cache',
            'connection': 'Keep-Alive',
            'content-type': 'application/json',
            'product': 'llu.android',
            'version': '4.7'
        }
        return header
    elif api_type == 'Nightscout':
        return ""
    
def get_base_url(api_type):
    """Returns the base URL for the specified API.
    Args:
        api_type (str): The type of API to return the base URL for.
    Returns:
        str: The base URL for the specified API.
    """
    if api_type == 'LinkUP':
        base_url = "https://api-eu.libreview.io" 
        return base_url
    elif api_type == 'Nightscout':
        return "https://cd4c.ns.gluroo.com"
    else:
        raise ValueError("Unsupported API type")