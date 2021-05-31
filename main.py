import json
import requests
from unidecode import unidecode
from flask import Flask, request, jsonify

from app.regex import Regex
from app.elements import ElementSpecs
from app.format import Formats
from app.get import get


def insight_bot(request):
    """ Http Cloud Function
    Args: Platform: [android/itunes], Identifier: App Identifier 
    Returns: App metadata
    """
    # get requeted platform, identifer
    platform = request.args.get('platform', None)
    identifier = request.args.get('identifier', None)
    
    # make request to appstore
    if platform != "itunes" and platform != "android":
        return jsonify(
            status=400,
            msg="invalid platform: " + platform
        )
    if identifier is None:
        return jsonify(
            status=400,
            msg="identifier is empty"
        )
        
    # iphone
    if platform == "itunes":
        return _fetch_appstore(identifier)
    
    # android
    if platform == "android":
        return _fetch_playstore(identifier)


def _fetch_appstore(identifier):
    """ metadata fetcher from appstore
    Args: bundleId
    Returns: App metadata
    """
    # url of itunes lookup api
    url = "https://itunes.apple.com/lookup"
    
    # parameters
    PARAMS = {'bundleId':identifier, 'country': 'us', 'entity': 'software'}
    
    # do request
    r = requests.post(url = url, data = PARAMS) 
  
    j = r.json()
    
    # not found
    if len(j['results']) == 0:
        return jsonify(
            status=404,
            msg="no metadata found for: " + identifier
        )
    
    # generate response
    obj = {}
    obj['source'] = j['results'][0]['trackViewUrl']
    ## check unicode
    if isinstance(j['results'][0]['trackName'], str):
        obj['name'] = unidecode(j['results'][0]['trackName'])
    else:
        obj['name'] = j['results'][0]['trackName']
    if isinstance(j['results'][0]['sellerName'], str):
        obj['publisher'] = unidecode(j['results'][0]['sellerName'])
    else:
        obj['publisher'] = j['results'][0]['sellerName']
    obj['category'] = j['results'][0]['primaryGenreName']
    obj['raw'] = r.text
    
    # temporary until we have more datasource
    data = []
    data.append(obj)
    
    resp = {}
    resp['platform'] = "itunes"
    resp['identifier'] = identifier
    resp['data'] = data
    
    # extracting data
    return jsonify(resp)


def _fetch_playstore(identifier):
    """ metadata fetcher from playstore
    Args: appId
    Returns: App metadata
    """
    
    # generate request url to playstore
    url = Formats.Detail.build(app_id=identifier, lang="en", country="us")
    
    # do request
    resp = get(url)
    
    # not found
    if resp == "App not found":
        return jsonify(
            status=404,
            msg="no metadata found for: " + identifier
        )
    
    # parse playstore response
    matches = Regex.SCRIPT.findall(resp)

    res = {}

    # generate key-value pair from playstore response
    for match in matches:
        key_match = Regex.KEY.findall(match)
        value_match = Regex.VALUE.findall(match)

        if key_match and value_match:
            key = key_match[0]
            value = json.loads(value_match[0])

            res[key] = value

    # generate response
    result = {}

    for k, spec in ElementSpecs.Detail.items():
        content = spec.extract_content(res)
        # check unicode
        if isinstance(content, str):
            content = unidecode(content)
        result[k] = content
    
    obj = {}
    obj["source"] = url
    obj["name"] = result["title"]
    obj["publisher"] = result["developer"]
    obj["category"] = result["genre"]
    obj["raw"] = json.dumps(result)
    
    # temporary until we have more datasource
    data = []
    data.append(obj)
    
    resp = {}
    resp["data"] = data
    resp["identifier"] = identifier
    resp["platform"] = "android"
    
    return json.dumps(resp, ensure_ascii=True)
