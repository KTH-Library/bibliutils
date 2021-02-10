#!/usr/bin/python

#Author: Gaël Dubus / KTH Library / dubus@kth.se

#For the API client
import os
import requests

#For other functions
from xml.etree import cElementTree as ET


# Get secret keys, tokens and parameters stored as environment variables
UNPAYWALL_EMAIL = os.getenv('UNPAYWALL_EMAIL')
SCOPUS_KEY = os.getenv('SCOPUS_KEY')
SCOPUS_TOKEN = os.getenv('SCOPUS_TOKEN')
LENS_TOKEN = os.getenv('LENS_TOKEN')
ALTMETRICS_API_KEY = os.getenv('ALTMETRICS_API_KEY')
WOS_KEY = os.getenv('WOS_KEY')
    

class BibAPI:
    """
    API calls for:
     - altmetric
     - clarivate (web of science)
     - doi.org
     - elsevier (scopus)
     - the lens
     - ror
     - unpaywall
    """
    def __init__(self, service=None, headers={}, proxies={}, method=requests.get, apiname=""):
        self.apiname = apiname
        if service == 'unpaywall':
            self.base_url = 'https://api.unpaywall.org/v2/'
            self.doc_url = '- URL: https://unpaywall.org/products/api'
            self.options = ['email']
        elif service == 'ror':
            self.base_url = 'https://api.ror.org/'
            self.doc_url = '- URL: https://github.com/ror-community/ror-api#research-organization-registry-ror-api'
            self.options = ['affiliation',
                                'filter',
                                'page']
        elif service == 'doi':
            self.base_url = 'https://doi.org/api/handles/'
            self.doc_url = 'https://www.doi.org/factsheets/DOIProxy.html#rest-api'
            self.options = ['auth',
                                'callback',
                                'cert',
                                'index',
                                'pretty',
                                'type']
        elif service == 'elsevier':
            #other apinames: Embase, SUSHI
            if not apiname:
                print("Please provide the name of the chosen API for Elsevier")
            elif apiname.lower() == 'scopus':
                self.base_url = 'https://api.elsevier.com/content/'
                self.doc_url = '- URL: https://dev.elsevier.com/api_docs.html\n- Swagger UI: https://dev.elsevier.com/scopus.html'
                self.options = ['access_token',
                                    'apikey',
                                    'count',
                                    'date',
                                    'doi',
                                    'eid',
                                    'field',
                                    'httpaccept',
                                    'insttoken',
                                    'issn',
                                    'pii',
                                    'pubmed_id',
                                    'query',
                                    'ref',
                                    'scopus_id',
                                    'start',
                                    'subj',
                                    'subjcode',
                                    'view',
                                    #'citation',
                                    'title']
            elif apiname.lower() == 'sciencedirect':
                self.base_url = 'https://api.elsevier.com/content/'
                self.doc_url = '- URL: https://dev.elsevier.com/api_docs.html\n- Swagger UI: https://dev.elsevier.com/sciencedirect.html'
                self.options = ['access_token',
                                     'apikey',
                                     'date',
                                     'doi',
                                     'eid',
                                     'httpaccept',
                                     'insttoken',
                                     'isbn',
                                     'issn',
                                     'pii',
                                     'pubmed_id',
                                     'query',
                                     'ref',
                                     'scopus_id',
                                     'subj',
                                     'subjcode',
                                     'title',
                                     'view']
            elif apiname.lower() in ["scival","engineeringvillage","geofacets","pharma","authenticate"]:
                print("Elsevier API " + apiname + " not yet supported")
            else:
                print("Unknown API name for Elsevier: " + apiname)
        elif service == 'lens':
            self.base_url = 'https://api.lens.org/'
            self.doc_url = '- URL: https://docs.api.lens.org/\n- Swagger UI: https://api.lens.org/swagger-ui.html'
            self.options = ['exclude',
                                'from',
                                'include',
                                'query',
                                'size',
                                'sort',
                                'token']
        elif service == 'altmetric':
            self.base_url = 'https://api.altmetric.com/v1/'
            self.doc_url = '- URL: https://api.altmetric.com/'
            self.options = ['key']
        elif service == 'clarivate':
            #Clarivate APIs are case-sensitive
            if not apiname:
                print("Please provide the name of the chosen API for Web of Science")
            elif apiname == "wos":
                self.base_url = 'https://wos-api.clarivate.com/api/wos/'
                self.doc_url = '- URL: https://clarivate.com/webofsciencegroup/solutions/xml-and-apis/\n- Swagger UI: https://api.clarivate.com/swagger-ui/?apikey= + [api_key] + &url=https://developer.clarivate.com/apis/wos/swagger?forUser%3D + [user_id]\n    To find your user_id: 1) go to https://developer.clarivate.com/apis and log in 2) choose whatever API you have access to and click on "Information" 3) click on "View Swagger definition" at the bottom 4) your user_id is at the end of the url'
                self.options = ['count',
                                    'databaseId',
                                    'edition',
                                    'firstRecord',
                                    'lang',
                                    'loadTimeSpan',
                                    'optionOther',
                                    'optionView',
                                    'publishTimeSpan',
                                    'queryId',
                                    'refId',
                                    'sortField',
                                    'uniqueId',
                                    'usrQuery',
                                    'viewField']
            elif apiname == "woslite":
                self.base_url = 'https://wos-api.clarivate.com/api/woslite/'
                self.doc_url = '- URL: https://clarivate.com/webofsciencegroup/solutions/xml-and-apis/\n- Swagger UI: https://api.clarivate.com/swagger-ui/?apikey= + [api_key] + &url=https://developer.clarivate.com/apis/woslite/swagger?forUser%3D + [user_id]\n    To find your user_id: 1) go to https://developer.clarivate.com/apis and log in 2) choose whatever API you have access to and click on "Information" 3) click on "View Swagger definition" at the bottom 4) your user_id is at the end of the url'
                self.options = ['count',
                                    'databaseId',
                                    'edition',
                                    'firstRecord',
                                    'lang',
                                    'loadTimeSpan',
                                    'publishTimeSpan',
                                    'queryId',
                                    'sortField',
                                    'uniqueId',
                                    'usrQuery']
            elif apiname in ["caas-metabase-api","converisreadapi","endnote","reviewer-connect"]:
                print("Clarivate API " + apiname + " not yet supported")
            else:
                print("Unknown API name for Clarivate: " + apiname)
        else:
            self.base_url = None
            self.doc_url = None
        self.service = service
        self.headers = headers
        self.proxies = proxies
        self.method = method
        self.lasturl = None
        self.lastresponse = None
        self.supported = {"altmetric": [""],
                              "clarivate": ["wos","woslite"],
                              "doi": [""],
                              "elsevier": ["scopus","sciencedirect"],
                              "lens": [""],
                              "ror": [""],
                              "unpaywall": [""]}
    def doc(self, service=None, apiname=""):
        if service:
            if apiname in self.supported[service]:
                self.__init__(service=service,apiname=apiname)
                print("## Documentation for " + service + " API " + apiname + ": ")
                print(self.doc_url)
            else:
                for apiname in self.supported[service]:
                    self.__init__(service=service,apiname=apiname)
                    print("## Documentation for " + service + " API " + apiname + ": ")
                    print(self.doc_url)
        else:
            for service in self.supported:
                for apiname in self.supported[service]:
                    self.__init__(service=service,apiname=apiname)
                    print("## Documentation for " + service + " API " + apiname + ": ")
                    print(self.doc_url + '\n')
    def setHeaders(self, headers):
        self.headers = headers
    def setProxies(self, proxies):
        self.proxies = proxies
    def setMethod(self, method):
        self.method = method
    def call(self, path, params={}, headers={}, proxies={}, method=None, casesensitive=False):
        #self.service and self.apiname should already be set
        if not headers:
            headers = self.headers
        if not proxies:
            proxies = self.proxies
        if not method:
            method = self.method
        url = self.base_url + path.lower() + '?'
        if casesensitive:
            for o in params.keys():
                if o in self.options:
                    url += o + "=" + params[o] + '&'
                else:
                    print("Unknown option for " + self.service + " API " + self.apiname + ": " + o)
        else:
            for o in params.keys():
                if o.lower() in self.options:
                    url += o + "=" + params[o] + '&'
                else:
                    print("Unknown option for " + self.service + " API " + self.apiname + ": " + o)
        #remove extra '&' (or '?' if there are no parameters)
        url = url[:-1]
        self.lasturl = url
        self.lastresponse = method(url, headers=headers, proxies=proxies)
        try:
            return self.lastresponse.json()
        except:
            return self.lastresponse.text
    ## Service-specific methods
    def altmetric(self, path, params={}, headers={}, proxies={}, method=None):
        global ALTMETRICS_API_KEY
        self.__init__(service='altmetric')
        if ALTMETRICS_API_KEY and "key" not in map(str.lower, params.keys()):
            params["key"] = ALTMETRICS_API_KEY
        return self.call(path=path, params=params, headers=headers, proxies=proxies, method=method)
    def clarivate(self, path="", params={}, headers={"accept": 'application/json'}, proxies={}, method=None, apiname="wos"):
        global WOS_KEY
        self.__init__(service='clarivate', apiname=apiname)
        if WOS_KEY and "x-apikey" not in map(str.lower, headers.keys()):
            headers["X-ApiKey"] = WOS_KEY
        DefaultParams = {"count": "100","firstRecord": "1"}
        if path.lower() in ["", "related", "citing", "references"] or "id/" in path.lower():
            DefaultParams["databaseId"] = "WOK"
        for P in DefaultParams:
            if P not in params.keys():
                params[P] = DefaultParams[P]
        return self.call(path=path, params=params, headers=headers, proxies=proxies, method=method, casesensitive=True)
    def doi(self, path, params={}, headers={}, proxies={}, method=None):
        self.__init__(service='doi')
        return self.call(path=path, params=params, headers=headers, proxies=proxies, method=method)
    def elsevier(self, path, params={}, headers={}, proxies={}, method=None, apiname='scopus'):
        global SCOPUS_KEY, SCOPUS_TOKEN
        self.__init__(service='elsevier', apiname=apiname)
        if SCOPUS_KEY and "apikey" not in map(str.lower, params.keys()):
            params["apiKey"] = SCOPUS_KEY
            if SCOPUS_TOKEN and "insttoken" not in params.keys():
                params["insttoken"] = SCOPUS_TOKEN
        if "httpaccept" not in map(str.lower, params.keys()):
            params["httpAccept"] = "application/json"
        return self.call(path=path, params=params, headers=headers, proxies=proxies, method=method)
    def lens(self, path, params={}, headers={}, proxies={}, method=None):
        global LENS_TOKEN
        self.__init__(service='lens')
        if LENS_TOKEN and "token" not in map(str.lower, params.keys()):
            params["token"] = LENS_TOKEN
        return self.call(path=path, params=params, headers=headers, proxies=proxies, method=method)
    def ror(self, path="organizations", params={}, headers={}, proxies={}, method=None):
        self.__init__(service='ror')
        return self.call(path=path, params=params, headers=headers, proxies=proxies, method=method)
    def unpaywall(self, path, params={}, headers={}, proxies={}, method=None):
        global UNPAYWALL_EMAIL
        if UNPAYWALL_EMAIL and "email" not in map(str.lower, params.keys()):
                params = {"email": UNPAYWALL_EMAIL}
        self.__init__(service='unpaywall')
        return self.call(path=path, params=params, headers=headers, proxies=proxies, method=method)



