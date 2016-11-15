import hug, requests, json
from falcon import HTTP_400
from bs4 import BeautifulSoup

@hug.get('/bus', output=hug.output_format.pretty_json, examples="poste=1169&source=web&simplify=true")
def get_buses(poste, source='web', simplify=False):
    if source == 'web':
        url = 'http://www.urbanosdezaragoza.es/frm_esquemaparadatime.php?poste={}'.format(poste)
        res = requests.get(url)

        if res.status_code != 200:
            return {
                'errors': {
                    'status': HTTP_400
                 }
            }
        
        soup = BeautifulSoup(res.text, 'lxml')
        table = soup.find(attrs={"style": "border:1pt solid #cccccc"}).findAll('tr')
        table.pop(0)

        street = None
        lines = None
        buses = []

        for row in table:
            cells = row.findAll('td')
            if simplify:
                try:
                    linea = int(cells[0].getText())
                    destino = cells[1].getText().title()
                    tiempo = int(cells[2].getText().replace(' minutos.', ''))
                    buses.append((linea, destino, tiempo))
                except:
                    linea = int(cells[0].getText())
                    destino = cells[1].getText().title()
                    tiempo = int(cells[2].getText().replace(' minutos.', ''))
                    buses.append((linea, destino, tiempo))
            else:
                linea = int(cells[0].getText())
                destino = cells[1].getText().title()
                tiempo = cells[2].getText().rstrip('.')
                buses.append({
                    'linea': linea,
                    'destino': destino,
                    'tiempo': tiempo
                })
        
        if simplify:
            buses = sorted(buses, key=lambda bus: bus[2])
        else:
            buses = sorted(buses, key=lambda bus: int(bus['tiempo'].split()[0]))


    elif source == 'opendata':
        url = 'http://www.zaragoza.es/api/recurso/urbanismo-infraestructuras/transporte-urbano/poste/tuzsa-' + poste.lstrip('0') + '.json'
        params = {
            'srsname': 'wgs84'
        }

        data = json.loads(requests.get(url, params=params).text)

        if 'error' in data:
            return {
                'errors': {
                    'status': HTTP_400
                 }
            }

        street = data['title'].split(')')[-1].split('Lí')[0].strip().title()
        parada = data['title'].split(')')[0].replace('(', '')
        line = data['title'].title().split(street)[-1].strip().replace('Líneas: ','')
        buses = []
        nodatabuses = []

        for destino in data['destinos']:
            try:
                tiempo = int(destino['primero'].replace(' minutos', '').rstrip('.'))
                buses.append((
                    destino['linea'],
                    destino['destino'].rstrip(',').rstrip('.').title(),
                    tiempo
                ))
            except Exception as e:
                print(e)
                tiempo = destino['primero'].rstrip('.').replace('cin', 'ción')
                nodatabuses.append((
                    destino['linea'],
                    destino['destino'].rstrip(',').rstrip('.').title(),
                    tiempo
                ))

            try:
                tiempo = int(destino['segundo'].replace(' minutos', '').rstrip('.'))
                buses.append((
                    destino['linea'],
                    destino['destino'].rstrip(',').rstrip('.').title(),
                    tiempo
                ))
            except Exception as e:
                print(e)
                tiempo = destino['segundo'].rstrip('.').replace('cin', 'ción')
                nodatabuses.append((
                    destino['linea'],
                    destino['destino'].rstrip(',').rstrip('.').title(),
                    tiempo
                ))

        buses = sorted(buses, key=lambda bus: bus[2])
        buses.extend(nodatabuses)


    else:
        return {
            'errors': {
                'status': HTTP_400
             }
        }

    return {
        'poste': poste,
        'street': street,
        'lines': lines,
        'buses': buses,
        'source': source,
        'simplify': simplify
    }
