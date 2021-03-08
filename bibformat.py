#!/usr/bin/python

#Author: Gaël Dubus / KTH Library / dubus@kth.se

### FORMAT CHECK ###
import re

##Attempts to recognize an identifier string
##Returns the recognized identifier or an empty string ifthe format is wrong
##Online check possible by providing an online method, see examples below
##Predefined types supported: DOI, ISBN, ISSN, PMID, Scopus ID (EID), UT (aka ISI)
def fix_identifier(ustring,idtype=None,online_method=None,regexp=None,headers={},proxies={}):
    idtype = str(idtype)
    if regexp:
        #Passing regexp in argument overrides the predefined regular expressions
        pass
    elif idtype.lower() == 'doi':
        #regexp = r'\b(10.\d{4,}(\/|%2F)(?:(?!["&\' ,<>#?{}^\[\]`|+%])\S|(%[\da-fA-F]{2,2}))+)' #strict (exclude non-compliance to recommended encoding, ref: https://www.doi.org/doi_handbook/2_Numbering.html#2.5.2.4)
        regexp = r'\b(10.\d{4,}(\/|%2F)(?:(?![" #?%])\S|(%[\da-fA-F]{2,2}))+)' #permissive (exclude non-compliance to mandatory encoding only, same ref)
    elif idtype.lower() == 'isbn':
        regexp = r'\b(\d[- ]*){12}\d|\b(\d[- ]*){9}[\dxX]\b'
    elif idtype.lower() == 'issn':
        regexp = r'\b\d{4}-\d{3}[\dxX]\b'
    elif idtype.lower() == 'pmid':
        regexp = r'\b\d+\b'
    elif idtype.lower() == 'scopusid':
        regexp = r'2-s2\.0-\d{10,11}'
    elif idtype.lower() == 'ut' or idtype.lower() == 'isi':
        regexp = r'A19\d{2}[A-Z\d]{5}\d{5}|000\d{12}'
    else:
        print("Unknown identifier type: " + idtype)
        return ""
    match = re.search(regexp,ustring)
    if match:
        the_id = match.group(0)
        isFound = True
        if online_method:
            online_res = online_method(the_id,headers=headers,proxies=proxies)
            if not online_res:
                isFound = False
        return isFound*the_id
    else:
        return ""



### ONLINE CHECKS ###
import bibapi
import requests

