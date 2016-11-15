# drk.cat REST APIs
That feel when the APIs are so shitty that you have to make better ones.

# ZgzPls
## Parameters
 - `poste` (required): expects int. Number of the poste.
 - `source` (optional): expects `web` or `opendata`. From where should get data, urbanosdezaragoza.es or Zaragoza's OpenData.
 - `simplify` (optional): expects `true` or `false`. Simplify buses list or not.

## Example
`https://api.drk.cat/zgzpls/bus?poste=1169&source=web&simplify=false`

## Install
If you want tu install it just run `./install.sh` to create the virtualenv and install all Python dependencies.
You can use the example files in `extra` for `gunicorn` systemd unit and `nginx` configuration.