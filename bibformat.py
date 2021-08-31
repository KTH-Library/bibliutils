#!/usr/bin/python

#Author: Gaël Dubus / KTH Library / dubus@kth.se

### FORMAT CHECK ###
import re

##Attempts to recognize an identifier string
##Returns the recognized identifier or an empty string ifthe format is wrong
##Online check possible by providing an online method, see examples below
##Predefined types supported: DOI, ISBN, ISSN, PMID, Scopus ID (EID), UT (aka ISI)
def fix_identifier(ustring,idtype=None,online_method=None,checksum=True,regexp=None,headers={},proxies={},timeout=None):
    idtype = str(idtype)
    do_check_digit = False
    check_digit_method = None
    if regexp:
        #Passing regexp in argument overrides the predefined regular expressions
        pass
    elif idtype.lower() == 'doi':
        #regexp = r'\b(10.\d{4,}(\/|%2F)(?:(?!["&\' ,<>#?{}^\[\]`|+%])\S|(%[\da-fA-F]{2,2}))+)' #strict (exclude non-compliance to recommended encoding, ref: https://www.doi.org/doi_handbook/2_Numbering.html#2.5.2.4)
        regexp = r'\b(10.\d{4,}(\/|%2F)(?:(?![" #?%])\S|(%[\da-fA-F]{2,2}))+)' #permissive (exclude non-compliance to mandatory encoding only, same ref)
    elif idtype.lower() == 'isbn':
        regexp = r'\b(\d[- ]*){12}\d|\b(\d[- ]*){9}[\dxX]\b'
        do_check_digit = checksum
        check_digit_method = isbn_checkdigit
    elif idtype.lower() == 'issn':
        regexp = r'\b\d{4}-\d{3}[\dxX]\b'
        do_check_digit = checksum
        check_digit_method = issn_checkdigit
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
        isFound = not do_check_digit or check_digit_method(the_id)
        if isFound and online_method:
            online_res = online_method(the_id,headers=headers,proxies=proxies,timeout=timeout)
            if not online_res:
                isFound = False
        return isFound*the_id
    else:
        return ""



### ONLINE CHECKS ###
import bibapi_v2
import requests
import json

