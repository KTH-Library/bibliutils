#!/usr/bin/env python

"""
A really simple script just to demonstrate packaging
"""

import sys, os
from bibliutils import bibapi
from bibliutils import bibformat


if __name__ == "__main__":
    MyClient = bibapi.BibAPI()

    #The same BibAPI client object can be used for all services

    #################
    ### ALTMETRIC ###
    # N.B. This is for Altmetric Public API (not Altmetric Explorer API)

    ## Display documentation URL
    MyClient.doc(service='altmetric')
    ## Search for a document's Altmetric record
    Result1 = MyClient.altmetric(path='doi/10.1002/ijc.11382')

    #The complete result given by the API as a JSON object
    print(Result1)
    #Some specific fields
    print(Result1["title"])
    print(Result1["score"]) #Altmetric score
    print(Result1["cited_by_tweeters_count"])

    #We can see the URL that was called by the client
    print(MyClient.lasturl)

    ###############
    ### DOI.ORG ###

    ## Display documentation URL
    MyClient.doc(service='doi')

    ## DOI info lookup
    Result2 = MyClient.doi(path='10.1002/ijc.11382')
    print(Result2)

    ## bibapi.doi_handle: a dedicated function (using the BibAPI class) returning a DOI's corresponding URL
    Result3 = bibapi.doi_handle('10.1002/ijc.11382')
    print(Result3)

    ###########
    ### ROR ###

    ## Display documentation URL
    MyClient.doc(service='ror')

    ## Affiliation search
    Result4 = MyClient.ror(params={"affiliation": "Fiskeridirektoratet, Norway"})
    #print the first result
    print(Result4["items"][0])

    ## bibapi.ror_id: a dedicated function returning the ROR id of the best match
    Result5 = bibapi.ror_id("Fiskeridirektoratet, Norway")
    print(Result5)

    #################
    ### UNPAYWALL ###

    ## Display documentation URL
    MyClient.doc(service='unpaywall')

    #Fetch Unpaywall record from a DOI
    Result6 = MyClient.unpaywall(path='10.1001/JAMASURG.2018.1741')
    print(Result6["title"])
    print(Result6["oa_status"])

    #################
    ### CLARIVATE ###
    # Supported: Web of Science API Expanded ('wos'), Web of Science API Lite ('woslite')
    # Required: environment variable WOS_KEY containing the API key. To set it up from Python (which must be done BEFORE the 'import bibapi' statement), run: import os; os.environ['WOS_KEY'] = "...your key here..."
    #  N.B. only Tobias' API key and User ID are working, and only for Web of Science API Expanded ('wos')

    ## Display documentation URLs
    MyClient.doc(service='clarivate', apiname='wos')
    MyClient.doc(service='clarivate', apiname='woslite') #it seems we don't have access to Web of Science API Lite

    ## Default call
    # default API call parameters: path="", headers={"accept": 'application/json'}, proxies={}, method=None, apiname="wos"
    # default query parameters: databaseId=WOK, count = 100, firstRecord=1
    #ex: look for the first 100 results in all Web of Science collections of the query specified in "usrQuery" fed into a Web of Science search, get a JSON object as result
    Result7 = MyClient.clarivate(params = {'usrQuery': 'TI="Bob Dylan" AND AU="Larsson"'})
    print(Result7)

    ## We can change any default value by specifying it in the call
    #ex: look for 2 results ('count') starting at the 5th one ('firstRecord') among records from the Web of Science Core Collection ('databaseId') related to the UID found in the previous call ('uniqueId') published in 2016 ('publishTimeSpan'), get an XML string as result (headers['accept'])
    MyUID = Result7["Data"]["Records"]["records"]["REC"][0]["UID"]
    Result8 = MyClient.clarivate(path='related', params = {'databaseId': 'WOS', 'uniqueId': MyUID, 'count': '2', 'firstRecord': '5', 'publishTimeSpan': '2016-01-01%2B2016-12-31'}, headers = {'accept': 'application/xml'}, apiname = "wos")
    print(Result8)

    ## bibapi.wos_search: a function for simple WOS advanced search using the BibAPI class
    Result9 = bibapi.wos_search('UT=000347297400035 OR DO=10.1002/asi.23930')
    #Summary of the query 
    print(Result9["QueryResult"])
    #The only author in the first result
    print(Result9["Data"]["Records"]["records"]["REC"][0]["static_data"]["summary"]["names"]["name"]["display_name"])
    #The first author in the second result
    print(Result9["Data"]["Records"]["records"]["REC"][1]["static_data"]["summary"]["names"]["name"][0]["display_name"])


    ################
    ### ELSEVIER ###
    # Supported: Scopus API ('scopus'), ScienceDirect API ('sciencedirect')
    # Required: environment variable SCOPUS_KEY containing the API key. To set it up from Python (which must be done BEFORE the 'import bibapi' statement), run: import os; os.environ['SCOPUS_KEY'] = "...your key here..."#   (similarly, an institutional token may be defined in the environment variable SCOPUS_TOKEN)
    # Scopus API keys can be created at https://dev.elsevier.com/apikey/manage

    ## Display documentation URLs
    MyClient.doc(service='elsevier', apiname='scopus')
    MyClient.doc(service='elsevier', apiname='sciencedirect')

    ## Default call
    # default API call parameters: apiname="scopus"
    # default query parameters: httpAccept="application/json"
    #ex 1: Scopus Author retrieval
    Result10 = MyClient.elsevier(path="author/eid/9-s2.0-24802234300")
    #name
    print(Result10["author-retrieval-response"][0]["author-profile"]["preferred-name"])
    #subject areas according to Scopus
    print(Result10["author-retrieval-response"][0]["subject-areas"])
    #ex 2: Scopus search
    Result11 = MyClient.elsevier(path="search/scopus", params={"query": "TITLE(sonification) AND AUTHOR-NAME(dubus)"}, apiname="scopus")
    #total number of results
    print(Result11["search-results"]["opensearch:totalResults"])
    #second record
    print(Result11["search-results"]["entry"][1])

    ## bibapi.scopus_search: a function for simple Scopus search using the BibAPI class
    #ex: run the previous query
    Result12 = bibapi.scopus_search("TITLE(sonification) AND AUTHOR-NAME(dubus)")
    print(Result12["search-results"]["opensearch:totalResults"])
    print(Result12["search-results"]["entry"][1])

    ## We can change any default value by specifying it in the call
    #ex: ScienceDirect article retrieval, get an XML string as result
    Result13 = MyClient.elsevier(path="article/doi/10.1016/j.foreco.2007.03.035", params={"httpAccept": 'text/xml'}, apiname="sciencedirect")
    print(Result13)

    ## bibapi.get_dates_sciencedirect: a more complex function using the BibAPI class to call the ScienceDirect API and fetch the "Received date" and "Accepted date"
    #N.B. For the function to work, terms for data mining must have been accepted during your Scopus API key creation
    #WARNING: this doesn't seem to work anymore?
    Result14 = bibapi.get_dates_sciencedirect(idtype='pubmed_id', idval='24662697')
    print(Result14)