## Ususal API calls

def ror_affiliation(affil):
    TheClient = BibAPI()
    return TheClient.ror(params={"affiliation": affil.encode('utf8')})

def ror_id(affil):
    return safe_access(ror_affiliation(affil), ["items",0,"organization","id"])

def scopus_search(query):
    TheClient = BibAPI()
    return TheClient.elsevier(path='search/scopus', params={"query": query}, apiname='scopus')

def wos_search(query,databaseid="WOK"):
    TheClient = BibAPI()
    return TheClient.clarivate(params={"usrQuery": query, "databaseId": databaseid}, apiname='wos')

def wos_search_params(path="",params={}):
    TheClient = BibAPI()
    return TheClient.clarivate(path=path,params=params, apiname='wos')

def doi_handle(doi):
    TheClient = BibAPI()
    res = TheClient.doi(path=doi, params={"type": "URL"})
    return str(safe_access(res, ["values", 0, "data","value"], ""))

## Scopus API calls

#Returns the list of groups of authors ("collaborations") of a given scopus record
def scopus_collaborations(idtype,idval):
    #idtype can be: eid, doi, pubmed_id (, pii, pui, scopus_id)
    TheClient = BibAPI()
    response = TheClient.elsevier(path="abstract/" + idtype + "/" + idval, apiname='scopus')
    AuthorGroup = safe_access(response,["abstracts-retrieval-response","item","bibrecord","head","author-group"])
    CollaborationList = []
    if AuthorGroup:
        if type(AuthorGroup) == list:
            for Author in AuthorGroup:
                if "collaboration" in Author.keys():
                    if type(Author["collaboration"]) == list:
                        for Coll in Author["collaboration"]:
                            CollaborationList.append(Coll)
                    else:
                        CollaborationList.append(Author["collaboration"])
        else:
            if "collaboration" in AuthorGroup.keys():
                if type(AuthorGroup["collaboration"]) == list:
                    for Coll in AuthorGroup["collaboration"]:
                        CollaborationList.append(Coll)
                else:
                    CollaborationList.append(AuthorGroup["collaboration"])
    return CollaborationList


