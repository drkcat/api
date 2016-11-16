import hug
from falcon import HTTP_400
from endpoints import zgzpls
from endpoints import riotpls


@hug.extend_api('/zgzpls')
def zgzpls_api():
    return [zgzpls]


@hug.extend_api('/riotpls')
def riotpls_api():
    return [riotpls]
