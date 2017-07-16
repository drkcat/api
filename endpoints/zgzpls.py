import hug, requests, json
from falcon import HTTP_400
from bs4 import BeautifulSoup
import datetime

@hug.get('/bus/stations', output=hug.output_format.pretty_json, examples=["number=1169"])
def get_buses(number:int=None, source=None):
    def get_buses_from_web(number):
        url = 'http://www.urbanosdezaragoza.es/frm_esquemaparadatime.php?poste={}'.format(number)
        try:
            res = requests.get(url)
            backup = json.loads(requests.get('https://zgzpls.firebaseio.com/bus/stations/tuzsa-{}.json'.format(number)).text)
        except Exception as e:
            return {
                'errors': {
                    'status': HTTP_400,
                    'exception': str(e),
                 }
            }

        if res.status_code != 200:
            return None

        soup = BeautifulSoup(res.text, 'lxml')
        table = soup.find(attrs={"style": "border:1pt solid #cccccc"}).findAll('tr')
        table.pop(0)

        street = backup['street']
        lines = backup['lines']
        buses = []
        nodatabuses = []
        last_update = datetime.datetime.now().isoformat()
        coordinates = backup['coordinates']

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
            backup = json.loads(requests.get('https://zgzpls.firebaseio.com/bus/stations/tuzsa-{}.json'.format(number)).text)

        except Exception as e:
            return {
                'errors': {
                    'status': HTTP_400,
                    'exception': str(e),
                 }
            }

        if 'error' in data or not 'title' in data:
            return None

        street = data['title'].split(')')[-1].split('Lí')[0].strip().title()
        lines = data['title'].title().split(street)[-1].strip().replace('Líneas: ','')
        buses = []
        nodatabuses = []
        last_update = data['lastUpdated']
        coordinates = backup['coordinates']

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
            'source': 'opendata',
            'lastUpdated': last_update
        }

    if number:
        if source == 'web':
            buses = get_buses_from_web(number)
            if not buses:
                return {
                    'errors': {
                        'status': HTTP_400
                    }
                }

        elif source == 'opendata':
            buses = get_buses_from_opendata(number)
            if not buses:
                return {
                    'errors': {
                        'status': HTTP_400
                    }
                }

        else:
            buses = get_buses_from_opendata(number)
            if not buses:
                buses = get_buses_from_web(number)
                if not buses:
                    return {
                        'errors': {
                            'status': HTTP_400
                        }
                    }
        data = {
            'transports': buses['transports'],
            'lastUpdated': buses['lastUpdated'],
        }
        if buses['lines']:
            data['lines'] = buses['lines']
        requests.patch('https://zgzpls.firebaseio.com/bus/stations/tuzsa-{}.json'.format(number), json = data)
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