# drk.cat REST APIs
That feel when the APIs are so shitty that you have to make better ones.

# ZgzPls
## Parameters
 - `poste` (required): expects int. Number of the poste.
 - `source` (optional): expects `web` or `opendata`. From where should get data, urbanosdezaragoza.es or Zaragoza's OpenData.

## Example
`https://api.drk.cat/zgzpls/bus?poste=1169&source=web`

# RiotPls
## Parameters
 - name (required): Expects string. Summoner display name.
 - region (required): Expects string. Region of the summoner.
 - key (required): Expects string. Riot API Key.

## Example
`https://api.drk.cat/riotpls/profile?name=LuxieEndbringer&region=euw&key=YoUrApIkEy`

## Install
If you want tu install it just run `./install.sh` to create the virtualenv and install all Python dependencies.
You can use the example files in `extra` for `gunicorn` systemd unit and `nginx` configuration.