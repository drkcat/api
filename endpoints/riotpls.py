import hug, requests, json
from falcon import HTTP_404
from bs4 import BeautifulSoup

@hug.get('/profile', output=hug.output_format.pretty_json)
def get_summoner_profile(summoner_name):
    return {
        'errors': {
            'status': HTTP_404
         }
    }
