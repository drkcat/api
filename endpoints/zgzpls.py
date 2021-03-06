import hug, requests, json
from falcon import HTTP_400, HTTP_404
from bs4 import BeautifulSoup
import datetime

@hug.get('/bus/stations', output=hug.output_format.pretty_json, examples=["number=1169"])
def get_buses(number:int=None, source=None):
    def get_buses_from_web(number):
        url = 'http://www.urbanosdezaragoza.es/frm_esquemaparadatime.php?poste={}'.format(number)

        try:
            res = requests.get(url)

        except Exception as e:
            return {
                'errors': {
                    'status': HTTP_400,
                    'exception': str(e)
                 }
            }

        try:
            backup = json.loads(requests.get('https://zgzpls.firebaseio.com/bus/stations/tuzsa-{}.json'.format(number)).text)

        except:
            backup = None

        if res.status_code != 200:
            return None

        soup = BeautifulSoup(res.text, 'html.parser')
        table = soup.find(attrs={"style": "border:1pt solid #cccccc"}).findAll('tr')
        table.pop(0)

        if backup:
            street = backup['street']
            lines = backup['lines']
            coordinates = backup['coordinates']

        else:
            street = None
            lines = None
            coordinates = None

        buses = []
        nodatabuses = []
        last_update = datetime.datetime.now().isoformat()
        

        for row in table:
            cells = row.findAll('td')
            line = cells[0].getText()
            destination = cells[1].getText().title()
            try:
                time = int(cells[2].getText().split()[0])
                buses.append({
                    'line': line,
                    'destination': destination,
                    'time': '{} min.'.format(time)
                })

            except:
                time = cells[2].getText()
                nodatabuses.append({
                    'line': line,
                    'destination': destination,
                    'time': time
                })

        buses = sorted(buses, key=lambda bus: int(bus['time'].split()[0]))
        buses.extend(nodatabuses)

        return {
            'id': 'tuzsa-' + str(number),
            'number': number,
            'street': street,
            'lines': lines,
            'transports': buses,
            'coordinates': coordinates,
            'source': 'web',
            'sourceUrl': url,
            'lastUpdated': last_update
        }


    def get_buses_from_opendata(number):
        url = 'https://www.zaragoza.es/sede/servicio/urbanismo-infraestructuras/transporte-urbano/poste-autobus/tuzsa-{}.json'.format(number)
        params = {
            'srsname': 'wgs84'
        }
        headers = {
            'Accept': 'application/json'
        }

        try:
            res = requests.get(url, params = params, headers = headers)
            data = json.loads(res.text)

            if 'status' in data and data['status'] == 404:
                return {
                    'errors': {
                        'status': HTTP_404
                     }
                }

        except Exception as e:
            return {
                'errors': {
                    'status': HTTP_400,
                    'exception': str(e),
                 }
            }

        try:
            backup = json.loads(requests.get('https://zgzpls.firebaseio.com/bus/stations/tuzsa-{}.json'.format(number)).text)
        except:
            backup = None

        if not data or 'error' in data or not 'title' in data:
            return None

        street = data['title'].split(')')[-1].split('Lí')[0].strip().title()
        lines = data['title'].title().split(street)[-1].strip().replace('Líneas: ','')
        buses = []
        nodatabuses = []
        last_update = data['lastUpdated']
        if 'geometry' in data and 'coordinates' in data['geometry']:
            coordinates = data['geometry']['coordinates']

        elif backup:
            coordinates = backup['coordinates']

        else:
            coordinates = None

        for destination in data['destinos']:
            try:
                time = int(destination['primero'].replace(' minutos', '').rstrip('.'))
                buses.append({
                    'line': destination['linea'],
                    'destination': destination['destino'].rstrip(',').rstrip('.').title(),
                    'time': '{} min.'.format(time)
                })

            except:
                time = destination['primero'].rstrip('.').replace('cin', 'ción')
                nodatabuses.append({
                    'line': destination['linea'],
                    'destination': destination['destino'].rstrip(',').rstrip('.').title(),
                    'time': '{}'.format(time)
                })

            try:
                time = int(destination['segundo'].replace(' minutos', '').rstrip('.'))
                buses.append({
                    'line': destination['linea'],
                    'destination': destination['destino'].rstrip(',').rstrip('.').title(),
                    'time': '{} min.'.format(time)
                })

            except:
                time = destination['segundo'].rstrip('.').replace('cin', 'ción')
                nodatabuses.append({
                    'line': destination['linea'],
                    'destination': destination['destino'].rstrip(',').rstrip('.').title(),
                    'time': '{}'.format(time)
                })

        buses = sorted(buses, key=lambda bus: int(bus['time'].split()[0]))
        buses.extend(nodatabuses)

        return {
            'id': 'tuzsa-' + str(number),
            'number': number,
            'street': street,
            'lines': lines,
            'transports': buses,
            'coordinates': coordinates,
            'source': 'official-api',
            'sourceUrl': res.url,
            'lastUpdated': last_update
        }

    if number:
        if source == 'web':
            buses = get_buses_from_web(number)
            if not buses:
                return {
                    'errors': {
                        'status': HTTP_404
                    }
                }

        elif source == 'official-api':
            buses = get_buses_from_opendata(number)
            if not buses:
                return {
                    'errors': {
                        'status': HTTP_404
                    }
                }

        else:
            buses = get_buses_from_opendata(number)
            if not buses:
                buses = get_buses_from_web(number)
                if not buses:
                    return {
                        'errors': {
                            'status': HTTP_404
                        }
                    }

        if not 'errors' in buses:
            data = {
                'transports': buses['transports'],
                'lastUpdated': buses['lastUpdated'],
            }
            if buses['lines']:
                data['lines'] = buses['lines']
            try:
                requests.patch('https://zgzpls.firebaseio.com/bus/stations/tuzsa-{}.json'.format(number), json = data)

            except Exception:
                requests.put('https://zgzpls.firebaseio.com/bus/stations/tuzsa-{}.json'.format(number), json = data)

        return buses
    else:
        return json.loads(requests.get('https://zgzpls.firebaseio.com/bus/stations.json').text)

