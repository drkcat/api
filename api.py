import hug
from falcon import HTTP_400

from endpoints import zgzpls

app = hug.API(__name__)
app.http.add_middleware(hug.middleware.CORSMiddleware(app, max_age=7))

@hug.extend_api('/zgzpls')
def zgzpls_api():
    return [zgzpls]
