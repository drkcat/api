import hug, requests, json
from falcon import HTTP_400
from bs4 import BeautifulSoup
import datetime

@hug.get('/bus', output=hug.output_format.pretty_json, examples=["poste=1169&source=web", "poste=167&source=opendata"])
def get_buses(poste:int, source=None):
    def get_buses_from_web(poste):
        url = 'http://www.urbanosdezaragoza.es/frm_esquemaparadatime.php?poste={}'.format(poste)
        try:
            res = requests.get(url)
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

        street = None
        lines = None
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
            'poste': poste,
            'street': street,
            'lines': lines,
            'buses': buses,
            'source': 'web',
            'last_update': last_update
        }


    def get_buses_from_opendata(poste):
        url = 'http://www.zaragoza.es/api/recurso/urbanismo-infraestructuras/transporte-urbano/poste/tuzsa-{}.json'.format(poste)
        # url = 'https://www.zaragoza.es/sede/servicio/urbanismo-infraestructuras/transporte-urbano/poste-autobus/tuzsa-{}.json'.format(poste)
        params = {
            'srsname': 'wgs84'
        }

        try:
            res = requests.get(url, params = params)
            data = json.loads(res.text)

        except Exception as e:
            return {
                'errors': {
                    'status': HTTP_400,
                    'exception': str(e),
                 }
            }

        if 'error' in data:
            return None

        street = data['title'].split(')')[-1].split('Lí')[0].strip().title()
        lines = data['title'].title().split(street)[-1].strip().replace('Líneas: ','')
        buses = []
        nodatabuses = []
        last_update = data['lastUpdated']

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
            'poste': poste,
            'street': street,
            'lines': lines,
            'buses': buses,
            'source': 'opendata',
            'last_update': last_update
        }


    if source == 'web':
        buses = get_buses_from_web(poste)
        if not buses:
            return {
                'errors': {
                    'status': HTTP_400
                 }
            }

    elif source == 'opendata':
        buses = get_buses_from_opendata(poste)
        if not buses:
            return {
                'errors': {
                    'status': HTTP_400
                 }
            }

    else:
        buses = get_buses_from_opendata(poste)
        if not buses:
            buses = get_buses_from_web(poste)
            if not buses:
                return {
                    'errors': {
                        'status': HTTP_400
                     }
                }

    return buses