#Method for checking that an identifier corresponds to a correct web location
def identifier_has_location(idstring,idtype=None,urlbase=None,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'},proxies={},timeout=None):
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
        req = requests.get("https://" + urlbase + "/" + idstring, headers=headers, proxies=proxies, timeout=timeout)
        if idtype == 'issn':
            isFound = (fix_issn(req.text, False) != "")
        else:
            isFound = req.status_code == 200
    except requests.exceptions.RequestException as e:
        print('\nWARNING: "requests.get()" raised an exception for ' + idtype + ':' + idstring + ', treated as not found\nException: ' + str(e) + (proxies != {})*('\nProxies: ' + str(proxies)))
        isFound = False
    return isFound

def doi_has_content(ustring,headers={},proxies={},timeout=None):
    return identifier_has_location(ustring,idtype='doi',headers=headers,proxies=proxies,timeout=timeout)

def pmid_has_content(ustring,headers={},proxies={},timeout=None):
    return identifier_has_location(ustring,idtype='pmid',headers=headers,proxies=proxies,timeout=timeout)

def issn_has_content(ustring,headers={},proxies={},timeout=None):
    return identifier_has_location(ustring,idtype='issn',headers=headers,proxies=proxies,timeout=timeout)

def scopusid_has_content(ustring,headers={},proxies={},timeout=None):
    rec = bibapi_v2.scopus_search("EID(" + ustring + ")",headers=headers,proxies=proxies,timeout=timeout)
    nres = int(bibapi_v2.safe_access(rec,['search-results','opensearch:totalResults'],'0'))
    return nres > 0

def ut_has_content(ustring,headers={},proxies={},timeout=None):
    rec = bibapi_v2.wos_search("UT=" + ustring,headers=headers,proxies=proxies,timeout=timeout)
    nres = bibapi_v2.safe_access(rec,['QueryResult','RecordsFound'],0)
    return nres > 0

def isbn_has_content(ustring,verbose=False,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'},proxies={},timeout=None):
    #Special case of an empty string (some services can return a false positive)
    if not(ustring):
        return False
    isbncand = ustring.replace('-','').replace(' ','')
    LocList = ["Libris","Google Books API","Open Library Book API","ISBN search","Books by ISBN"]
    acc = 0
    try:
        isFound = (bibapi_v2.safe_access(bibapi_v2.libris_isbn_search(isbncand, headers=headers, proxies=proxies, timeout=timeout),["xsearch","records"],0) > 0)
    except requests.exceptions.RequestException as e:
        print('\nWARNING: "requests.get()" raised an exception for isbn:' + ustring + ', treated as not found\nException: ' + str(e) + (proxies != {})*('\nProxies: ' + str(proxies)))
        isFound = False
    if not isFound:
        acc += 1
        try:
            req = requests.get("https://www.googleapis.com/books/v1/volumes?q=isbn:" + isbncand, headers=headers, proxies=proxies, timeout=timeout)
            isFound = req.json()["totalItems"] > 0
        except requests.exceptions.RequestException as e:
            print('\nWARNING: "requests.get()" raised an exception for isbn:' + ustring + ', treated as not found\nException: ' + str(e) + (proxies != {})*('\nProxies: ' + str(proxies)))
    if not isFound:
        acc += 1
        try:
            req = requests.get("https://openlibrary.org/api/books?bibkeys=ISBN:" + isbncand + "&format=json", headers=headers, proxies=proxies, timeout=timeout)
            isFound = len(req.json()) > 0
        except requests.exceptions.RequestException as e:
            print('\nWARNING: "requests.get()" raised an exception for isbn:' + ustring + ', treated as not found\nException: ' + str(e) + (proxies != {})*('\nProxies: ' + str(proxies)))
        except ValueError:
            print('\nWARNING: Open Library service appears to be offline for isbn:' + ustring + ', treated as not found')
    if not isFound:
        acc += 1
        try:
            req = requests.get("https://isbnsearch.org/isbn/" + isbncand, headers=headers, proxies=proxies, timeout=timeout)
            isFound = req.status_code == 200
        except requests.exceptions.RequestException as e:
            print('\nWARNING: "requests.get()" raised an exception for isbn:' + ustring + ', treated as not found\nException: ' + str(e) + (proxies != {})*('\nProxies: ' + str(proxies)))
    if not isFound:
        acc += 1
        try:
            req = requests.get("https://www.books-by-isbn.com/" + isbncand, headers=headers, proxies=proxies, timeout=timeout)
            isFound = (req.status_code == 200) and ("No page yet on ISBN" not in req.text)
        except requests.exceptions.RequestException as e:
            print('\nWARNING: "requests.get()" raised an exception for isbn:' + ustring + ', treated as not found\nException: ' + str(e) + (proxies != {})*('\nProxies: ' + str(proxies)))
    if verbose and isFound:
        print("Found via " + LocList[acc])
    return isFound


### IDTYPE-SPECIFIC FUNCTIONS ###

##Attempts to recognize a PMID identifier from a string
##Returns the recognized PMID or an empty string if the format is wrong
##Online check (if set to True) via PubMed
def fix_pmid(ustring,online_check=False,headers={},proxies={},timeout=None):
    if online_check:
        return fix_identifier(ustring,'pmid',online_method=pmid_has_content,headers=headers,proxies=proxies,timeout=timeout)
    else:
        return fix_identifier(ustring,'pmid')

##Attempts to recognize a DOI identifier from a string
##Returns the recognized DOI or an empty string if the format is wrong
##Online check (if set to True) that there exists a handle at doi.org (check_what="handle") or that the handle leads to an actual web location (check_what="content")
def fix_doi(ustring,online_check=False,check_what="handle",headers={},proxies={},timeout=None):
    if online_check:
        if check_what == "handle":
            return fix_identifier(ustring,'doi',online_method=bibapi_v2.doi_handle,headers=headers,proxies=proxies,timeout=timeout)
        elif check_what == "content":
            return fix_identifier(ustring,'doi',online_method=doi_has_content,headers=headers,proxies=proxies,timeout=timeout)
        else:
            print("ERROR: in function \'fix_doi\': the value of parameter \'check_what\' should be either \'handle\' or \'content\'")
            return ""
    else:
        return fix_identifier(ustring,'doi')

##Attempts to recognize an ISBN identifier from a string
##Returns the recognized ISBN or an empty string if the format is wrong
##Online check (if set to True) via Google Books API, Open Library Book API, isbnsearch.org, www.books-by-isbn.com
def fix_isbn(ustring,online_check=False,checksum=True,headers={},proxies={},timeout=None):
    if online_check:
        return fix_identifier(ustring,'isbn',online_method=isbn_has_content,checksum=checksum,headers=headers,proxies=proxies,timeout=timeout)
    else:
        return fix_identifier(ustring,'isbn',checksum=checksum)

##Attempts to recognize an ISSN identifier from a string
##Returns the recognized ISSN or an empty string if the format is wrong
##Online check (if set to True) via portal.issn.org
def fix_issn(ustring,online_check=False,checksum=True,headers={},proxies={},timeout=None):
    if online_check:
        return fix_identifier(ustring,'issn',online_method=issn_has_content,checksum=checksum,headers=headers,proxies=proxies,timeout=timeout)
    else:
        return fix_identifier(ustring,'issn',checksum=checksum)

##Attempts to recognize a Scopus EID identifier from a string
##Returns the recognized Scopus EID or an empty string if the format is wrong
##Online check (if set to True) via Scopus API (requires bibapi and an API key)
def fix_scopusid(ustring,online_check=False,headers={},proxies={},timeout=None):
    if online_check:
        return fix_identifier(ustring,'scopusid',online_method=scopusid_has_content,headers=headers,proxies=proxies)
    else:
        return fix_identifier(ustring,'scopusid')

##Attempts to recognize a Scopus EID identifier from a string
##Returns the recognized Scopus EID or an empty string if the format is wrong
##Online check (if set to True) via Web of Science API Expanded (requires bibapi and an API key)
def fix_ut(ustring,online_check=False,headers={},proxies={},timeout=None):
    if online_check:
        return fix_identifier(ustring,'ut',online_method=ut_has_content,headers=headers,proxies=proxies,timeout=timeout)
    else:
        return fix_identifier(ustring,'ut')


    
### OTHER USES ###

#Identifier with a specific format

##Attempts to recognize a KTHID identifier from a string
##Returns the recognized KTHID or an empty string if the format is wrong
def fix_kthid(ustring,idtype="person"):
    if idtype == "person":
        typecode = '1'
    elif idtype == "unit":
        typecode = '2'
    kthid_regexp = r'u' + typecode + '[a-z0-9]{6}'
    return fix_identifier(ustring,regexp=kthid_regexp)


import ftfy

##Attempts to correct a bad encoding of a Unicode string (mojibake)
##The list is not exhaustive, could be extended whenever needed
##Also uses the ftfy package for more corrections
#If the encoding types are known beforehand, use this instead:
#'GaÃ«l Ã¥ker till SÃ£o Paulo'.encode('latin-1').decode('utf-8')
def fix_bad_unicode(utfstring,added_rules=[]):
    res = utfstring    
    substitute = [
        [u'Á¯¿Å“',u'ö'],
        [u'Á“',u'Ó'],
        [u'Ó“',u'ä'],
        [u'Á”',u'Ô'],
        [u'Å“',u'œ'],
        [u'sË‡',u'š'],
        [u'Ä',u'č'],
        [u'cË‡',u'č'],
        [u'Á²',u'ò'],    
        [u'Á£',u'ã'],
        [u'Á­',u'í'],
        [u'Á¸',u'ø'],
        [u'Á«',u'ë'],
        [u'Á‡',u'Ç'],
        [u'Áœ',u'Ü'],
        [u'Á‰',u'É'],
        [u'Á¢',u'â'],
        [u'ÄŒ',u'Č'],
        [u'Á ',u'à'],
        [u'Å\'',u'ő'],
        [u'Á†',u'Æ'],
        [u'Å¡',u'š'],
        [u'Å™',u'ř'],
        [u'Å¾',u'ž'],
        [u'Å‚',u'ł'],
        [u'Å ',u'Š'],
        [u'È©',u'ę'],
        [u'Á¯',u'ï'],
        [u'Á¬',u'ì'],
        [u'Å',u'Ř'],
        [u'Ã',u'Í'],
        [u'Ã³',u'ó'],
        [u'Ã',u'Ã'],
        [u'Ä±',u'ı'],
        [u'Ç§',u'ǧ'],
        [u'Ê‡',u'ʇ'],
        [u'Á´',u'ô'],
        [u'Á¹',u'ù'],
        [u'Á½',u'ý'],
        [u'ÁŸ',u'ß'],
        [u'Áª',u'ê'],
        [u'Á ',u'á'],
        [u'Áˆ',u'È'],
        [u'Á˜',u'Ø'],
        [u'Á',u'Í'],
        [u'Áš',u'Ú'],
        [u'ÁƒƒÁ‚–',u'Ö'],                      
        [u'ÁƒƒÁ‚¶',u'ö'],                      
        [u'Á®',u'î'],
        [u'Á»',u'ü'],
        [u'Áƒ…',u'Å'],
        [u'Áƒ²',u'ò'],
        [u'Áƒ¶',u'ö'],
        [u'Áƒ©',u'é'],
        [u'Áƒ–',u'Ö'],
        [u'Áƒ¥',u'å'],
        [u'Áƒ³',u'ó'],
        [u'Á¯',u'ï'],
        [u'Å«',u'ū'],
        [u'-™',u'’'],
        [u'Ä—',u'ė'],
        [u'Å½',u'Ž'],
        [u'Ä›',u'ě'],
        [u'Ä™',u'ę'],
        [u'Å›',u'ś'],
        [u'Å°',u'Ű'],
        [u'Åž',u'Ş'],
        [u'a`§',u'a̧'],
        [u'Åˆ',u'ň'],
        [u'rÌˆ',u'r̈'],
        [u'Å˜',u'Ř'],
        [u'Å»',u'Ż'],
        [u'Åº',u'ź'],
        [u'Ä°',u'İ'],
        [u'a`',u'á'],
        [u'iÌ',u'í'],
        [u'oÌ',u'ó'],
        [u'Å„',u'ń'],
        [u'Å‘',u'ő'],
        [u'Á°',u'ð'],
        [u'Á•',u'Õ'],
        [u'Á’',u'Ò'],
        [u'Á‘',u'Ñ'],
        [u'Áž',u'Þ'],
        [u'Å†',u'ņ'],
        [u'ÁŒ',u'Ì'],
        [u'Á',u'Ý'],
        [u'Äž',u'Ğ'],
        [u'-',u'”'],
        [u'-•',u'―'],
        [u'Áƒ',u'Ã'],
        [u'Ï‡',u'χ'],
        [u'ˆ’',u'−'],
        [u'-¨',u'\u2028'],
        [u'Ëš',u'˚'],
        [u'ï¼Ÿ',u'？'],
        [u'Î¼',u'μ'],
        [u'ˆ¼',u'∼'],
        [u'Ï„',u'τ'],
        [u'Á—',u'×'],
        [u'Î½',u'ν'],
        [u'†’',u'→'],
        [u'ˆ—',u'∗'],
        [u'„“',u'ℓ'],
        [u'Á¾',u'þ'],
        [u'Á¿',u'ÿ'],
        [u'ï»¿',u'﻿﻿﻿'],
        [u'-ƒ',u'\u2003'],
        [u'Îµ',u'ε'],
        [u'Î³',u'γ'],
        [u'ÁŽ',u'Î'],
        [u'Ã¡',u'á'], 
        [u'Ãº',u'ú'],
        [u'Ã­',u'í'],
        [u'Ã¨',u'è'],
        [u'Ã½',u'ý'],
        [u'Ã®',u'î'],
        [u'Ã©',u'é'],
        [u'Ã²',u'ò'],
        [u'Ä',u'ě'],
        [u'Ä',u'Č'],
        [u'Ã ',u'à'],
        [u'Ã§',u'ç'],
        [u'Ã£',u'ã'],
        [u'Ã',u'û'],
        [u'Ãª',u'ê'],
        [u'Ã',u'É'],
        [u'Â ',u' '],
        [u'Ã¤',u'ä'],
        [u'Ã¶',u'ö'],
        [u'Ã',u'Å'],
        [u'Ã¼',u'ü'],
        [u'Ã¥',u'å'],
        [u'Ã',u'Ö'],
        [u'Ãµ',u'õ'],
        [u'Ã«',u'ë'],
        [u'Ã±',u'ñ'],
        [u'Ä',u'đ'],
        [u'Ä',u'ć'],
        [u'ÅŸ',u'ş']
    ]
        
    for rule in added_rules:
        substitute.append(rule)

    for subs in substitute:
        res = res.replace(subs[0],subs[1])
    res = ftfy.fix_text(ftfy.fix_encoding(res))
    return res


def doi_is_from_isbn(ustring):
    lastbit = ustring.split('/')[-1]
    return (fix_doi(ustring) != "") and (lastbit == fix_isbn(lastbit))


def issn_checkdigit(issn):
    if len(issn) == 9:
        sumlist = [(8-i)*int(x) for i,x in enumerate(issn[0:4])]+[(4-i)*int(x) for i,x in enumerate(issn[5:8])]
        checksum = (11-sum(sumlist)) % 11
        if checksum == 10:
            checkchar = 'x'
        else:
            checkchar = str(checksum)
        return issn[8].lower() == checkchar
    else:
        return False


def isbn_checkdigit(isbn):
    isbn_canonical = isbn.replace('-','').replace(' ','')
    if len(isbn_canonical) == 10:
        sumlist = [(10-i)*int(x) for i,x in enumerate(isbn_canonical[:-1])]
        checksum = (11-(sum(sumlist) % 11)) % 11
        if checksum == 10:
            checkchar = 'x'
        else:
            checkchar = str(checksum)
    elif len(isbn_canonical) == 13:
        sumlist = [(1+2*(i%2==1))*int(x) for i,x in enumerate(isbn_canonical[:-1])]
        checksum = (10-(sum(sumlist) % 10)) % 10
        checkchar = str(checksum)
    else:
        return False
    return isbn_canonical[-1].lower() == checkchar
