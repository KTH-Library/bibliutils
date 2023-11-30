#!/usr/bin/python

#Author: Gaël Dubus / KTH Library / dubus@kth.se

#For the API client
import os
import requests

#For other functions
from xml.etree import cElementTree as ET
import time

# Get secret keys, tokens and parameters stored as environment variables
UNPAYWALL_EMAIL = os.getenv('UNPAYWALL_EMAIL')
SCOPUS_KEY = os.getenv('SCOPUS_KEY')
SCOPUS_TOKEN = os.getenv('SCOPUS_TOKEN')
LENS_TOKEN = os.getenv('LENS_TOKEN')
ALTMETRICS_API_KEY = os.getenv('ALTMETRICS_API_KEY')
WOS_KEY = os.getenv('WOS_KEY')
OVERTON_KEY = os.getenv('OVERTON_KEY')
    

#- ncbi (pubmed)

class BibAPI:
    """
    API calls for:
     - altmetric
     - clarivate (web of science)
     - doaj
     - doi.org
     - elsevier (scopus)
     - the lens
     - libris
     - openalex
     - openapc
     - overton
     - ror
     - unpaywall
    """
    def __init__(self, service=None, headers={}, proxies={}, timeout=None, method=requests.get, apiname=""):
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
        elif service == 'doaj':
            self.base_url = 'https://doaj.org/api/v2/'
            self.doc_url = 'https://doaj.org/api/v2/docs'
            self.options = ['',
                                'api_key',
                                'application_id',
                                'application_ids',
                                'application_json',
                                'article_id',
                                'article_ids',
                                'article_json',
                                'journal_id',
                                'page',
                                'pageSize',
                                'sort']
        elif service == 'doi':
            self.base_url = 'https://doi.org/api/handles/'
            self.doc_url = 'https://www.doi.org/factsheets/DOIProxy.html#rest-api'
            self.options = ['auth',
                                'callback',
                                'cert',
                                'index',
                                'pretty',
                                'type']
        elif service == 'libris':
            self.base_url = 'https://libris.kb.se/xsearch'
            self.doc_url = 'http://librishelp.libris.kb.se/help/xsearch_eng.jsp'
            self.options = ['database',
                                'format',
                                'format_level',
                                'holdings',
                                'n',
                                'order',
                                'query',
                                'start']
        elif service == 'overton':
            self.base_url = 'https://app.overton.io/'
            self.doc_url = 'https://help.overton.io/article/using-the-overton-api'
            self.options = ['api_key',
                                'format',
                                'identifiers',
                                'open_linked_institution_authors',
                                'plain_dois_cited',
                                'query',
                                'sort']
        elif service == "openalex":
            self.base_url = 'https://api.openalex.org/'
            self.doc_url = 'https://docs.openalex.org/api'
            self.options = ['cursor',
                                'filter',
                                'group_by',
                                'mailto',
                                'page',
                                'per_page',
                                'per-page',
                                'search',
                                'sort']
        elif service == "openapc":
            self.base_url = "https://olap.openapc.net/"
            self.doc_url = "https://github.com/OpenAPC/openapc-olap/blob/master/HOWTO.md"
            self.options = ['cut',
                                'drilldown',
                                'order',
                                'page',
                                'pagesize']
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
                                    'refcount',
                                    'scopus_id',
                                    'start',
                                    'startref',
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
                self.doc_url = '- URL: https://clarivate.com/webofsciencegroup/solutions/xml-and-apis/\n- Swagger UI: https://api.clarivate.com/swagger-ui/?apikey= + [api_key] + &url=https://developer.clarivate.com/apis/wos/swagger'
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
                self.doc_url = '- URL: https://clarivate.com/webofsciencegroup/solutions/xml-and-apis/\n- Swagger UI: https://api.clarivate.com/swagger-ui/?apikey= + [api_key] + &url=https://developer.clarivate.com/apis/woslite/swagger'
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
        self.timeout = timeout
        self.method = method
        self.lasturl = None
        self.lastresponse = None
        self.supported = {"altmetric": [""],
                              "clarivate": ["wos","woslite"],
                              "doaj": [""],
                              "doi": [""],
                              "elsevier": ["scopus","sciencedirect"],
                              "lens": [""],
                              "libris": [""],
                              "openalex": [""],
                              "overton": [""],
                              "openapc": [""],
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
    def setTimeout(self, timeout):
        self.timeout = timeout
    def setMethod(self, method):
        self.method = method
    def call(self, path, params={}, headers={}, proxies={}, timeout=None, method=None, casesensitive=False):
        #self.service and self.apiname should already be set
        if not headers:
            headers = self.headers
        if not proxies:
            proxies = self.proxies
        if not timeout:
            timeout = self.timeout
        if not method:
            method = self.method
        if casesensitive:
            url = self.base_url + path + '?'
            for o in params.keys():
                if o in self.options:
                    url += o + "=" + params[o] + '&'
                else:
                    print("Unknown option for " + self.service + " API " + self.apiname + ": " + o)
                    url += o + "=" + params[o] + '&'
        else:
            url = self.base_url + path.lower() + '?'
            for o in params.keys():
                if o.lower() in self.options:
                    url += o + "=" + params[o] + '&'
                else:
                    print("Unknown option for " + self.service + " API " + self.apiname + ": " + o)
                    url += o + "=" + params[o] + '&'
        #remove extra '&' (or '?' if there are no parameters)
        url = url[:-1]
        self.lasturl = url
        self.lastresponse = method(url, headers=headers, proxies=proxies, timeout=timeout)
        try:
            return self.lastresponse.json()
        except:
            return self.lastresponse.text
    ## Service-specific methods
    def altmetric(self, path, params={}, headers={}, proxies={}, timeout=None, method=None):
        global ALTMETRICS_API_KEY
        self.__init__(service='altmetric')
        if ALTMETRICS_API_KEY and "key" not in map(str.lower, params.keys()):
            params["key"] = ALTMETRICS_API_KEY
        return self.call(path=path, params=params, headers=headers, proxies=proxies, timeout=timeout, method=method)
    def clarivate(self, path="", params={}, headers={}, proxies={}, timeout=None, method=None, apiname="wos"):
        global WOS_KEY
        self.__init__(service='clarivate', apiname=apiname)
        if WOS_KEY and "x-apikey" not in map(str.lower, headers.keys()):
            headers["X-ApiKey"] = WOS_KEY
        if "accept" not in map(str.lower, headers.keys()):
            headers["accept"] = "application/json"
        DefaultParams = {"count": "100","firstRecord": "1"}
        if path.lower() in ["", "related", "citing", "references"] or "id/" in path.lower():
            DefaultParams["databaseId"] = "WOK"
        for P in DefaultParams:
            if P not in params.keys():
                params[P] = DefaultParams[P]
        return self.call(path=path, params=params, headers=headers, proxies=proxies, timeout=timeout, method=method, casesensitive=True)
    def doaj(self, path, params={}, headers={}, proxies={}, timeout=None, method=None):
        self.__init__(service='doaj')
        return self.call(path=path, params=params, headers=headers, proxies=proxies, timeout=timeout, method=method, casesensitive=True)
    def doi(self, path, params={}, headers={}, proxies={}, timeout=None, method=None):
        self.__init__(service='doi')
        return self.call(path=path, params=params, headers=headers, proxies=proxies, timeout=timeout, method=method)
    def elsevier(self, path, params={}, headers={}, proxies={}, timeout=None, method=None, apiname='scopus'):
        global SCOPUS_KEY, SCOPUS_TOKEN
        self.__init__(service='elsevier', apiname=apiname)
        if SCOPUS_KEY and "apikey" not in map(str.lower, params.keys()):
            params["apiKey"] = SCOPUS_KEY
            if SCOPUS_TOKEN and "insttoken" not in params.keys():
                params["insttoken"] = SCOPUS_TOKEN
        if "httpaccept" not in map(str.lower, params.keys()):
            params["httpAccept"] = "application/json"
        return self.call(path=path, params=params, headers=headers, proxies=proxies, timeout=timeout, method=method)
    def lens(self, path, params={}, headers={}, proxies={}, timeout=None, method=None):
        global LENS_TOKEN
        self.__init__(service='lens')
        if LENS_TOKEN and "token" not in map(str.lower, params.keys()):
            params["token"] = LENS_TOKEN
        return self.call(path=path, params=params, headers=headers, proxies=proxies, timeout=timeout, method=method)
    def libris(self, path="", params = {}, headers={}, proxies={}, timeout=None, method=None):
        self.__init__(service='libris')
        if "format" not in params.keys():
            params["format"] = "json"
        return self.call(path=path, params=params, headers=headers, proxies=proxies, timeout=timeout, method=method)
    def openapc(self, path, params = {}, headers={}, proxies={}, timeout=None, method=None):
        self.__init__(service='openapc')
        return self.call(path=path, params=params, headers=headers, proxies=proxies, timeout=timeout, method=method)
    def overton(self, path, params = {}, headers={}, proxies={}, timeout=None, method=None):
        global OVERTON_KEY
        self.__init__(service='overton')
        if "api_key" not in map(str.lower, params.keys()):
            params["api_key"] = OVERTON_KEY
        if "format" not in map(str.lower, params.keys()):
            params["format"] = "json"
        return self.call(path=path, params=params, headers=headers, proxies=proxies, timeout=timeout, method=method)
    def openalex(self, path, params = {}, headers={}, proxies={}, timeout=None, method=None):
        self.__init__(service='openalex')
        return self.call(path=path, params=params, headers=headers, proxies=proxies, timeout=timeout, method=method)
    def ror(self, path="organizations", params={}, headers={}, proxies={}, timeout=None, method=None):
        self.__init__(service='ror')
        return self.call(path=path, params=params, headers=headers, proxies=proxies, timeout=timeout, method=method)
    def unpaywall(self, path, params={}, headers={}, proxies={}, timeout=None, method=None):
        global UNPAYWALL_EMAIL
        if UNPAYWALL_EMAIL and "email" not in map(str.lower, params.keys()):
                params = {"email": UNPAYWALL_EMAIL}
        self.__init__(service='unpaywall')
        return self.call(path=path, params=params, headers=headers, proxies=proxies, timeout=timeout, method=method)



## Usual API calls

def ror_affiliation(affil):
    TheClient = BibAPI()
    return TheClient.ror(params={"affiliation": affil})

def ror_id(affil):
    return safe_access(ror_affiliation(affil), ["items",0,"organization","id"])

def scopus_search(query,extraparams={},headers={},proxies={},timeout=None):
    TheClient = BibAPI()
    return TheClient.elsevier(path='search/scopus', params=dict({"query": query},**extraparams), apiname='scopus', headers=headers, proxies=proxies, timeout=timeout)

def scopus_affiliations(ID,headers={},proxies={},timeout=None):
    #WARNING: ID is the "Scopus ID" as defined by Scopus, not EID (that we usually call Scopus ID)!
    TheClient = BibAPI()
    res = TheClient.elsevier(path='abstract/scopus_id/'+ID, params={"httpAccept": "application/json"}, apiname='scopus', headers=headers, proxies=proxies, timeout=timeout)
    return list(safe_access(res,['abstracts-retrieval-response','item','bibrecord','head','author-group'],[]))

def wos_search(query,databaseid="WOK",headers={},proxies={},timeout=None):
    TheClient = BibAPI()
    return TheClient.clarivate(params={"usrQuery": query, "databaseId": databaseid}, headers=headers, proxies=proxies, timeout=timeout)

def wos_search_params(path="",params={},headers={},proxies={},timeout=None):
    TheClient = BibAPI()
    return TheClient.clarivate(path=path,params=params, headers=headers, proxies=proxies, timeout=timeout)

def doi_handle(doi,headers={},proxies={},timeout=None):
    TheClient = BibAPI()
    res = TheClient.doi(path=doi, params={"type": "URL"}, headers=headers, proxies=proxies, timeout=timeout)
    return str(safe_access(res, ["values", 0, "data","value"],""))

def altmetric_score(pub):
    TheClient = BibAPI()
    pubtype = next(iter(pub))
    res = TheClient.altmetric(pubtype+'/'+pub[pubtype])
    return safe_access(res,["score"],0)

def altmetric_search(pub):
    TheClient = BibAPI()
    pubtype = next(iter(pub))
    return TheClient.altmetric(pubtype+'/'+pub[pubtype])

def wos_citations(ut):
    TheClient = BibAPI()
    res = TheClient.clarivate(params={"usrQuery": "UT="+ut, "databaseId": "WOS"}, apiname='wos')
    return safe_access(res, ["Data","Records","records","REC",0,"dynamic_data","citation_related","tc_list","silo_tc","local_count"],0)

def libris_isbn_search(isbn,headers={},proxies={},timeout=None):
    TheClient = BibAPI()
    return TheClient.libris(params={"query": "ISBN:"+isbn}, headers=headers, proxies=proxies, timeout=timeout)

def journal_has_apc(invar):
    TheClient = BibAPI()
    rec = {}
    if "issn" in invar.keys():
        rec = safe_access(TheClient.doaj(path="search/journals/issn%3A"+invar["issn"]),["results",0],{})
    elif "title" in invar.keys():
        reclist = TheClient.doaj(path="search/journals/title%3A"+invar["title"].replace(' ','%20'))
        for jrec in safe_access(reclist,["results"],[]):
            if invar == safe_access(jrec,["bibjson","title"],""):
                rec = jrec
    res = safe_access(rec,["bibjson","apc","has_apc"],"unknown")
    if res == True:
        return "yes"
    elif res == False:
        return "no"
    else:
        return res

def openalex_works(filters,params):
    TheClient = BibAPI()
    filterstring = ','.join([k+':'+filters[k] for k in filters.keys()])
    return TheClient.openalex(path='works',params=params|{"filter": filterstring})

def overton_policy_citations0(doi):
    TheClient = BibAPI()
    res = TheClient.overton(path="articles.php",params={"query": doi})
    return safe_access(res,['results','results',0,'citations'],0)
    
def overton_policy_citations(doi):
    TheClient = BibAPI()
    res = TheClient.overton(path="documents.php",params={"plain_dois_cited": doi})
    return (safe_access(res,['query','total_results'],0),len(safe_access(res,['facets','sources'],[])))

def openapc_price(doi):
    TheClient = BibAPI()
    res = TheClient.openapc(path="cube/openapc/facts",params={"cut": "doi:"+doi.lower()})
    return safe_access(res,[0,'euro'],"")

def openapc_publisher_price(bibmetpublisher,year=None,min_npub=None,max_stdev=None):
    from static_data import OpenAPCPublishers
    # static_data can be found here: https://gita.sys.kth.se/kthb/kthbibliometrics-python/tree/master/include
    openapcpublisher = safe_access(OpenAPCPublishers,[bibmetpublisher],bibmetpublisher).replace(',','\,').replace('&','%26')
    TheClient = BibAPI()
    Goodenough = False
    if year:
        DrillString = "publisher|period"
        CutString = "publisher:"+openapcpublisher+"|period:"+str(year)
    else:
        DrillString = "publisher"
        CutString = "publisher:"+openapcpublisher

    res = TheClient.openapc(path="cube/openapc/aggregate",params={"drilldown": DrillString, "cut": CutString})
    nres = safe_access(res,["summary","apc_num_items"],0)
    stdev =  safe_access(res,["summary","apc_amount_stddev"],99999) #unrealistically high value
    if not stdev:
        stdev = 99999
    if min_npub:
        if max_stdev:
            if nres >= min_npub and stdev <= max_stdev:
                Goodenough = True
        else:
            if nres >= min_npub:
                    Goodenough = True
    else:
        if max_stdev:
            if stdev <= max_stdev:
                Goodenough = True
        else:
            Goodenough = True

    return (safe_access(res,["cells",0,"apc_amount_avg"],""), Goodenough)


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
