#!/usr/bin/python

###########
## NOTES ##
## This module presents a set of functions performing format check for diverse identifiers used in library/bibliometric works. The supported identifiers so far are:
## DOI, ISBN, ISSN, PMID (PubMed ID), ScopusID (the identifier called "EID" on Scopus), UT (from Web of Science)
## Functions are in the form "fix_...(ustring)" where ustring is a unicode string to be ckecked. The function returns:
## - the input string itself if it follows the identifier format
## - a part of the input string following the identifier format if there is one
## - an empty string else
## There is an option in each function to perform an online check, that is, to verify if the identifier is recognized by a corresponding remote service.
## Use: "fix_...(ustring, online_check=True)"
## With this option activated, the function returns an empty string if the identifier is not recognized, even if its format is correct
############


#IMPORTANT: Online check uses functions from the library bibapi that require API keys for Scopus and Web of Science to be defined in environment variables
#uncomment the line below and define your Scopus API key
#os.environ['SCOPUS_KEY'] =
#uncomment the line below and define your Scopus institutional token below if you have one associated with your key
#os.environ['SCOPUS_TOKEN'] =
#uncomment the line below and define your Web of Science API key
#os.environ['WOS_KEY'] =

import os
import requests
import bibformat


### DOI ###
#Wrong format returns an empty string
bibformat.fix_doi("Random_string!?")
bibformat.fix_doi("10.1364/JOSA.18.000337")
bibformat.fix_doi("10.1002/(SICI)1520-6823(1997)5:4<206::AID-ROI6>3.0.CO;2-1")
#Removes the bad parts in case of partially right format 
bibformat.fix_doi("DOI: 10.1364/JOSA.18.000337")
bibformat.fix_doi("https://dx.doi.org/10.1364/JOSA.18.000337")
#Can be used to find a DOI on a webpage
req1 = requests.get('https://kth.diva-portal.org/smash/record.jsf?pid=diva2:1414460')
bibformat.fix_doi(req1.text)
#Option to verify that there exists a handle at doi.org (returns the DOI if yes, an empty string if no)
bibformat.fix_doi("10.1364/JOSA.18.000337", online_check=True, check_what="handle")
bibformat.fix_doi("10.9999/99999")
bibformat.fix_doi("10.9999/99999", online_check=True, check_what="handle")
#Option to verify that the handle from doi.org leads to an actual web location
bibformat.fix_doi("10.1364/JOSA.18.000337", online_check=True, check_what="content")
bibformat.fix_doi("10.5555/515151")
bibformat.fix_doi("10.5555/515151", online_check=True, check_what="handle")
bibformat.fix_doi("10.5555/515151", online_check=True, check_what="content")
#Function to check if the DOI is based on an ISBN
bibformat.doi_is_from_isbn("10.1364/JOSA.18.000337")
bibformat.doi_is_from_isbn("10.1057/978-1-137-54575-6")


### ISSN ###
#Same principle as above
#NB: Check digit not verified in the format check
bibformat.fix_issn("Random_string!?")
bibformat.fix_issn("14775751") #format without dash not accepted
bibformat.fix_issn("1477-5751")
#Option to verify that the ISSN is registered on portal.issn.org
bibformat.fix_issn("1477-5751", online_check=True)
bibformat.fix_issn("0000-0000")
bibformat.fix_issn("0000-0000", online_check=True)


### PMID ###
#Same principle as above
bibformat.fix_pmid("PMID:5843660")
#Option to verify that the record exists on PubMed
bibformat.fix_pmid("5843660", online_check=True)
bibformat.fix_pmid("203957354093259284205")
bibformat.fix_pmid("203957354093259284205", online_check=True)


### ISBN ###
#Same principle as above
#ISBN-10 and ISBN-13 are recognized with or without dashes
#NB: Check digit not verified in the format check
bibformat.fix_isbn("9780141040349")
bibformat.fix_isbn("978-0-14-104034-9")
bibformat.fix_isbn("3-86717-055-X")
#Option to verify if a corresponding book can be found (uses in sequence: Google Books API, Open Library Book API, isbnsearch.org, www.books-by-isbn.com)
bibformat.fix_isbn("978-0-14-104034-9", online_check=True)
bibformat.fix_isbn("012-3-45-678901-2")
bibformat.fix_isbn("012-3-45-678901-2", online_check=True)
#This function indicates where the ISBN was found
bibformat.isbn_has_content("978-0-14-104034-9", verbose=True)
#Similarly to other identifiers, this can be used to extract an ISBN number from a long text, for example on a webpage
req2 = requests.get('http://libris.kb.se/bib/14701172')
bibformat.fix_isbn(req2.text)
#If are several ISBN numbers in the text, only the first one is returned
req3 = requests.get('https://www.amazon.com/Interactive-Computer-aided-Expressive-Music-Performance/dp/9175010313', headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'})
bibformat.fix_isbn(req3.text)


### Scopus ID ###
#Same principle as above
bibformat.fix_scopusid("2-s2.0-84870230502")
#IMPORTANT: Online check uses functions from the library bibapi that require a Scopus API key to be defined in an environment variable. See how to do this temporarily at the top at this file (it should be done before importing bibformat)
bibformat.fix_scopusid("2-s2.0-84870230502", online_check=True)
bibformat.fix_scopusid("2-s2.0-00000000001")
bibformat.fix_scopusid("2-s2.0-00000000001", online_check=True)

### UT ###
#Same principle as above
bibformat.fix_ut("000380087400009")
bibformat.fix_ut("A1980HY50600004") #old format
#IMPORTANT: Online check uses functions from the library bibapi that require a Web of Science API key to be defined in an environment variable. See how to do this temporarily at the top at this file (it should be done before importing bibformat)
bibformat.fix_ut("000380087400009", online_check = True)
bibformat.fix_ut("000999999999999")
bibformat.fix_ut("000999999999999", online_check = True)


### Other custom identifier: KTH ID ###
bibformat.fix_kthid("u14h36o6") #right
bibformat.fix_kthid("ul4h36o6") #wrong

### Via a regular expression ###
bibformat.fix_identifier("For any question about this program, write to dubus@kth.se", regexp=r'[A-z]+@[A-z]+.[A-z]+')

