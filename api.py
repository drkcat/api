import hug
from falcon import HTTP_400
from endpoints import zgzpls


@hug.extend_api('/zgzpls')
def zgzpls_api():
    return [zgzpls]


@hug.not_found(output=hug.output_format.pretty_json)
def not_found_handler():
    return {
        'errors': {
            'status': HTTP_400
        }
    }
