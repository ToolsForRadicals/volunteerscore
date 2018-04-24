import json
from rauth import OAuth2Service
from tqdm import tqdm
from multiprocessing.dummy import Pool

api_version = "api/v1"


def getNation(token,nation_slug):
    global base_url
    base_url = "https://" + nation_slug + ".nationbuilder.com"
    global params
    params = dict()
    params['base_url'] = base_url
    params['api_version'] = api_version

    #REDIRECT_URI = 'http://localhost:5000/authorized'
    access_token_url = "http://" + nation_slug + ".nationbuilder.com/oauth/token"
    authorize_url = nation_slug + ".nationbuilder.com/oauth/authorize"

    service = OAuth2Service(
                client_id = "f85dfb6b2f85f0db877bf9ad593092e2232be35514d37d25cf63a55cbc9fc3a3",
                client_secret = "7563fccf49623d7c141d921b61cf72c416e6a71d7df712b6dec56a9c4e0dbcfe",
                name = "Margaret",
                authorize_url = authorize_url,
                access_token_url = access_token_url,
                base_url = base_url)

    #token = service.get_access_token(decoder=json.loads, data={"code": code,
                                                             #  "redirect_uri": REDIRECT_URI,
                                                            #   "grant_type": "authorization_code"})
    nation = service.get_session(token)
    nation.headers['Accept'] = 'application/json'
    nation.headers['Content-type'] = 'application/json'
    return nation

def getPaginatedResponse(nation,url):
    # TODO - FIX ME. Proper error handling, check for 200 OK in the response, throw error for 400 / 404, retry on timeout etc.
    rawresponse = nation.get(url)
    response = json.loads(rawresponse.content.decode())
    try:
        pbar = tqdm()
        while response['next']:
            try:
                url = str(base_url + response['next'])
                rawresponse = nation.get(url)
                thispage = json.loads(rawresponse.content.decode())
                response['results'].extend(thispage['results'])
                response['next'] = thispage['next']
                pbar.update(int(len(thispage['results'])))
            except:
                response['next'] = None
                pass
    except KeyError:
        return response['results']

    return response['results']

def getLists(nation):
    url = '{base_url}/{api_version}/lists?limit=100'.format(**params)
    lists = getPaginatedResponse(nation,url)
    return lists


def getPerson(nation,personid):
    params['id'] = personid
    url = '{base_url}/{api_version}/people/{id}'.format(**params)
    response = nation.get(url)
    response = json.loads(response.content.decode())
    person = response['person']
    return person

def getMe(nation):
    url = '{base_url}/{api_version}/people/me'.format(**params)
    response = nation.get(url)
    response = json.loads(response.content.decode())
    me = response['person']
    return me

def getList(nation,listid):
    params['listid'] = listid
    url = '{base_url}/{api_version}/lists/{listid}/people?limit=100'.format(**params)
    people = getPaginatedResponse(nation,url)
    return people

def makeList(nation,listname):
    data = dict()
    data['list'] = dict()
    data['list']['name'] = listname
    data['list']['slug'] = str(str.lower(data['list']['name']).replace(' ','_'))
    me = getMe(nation)
    data['list']['author_id'] = me['id']
    url = '{base_url}/{api_version}/lists'.format(**params)
    listresult = nation.post(url,json.dumps(data))
    return listresult


def getPeople(nation):
    url = '{base_url}/{api_version}/people?limit=100'.format(**params)
    people = getPaginatedResponse(nation,url)
    return people

def getTags(nation):
    url = '{base_url}/{api_version}/tags?limit=100'.format(**params)
    tags = getPaginatedResponse(nation,url)
    tags = [tag['name'] for tag in tags]
    return tags

def updatePerson(nation,personid,data):
    #nation = getNation() #QUESTION - DO WE NEED THIS FOR THREAD / MULTIPROCESSING SAFETY?
    # THIS IS AN UGLY HACK, FIX IT GLOBALLY
    nation.headers['Accept'] = 'application/json'
    nation.headers['Content-type'] = 'application/json'
    params['id'] = personid
    url = '{base_url}/{api_version}/people/{id}'.format(**params)
    result = nation.put(url,data=json.dumps(data))
    return result

def addPeopletoList(nation,peoplelist,listid):
    data = dict()
    data['people_ids'] = peoplelist
    params['listid'] = listid
    url = '{base_url}/{api_version}/lists/{listid}/people'.format(**params)
    result = nation.post(url,data=json.dumps(data))
    return result

def searchPeople(nation,externalid):
    nation.headers['Accept'] = 'application/json'
    nation.headers['Content-type'] = 'application/json'
    params['rnc_id'] = externalid #FIXME
    url = '{base_url}/{api_version}/people/search?rnc_id={rnc_id}'.format(**params)
    result = getPaginatedResponse(nation,url)

