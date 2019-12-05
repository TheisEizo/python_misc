import requests
from bs4 import BeautifulSoup
from datetime import datetime

def crawler(start, agent=None, depth=1, base=None, base_filter=None):
    """
    The Crawler v. 1.0
    Web crawler for stationary, non-paging web pages
    
    Input parameters:
    start:  an url, where the crawler start gathering data from
    agent:  an requests header with agent information
    depth:  number of degrees, the crawer should crawl. NB! Keep this number low.
    base:   a start to each url, which the crawler will try adding
    base_filter:  filter crawl-able links to have this base 
            (if base=True, the start url will be used) 
    
    Returns
    res  :  a dict with urls as keys and an value-dict as value for each of these keys.
            the value-dict has "links", "data" og "visited" as keys:
                "links":   a list with all out going links from key-url
                "data":    a BeautifulSoup soup-element with data from key-url
                "visited": boolean used by the crawler to keep track of visited urls
                "time":    when visited
    """
    
    def get_urls_data(url, base=None, agent=None): #get urls and data
        #takes url (and possibly an agent) and returns a tuple with:
        #    a list with all out going links from url
        #    a BeautifulSoup soup-element with data from url
        
        def get_hrefs(soup): #get Links
            #takes a BeautifulSoup soup-element and returns a list with
            #    all links ('href') from that soup
            return [link.get('href') for link in soup.find_all('a')]
        
        try:
            html = requests.get(url,headers=agent)
        except ValueError: # catch ValueErrors
            try: #try adding base in front of url for  some internal urls
                html = requests.get(base+url,headers=agent)
            except requests.exceptions.HTTPError:
                raise ValueError # converts HTTP errors to ValueErrors
    
        soup = BeautifulSoup(html.text, features='lxml') #create soup
        return get_hrefs(soup), soup #return tuple with links and soup

    if base_filter == True: base_filter = start #if true, use start url as base
    d, res = depth, {start: {'visited':False}} #set up depth stationary and res output
    while depth >= 0: #depth variable decresess while looping
        res_len = len(res.keys()) #count number of urls visited for early termination
        
        new_urls = [] #empty list for new urls each loop
        
        for url in res.keys():
            # dont visit same page twice
            if res[url]['visited'] == True:
                pass 
            else:
                #get and add url to res dict
                try:
                    urls, data = get_urls_data(url, base, agent) #get urls and data
                    #add urls and data to res dict plus change visited to true
                    res[url] = {'links':urls, 
                                'data':data, 
                                'visited':True, 
                                'time':str(datetime.now())} 
                    #add urls to new urls list as well
                    new_urls.extend(urls)
                except ValueError: #if bad link, add it to the dict with value error as data
                    res[url] = {'urls':None, 
                                'data':ValueError, 
                                'visited':True, 
                                'time':str(datetime.now())}
        new_urls = list(set(new_urls)) #make sure all links are unique
        for url in new_urls: #check all new urls for
            if not url: #none urls
                pass
            else:
                if base_filter: #check if filtering
                    if (url in res.keys()) or (len(url) <= len(base_filter)):
                        pass #already visited, too short urls
                    elif (url[:len(base_filter)] != base_filter):
                        pass #filter for base url
                    else:
                        res[url] = {'visited':False} #add the url to res dict
                else:
                    res[url] = {'visited':False} #add the url to res dict
        
        if len(res.keys()) == res_len: #if no new urls is added to res dict, terminate
            print('Depth: {} - No new links found'.format(d-depth))
            depth = -1
        else: 
            print('Depth: {} - Tot. number of links: {}'.format(d-depth,len(res.keys())))
            depth -= 1 #show status and decrese depth variable
    return res #return res dict

#url = 'https://theizo.com/'
#url = 'https://en.wikipedia.org/wiki/'
#agent = {'Name': 'Theis Eizo', 
#         'Mail': 'theizo.bedsted@gmail.com'}
#res = crawler(url, agent, 2, None, True)

#from pprint import pprint
#pprint(list(res.keys()))
