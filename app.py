#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout

app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print('Request:')
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)

    # print(res)

    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    if req.get('result').get('action') == 'water-recommendation':
        result = req.get('result')
        parameters = result.get('parameters')
        baseurl = 'https://query.yahooapis.com/v1/public/yql?'
        yql_query = makeYqlQuery(req)
        if yql_query is None:
            return {}
        yql_url = baseurl + urlencode({'q': yql_query}) + '&format=json'
        result = urlopen(yql_url).read()
        data = json.loads(result)
        res = makeWebhookResult(data, parameters)
    return res


def makeYqlQuery(req):
    result = req.get('result')
    parameters = result.get('parameters')
    city = parameters.get('geo-city')
    if city is None:
        return None

    return "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='" \
        + city + "')"


def makeWebhookResult(data, parameters):
    query = data.get('query')
    if query is None:
        return {}

    result = query.get('results')
    if result is None:
        return {'speech': 'No Result', 'displayText': 'No Result',
                'source': 'apiai-weather-webhook-sample'}
    channel = result.get('channel')
    if channel is None:
        return {'speech': 'No Channel', 'displayText': 'No Channel',
                'source': 'apiai-weather-webhook-sample'}

    item = channel.get('item')
    location = channel.get('location')
    units = channel.get('units')
    if location is None or item is None or units is None:
        return {'speech': 'No location or item or units',
                'displayText': 'No location or item or units',
                'source': 'apiai-weather-webhook-sample'}

    condition = item.get('condition')
    if condition is None:
        return {'speech': 'No condition',
                'displayText': 'No condition',
                'source': 'apiai-weather-webhook-sample'}
        plant = parameters.get('plant-type')
        moist = parameters.get('SoilMoisture')
        #cond = float(condition.get('temp'))
        if plant == 'tulips':
            result = {}
            result['speech'] = 'Yuvanshu your {0} needs water? '.format(plant)
            result['displayText'] = result['speech']
            result['source'] = 'apiai-weather-webhook-sample'
        return result


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print('Starting app on port %d' % port)

    app.run(debug=False, port=port, host='0.0.0.0')

			
