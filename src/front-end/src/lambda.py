import app
import serverless_wsgi

# Lambda Handler
def handler(event, context):
    return serverless_wsgi.handle_request(app.app, event, context)