@hug.get('/bus/lines', output=hug.output_format.pretty_json, examples=["number=21",])
def get_bus_line(number = None):
    if id:
        res = requests.get('https://zgzpls.firebaseio.com/bus/lines/tuzsa-{}.json'.format(number))
        data = json.loads(res.text)
        if data != 'null':
            return data

        else:
            return {
                'errors': {
                    'status': HTTP_400
                }
            }
    else:
        return json.loads(requests.get('https://zgzpls.firebaseio.com/bus/lines.json').text)

@hug.get('/tram/stations', output=hug.output_format.pretty_json, examples=["number=1169"])
def get_tram(number:int=None, street=None):
    if not number and street:
        stations = json.loads(requests.get('https://zgzpls.firebaseio.com/tram/stations.json').text)
        found = False
        for station in stations:
            if stations[station]['street'].replace('ñ', 'n').replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u').lower() == street.replace('ñ', 'n').replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u').lower():
                number = stations[station]['number']
                found = True
                break

        if not found:
            return {
                'errors': {
                    'status': HTTP_404
                 }
            }

    elif not number and not street:
        return {
            'errors': {
                'status': HTTP_400
             }
        }

    url = 'https://www.zaragoza.es/sede/servicio/urbanismo-infraestructuras/transporte-urbano/parada-tranvia/{}.json'.format(number)
    params = {
        'srsname': 'wgs84'
    }
    headers = {
        'Accept': 'application/json'
    }

    try:
        res = requests.get(url, params = params, headers = headers)
        data = json.loads(res.text)

        if 'status' in data and data['status'] == 404:
            return {
                'errors': {
                    'status': HTTP_404
                 }
            }

    except Exception as e:
        return {
            'errors': {
                'status': HTTP_400,
                'exception': str(e),
             }
        }

    try:
        backup = json.loads(requests.get('https://zgzpls.firebaseio.com/tram/stations/tram-{}.json'.format(number)).text)

    except:
        backup = None

    if 'error' in data or not 'title' in data:
        return None

    street = backup['street']
    # street = data['title'].title()
    lines = 'L1'
    trams = []
    nodatatrams = []
    last_update = data['lastUpdated']
    coordinates = backup['coordinates']

    for destination in data['destinos']:
        try:
            time = destination['minutos']
            trams.append({
                'line': destination['linea'],
                'destination': destination['destino'].rstrip(',').rstrip('.').title(),
                'time': '{} min.'.format(time)
            })

        except:
            time = destination['minutos'].rstrip('.').replace('cin', 'ción')
            nodatatrams.append({
                'line': destination['linea'],
                'destination': destination['destino'].rstrip(',').rstrip('.').title(),
                'time': '{}'.format(time)
            })

    trams = sorted(trams, key=lambda bus: int(bus['time'].split()[0]))
    trams.extend(nodatatrams)

    output = {
        'id': 'tuzsa-' + str(number),
        'number': number,
        'street': street,
        'lines': lines,
        'transports': trams,
        'coordinates': coordinates,
        'lastUpdated': last_update
    }
    data = {
        'transports': output['transports'],
        'lastUpdated': output['lastUpdated'],
    }

    if output['lines']:
        data['lines'] = output['lines']

    requests.patch('https://zgzpls.firebaseio.com/tram/stations/tram-{}.json'.format(number), json = data)

    return output
