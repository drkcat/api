import hug, requests, json
from falcon import HTTP_404


def send_request(url, params=None, headers=None, files=None, data=None, post=False, parse=True):
    try:
        if post:
            r = requests.post(url, params=params, headers=headers, files=files, data=data, timeout=100)
        else:
            r = requests.get(url, params=params, headers=headers, files=files, data=data, timeout=100)
    except:
        return None

    if r.status_code != 200:
        while r.status_code == 429:
            r = r.get(url, params=params, headers=headers, files=files, data=data)
    if parse:
        return json.loads(r.text)
    else:
        return r.url


def get_server(region):
    servers = {
        'br': 'br1',
        'eune': 'eun1',
        'euw': 'euw1',
        'jp': 'jp1',
        'kr': 'kr',
        'lan': 'la1',
        'las': 'la2',
        'na': 'na1',
        'oce': 'oc1',
        'ru': 'ru',
        'tr': 'tr1'
    }
    return servers[region]


def get_summoner(key, region, name):
    url = 'https://' + region + '.api.pvp.net/api/lol/' + region + '/v1.4/summoner/by-name/' + name
    params = {
        'api_key': key
    }
    return send_request(url, params)


def get_summoner_icon(key, region, summoner, summoner_name):
    versions_url = 'https://global.api.pvp.net/api/lol/static-data/euw/v1.2/versions'
    params = {
        'api_key': key
    }
    url = 'http://ddragon.leagueoflegends.com/cdn/%s/img/profileicon/' % (send_request(versions_url, params)[0])
    return url + str(summoner[summoner_name]['profileIconId']) + '.png'


def get_stats(key, region, summoner_id):
    url = 'https://%s.api.pvp.net//api/lol/%s/v1.3/stats/by-summoner/%s/summary' % (region, region, summoner_id)
    params = {
        'api_key': key
    }

    return send_request(url, params)


def get_top_champions(key, region, server, summoner_id, count = 3):
    url = 'https://' + region + '.api.pvp.net/championmastery/location/' + server + '/player/' + summoner_id + '/topchampions'
    params = {
        'api_key': key,
        'count': count
    }
    return send_request(url, params)

def get_stats_ranked(key, region, summoner_id):
    url = 'https://' + region + '.api.pvp.net//api/lol/' + region + '/v2.5/league/by-summoner/' + summoner_id
    params = {
        'api_key': key
    }
    return send_request(url, params)


@hug.get('/profile', output=hug.output_format.pretty_json)
def get_summoner_profile(name, region, key):
    name = name.lower().replace(' ', '')
    summoner = get_summoner(key, region, name)
    id = summoner[name]['id']
    stats = get_stats(key, region, str(summoner[name]['id']))

    if not stats:
        return {
            'errors': {
                'status': HTTP_404
             }
        }
    icon = get_summoner_icon(key, region, summoner, name)

    ranked = None

    try:
        ranked_stats = get_stats_ranked(key, region, str(summoner[name]['id']))
    except:
        ranked_stats = None

    if summoner[name]['summonerLevel'] != 30:
        level = summoner[name]['summonerLevel']

    if '30' in str(summoner[name]['summonerLevel']):
        level = summoner[name]['summonerLevel']
        if ranked_stats:
            if ranked_stats[str(summoner[name]['id'])][0]['queue'] == 'RANKED_SOLO_5x5':
                i = 0
                found = False
                while not found:
                    if str(ranked_stats[str(summoner[name]['id'])][0]['entries'][i]['playerOrTeamId']) != str(
                            summoner[name]['id']):
                        i += 1
                    else:
                        info = ranked_stats[str(summoner[name]['id'])][0]['entries'][i]
                        found = True

                ranked = {}
                ranked['league'] = ranked_stats[str(summoner[name]['id'])][0]['tier'].title()
                ranked['division'] = info['division']
                ranked['league_points'] = info['leaguePoints']
                ranked['wins'] = info['wins']
                ranked['losses'] = info['losses']
                ranked['winratio'] = int((float(info['wins']) / (float(info['wins']) + float(info['losses']))) * 100)

    normal = {}
    for summary in stats['playerStatSummaries']:
        if summary['playerStatSummaryType'] == 'Unranked':
            normal['5vs5_wins'] = summary['wins']

        elif summary['playerStatSummaryType'] == 'Unranked3x3':
            normal['3vs3_wins'] = summary['wins']

        elif summary['playerStatSummaryType'] == 'AramUnranked5x5':
            normal['ARAM_wins'] = summary['wins']


    top_champions_stats = get_top_champions(key, region, get_server(region), str(summoner[name]['id']))
    top_champions = []
    for champion_stats in top_champions_stats:
        top_champions.append({
            'champion': champion_stats['championId'],
            'level': champion_stats['championLevel'],
            'points': champion_stats['championPoints'],
            'chest': champion_stats['chestGranted'],
            'tokens': champion_stats['tokensEarned'],
        })


    name = summoner[name]['name']

    return {
        'id': id,
        'name': name,
        'region': region,
        'icon': icon,
        'level': level,
        'ranked': ranked,
        'normal': normal,
        'top_champions': top_champions
    }
