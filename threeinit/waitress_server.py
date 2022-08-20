'''
https://stackoverflow.com/questions/51045911/serving-flask-app-with-waitress-on-windows
'''

from waitress import serve
import flask_dbserver
serve(flask_dbserver.app, host='0.0.0.0', port=12800)