#Method for checking that an identifier corresponds to a correct web location
def identifier_has_location(idstring,idtype=None,urlbase=None,timeout=10,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'},proxies={}):
    idtype = str(idtype)
    if urlbase:
        pass
    elif idtype == 'doi':
        urlbase = "doi.org"
    elif idtype == 'issn':
        urlbase = "portal.issn.org/resource/ISSN"
    elif idtype == 'pmid':
        urlbase = "www.ncbi.nlm.nih.gov/pubmed"
    else:
        print("Identifier type " + idtype + " not supported")
    try:
        req = requests.get("https://" + urlbase + "/" + idstring, timeout=timeout, headers=headers, proxies=proxies)
        if idtype == 'issn':
            isFound = (fix_issn(req.text, False) != "")
        else:
            isFound = req.status_code == 200
    except requests.exceptions.RequestException:
        print('\nWARNING: "requests.get()" raised an exception for ' + idstring + ', treated as not found')
        isFound = False
    return isFound

def doi_has_content(ustring,headers={},proxies={}):
    return identifier_has_location(ustring,idtype='doi')

def pmid_has_content(ustring,headers={},proxies={}):
    return identifier_has_location(ustring,idtype='pmid')

def issn_has_content(ustring,headers={},proxies={}):
    return identifier_has_location(ustring,idtype='issn')

def scopusid_has_content(ustring,headers={},proxies={}):
    rec = bibapi.scopus_search("EID(" + ustring + ")")
    nres = int(bibapi.safe_access(rec,['search-results','opensearch:totalResults'],'0'))
    return nres > 0

def ut_has_content(ustring,headers={},proxies={}):
    rec = bibapi.wos_search("UT=" + ustring)
    nres = bibapi.safe_access(rec,['QueryResult','RecordsFound'],0)
    return nres > 0


import json

def isbn_has_content(ustring,verbose=False,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'},proxies={}):
    #Special case of an empty string (some services can return a false positive)
    if not(ustring):
        return ""
    isbncand = ustring.replace('-','').replace(' ','')
    LocList = ["Google Books API", "Open Library Book API", "ISBN search", "Books by ISBN"]
    acc = 0
    try:
        req = requests.get("https://www.googleapis.com/books/v1/volumes?q=isbn:" + isbncand, timeout=10, headers=headers, proxies=proxies)
        isFound = req.json()["totalItems"] > 0
    except requests.exceptions.RequestException:
        print('\nWARNING: "requests.get()" raised an exception for ' + ustring + ', treated as not found')
        isFound = False
    if not isFound:
        acc += 1
        try:
            req = requests.get("https://openlibrary.org/api/books?bibkeys=ISBN:" + isbncand + "&format=json", timeout=10, headers=headers, proxies=proxies)
            isFound = len(req.json()) > 0
        except requests.exceptions.RequestException:
            print('\nWARNING: "requests.get()" raised an exception for ' + ustring + ', treated as not found')
    if not isFound:
        acc += 1
        try:
            req = requests.get("https://isbnsearch.org/isbn/" + isbncand, timeout=10, headers=headers, proxies=proxies)
            isFound = req.status_code == 200
        except requests.exceptions.RequestException:
            print('\nWARNING: "requests.get()" raised an exception for ' + ustring + ', treated as not found')
    if not isFound:
        acc += 1
        try:
            req = requests.get("https://www.books-by-isbn.com/" + isbncand, timeout=10, headers=headers, proxies=proxies)
            isFound = (req.status_code == 200) and ("No page yet on ISBN" not in req.text)
        except requests.exceptions.RequestException:
            print('\nWARNING: "requests.get()" raised an exception for ' + ustring + ', treated as not found')
    if verbose and isFound:
        print("Found via " + LocList[acc])
    return isFound


### IDTYPE-SPECIFIC FUNCTIONS ###

##Attempts to recognize a PMID identifier from a string
##Returns the recognized PMID or an empty string if the format is wrong
##Online check (if set to True) via PubMed
def fix_pmid(ustring,online_check=False,headers={},proxies={}):
    if online_check:
        return fix_identifier(ustring,'pmid',online_method=pmid_has_content,headers=headers,proxies=proxies)
    else:
        return fix_identifier(ustring,'pmid')

##Attempts to recognize a DOI identifier from a string
##Returns the recognized DOI or an empty string if the format is wrong
##Online check (if set to True) that there exists a handle at doi.org (check_what="handle") or that the handle leads to an actual web location (check_what="content")
def fix_doi(ustring,online_check=False,check_what="handle",headers={},proxies={}):
    if online_check:
        if check_what == "handle":
            return fix_identifier(ustring,'doi',online_method=bibapi.doi_handle,headers=headers,proxies=proxies)
        elif check_what == "content":
            return fix_identifier(ustring,'doi',online_method=doi_has_content,headers=headers,proxies=proxies)
        else:
            print("ERROR: in function \'fix_doi\': the value of parameter \'check_what\' should be either \'handle\' or \'content\'")
            return ""
    else:
        return fix_identifier(ustring,'doi')

##Attempts to recognize an ISBN identifier from a string
##Returns the recognized ISBN or an empty string if the format is wrong
##Online check (if set to True) via Google Books API, Open Library Book API, isbnsearch.org, www.books-by-isbn.com
def fix_isbn(ustring,online_check=False,headers={},proxies={}):
    if online_check:
        return fix_identifier(ustring,'isbn',online_method=isbn_has_content,headers=headers,proxies=proxies)
    else:
        return fix_identifier(ustring,'isbn')

##Attempts to recognize an ISSN identifier from a string
##Returns the recognized ISSN or an empty string if the format is wrong
##Online check (if set to True) via portal.issn.org
def fix_issn(ustring,online_check=False,headers={},proxies={}):
    if online_check:
        return fix_identifier(ustring,'issn',online_method=issn_has_content,headers=headers,proxies=proxies)
    else:
        return fix_identifier(ustring,'issn')

##Attempts to recognize a Scopus EID identifier from a string
##Returns the recognized Scopus EID or an empty string if the format is wrong
##Online check (if set to True) via Scopus API (requires bibapi and an API key)
def fix_scopusid(ustring,online_check=False,headers={},proxies={}):
    if online_check:
        return fix_identifier(ustring,'scopusid',online_method=scopusid_has_content,headers=headers,proxies=proxies)
    else:
        return fix_identifier(ustring,'scopusid')

##Attempts to recognize a Scopus EID identifier from a string
##Returns the recognized Scopus EID or an empty string if the format is wrong
##Online check (if set to True) via Web of Science API Expanded (requires bibapi and an API key)
def fix_ut(ustring,online_check=False,headers={},proxies={}):
    if online_check:
        return fix_identifier(ustring,'ut',online_method=ut_has_content,headers=headers,proxies=proxies)
    else:
        return fix_identifier(ustring,'ut')


    
### OTHER USES ###

##Checks if the DOI is based on an ISBN
def doi_is_from_isbn(ustring):
    lastbit = ustring.split('/')[-1]
    return (fix_doi(ustring) != "") and (lastbit == fix_isbn(lastbit))


#Identifier with a specific format

##Attempts to recognize a KTHID identifier from a string
##Returns the recognized KTHID or an empty string if the format is wrong
def fix_kthid(ustring,idtype="person"):
    if idtype == "person":
        typecode = '1'
    elif idtype == "unit":
        typecode = '2'
    kthid_regexp = r'u' + typecode + '([a-z]|[0-9]){6}'
    return fix_identifier(ustring,regexp=kthid_regexp)