def get_dates_sciencedirect(idtype,idval,apikey="",apitoken=""):
    #Terms for data mining must have been accepted during the API key creation
    #Scopus API keys can be created at https://dev.elsevier.com/apikey/manage
    global SCOPUS_KEY, SCOPUS_TOKEN
    if not(apikey or apitoken):
        apitoken = SCOPUS_TOKEN
    if not apikey:
        apikey = SCOPUS_KEY
    TheClient = BibAPI()
    response = TheClient.elsevier(path = 'article/'+ idtype + '/' + idval, params = {'apiKey': apikey, 'insttoken': apitoken, 'httpAccept': 'text/xml'}, headers = {'Accept': 'text/xml'}, apiname='sciencedirect')
    XMLString = response.encode('utf8')
    namespaces = {'ns0': "http://www.elsevier.com/xml/svapi/article/dtd",
                      'dc': "http://purl.org/dc/elements/1.1/",
                      'ns1': "http://prismstandard.org/namespaces/basic/2.0/",
                      'ns10': "http://www.elsevier.com/xml/common/struct-bib/dtd",
                      'ns3': "http://www.elsevier.com/xml/xocs/dtd",
                      'ns5': "http://www.elsevier.com/xml/ja/dtd",
                      'ns6': "http://www.elsevier.com/xml/common/dtd",
                      'ns7': "http://www.w3.org/1999/xlink",
                      'ns8': "http://www.elsevier.com/xml/common/struct-aff/dtd",
                      'ns9': "http://www.w3.org/1998/Math/MathML",
                      'xsi': "http://www.w3.org/2001/XMLSchema-instance"}
    root = ET.fromstring(XMLString)
    result = {}
    dateTypes = ["date-received",]
    try:
        DateReceived = root.find('ns0:originalText/ns3:doc/ns3:serial-item/ns5:article/ns5:head/ns6:date-received', namespaces).attrib
        result["date-received"] = DateReceived
    except AttributeError:
        pass
    try:
        DateAccepted = root.find('ns0:originalText/ns3:doc/ns3:serial-item/ns5:article/ns5:head/ns6:date-accepted', namespaces).attrib
        result["date-accepted"] = DateAccepted
    except AttributeError:
        pass
    try:
        DateRevised = root.find('ns0:originalText/ns3:doc/ns3:serial-item/ns5:article/ns5:head/ns6:date-revised', namespaces).attrib
        result["date-revised"] = DateRevised
    except AttributeError:
        pass
    return result




## Output parsing

## Try to access fields of a dictionary/JSON object that may or may not exist
def safe_access(JSobject,JSfieldlist,defaultValue={}):
    CurrentObject = JSobject
    for JSfield in JSfieldlist:
        UJSfield = str(JSfield)
        if type(CurrentObject)==list and UJSfield.isdigit() and int(UJSfield)<len(CurrentObject):
            CurrentObject = CurrentObject[int(UJSfield)]
        elif type(CurrentObject)==dict and UJSfield in CurrentObject.keys():
            CurrentObject = CurrentObject[UJSfield]
        else:
            return defaultValue
    return CurrentObject
