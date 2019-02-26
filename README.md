# drk.cat REST APIs
That feel when the APIs are so shitty that you have to make better ones.

# ZgzPls
## Parameters
 - `number` (required): expects int. Number of the bus station.
 - `source` (optional): expects `web` or `official-api`. From where should get data, urbanosdezaragoza.es or Zaragoza's OpenData Official API.

## Example
`https://api.drk.cat/zgzpls/bus/stations?number=167&source=web`

## Example Response
```
{
    "id": "tuzsa-167",
    "number": 167,
    "street": "Av. Madrid 158",
    "lines": "33, 21, N3, 36, 24",
    "transports": [
        {
            "line": "33",
            "destination": "Delicias",
            "time": "2 min."
        },
        {
            "line": "21",
            "destination": "Oliver",
            "time": "3 min."
        },
        {
            "line": "24",
            "destination": "Valdefierro",
            "time": "3 min."
        },
        {
            "line": "36",
            "destination": "Valdefierro",
            "time": "6 min."
        },
        {
            "line": "33",
            "destination": "Delicias",
            "time": "8 min."
        },
        {
            "line": "24",
            "destination": "Valdefierro",
            "time": "10 min."
        },
        {
            "line": "21",
            "destination": "Oliver",
            "time": "13 min."
        },
        {
            "line": "36",
            "destination": "Valdefierro",
            "time": "15 min."
        }
    ],
    "coordinates": [
        -0.912984317735425,
        41.651519662081036
    ],
    "source": "web",
    "sourceUrl": "http://www.urbanosdezaragoza.es/frm_esquemaparadatime.php?poste=167",
    "lastUpdated": "2019-02-26T12:19:22.012170"
}
```

# RiotPls
## Parameters
 - name (required): Expects string. Summoner display name.
 - region (required): Expects string. Region of the summoner.
 - key (required): Expects string. Riot API Key.

## Example
`https://api.drk.cat/riotpls/profile?name=VoidEvelynn&region=euw&key=YoUrApIkEy`

## Install
If you want tu install it just run `./install.sh` to create the virtualenv and install all Python dependencies.
You can use the example files in `extra` for `gunicorn` systemd unit and `nginx` configuration.