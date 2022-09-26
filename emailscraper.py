import os
import requests
import requests_html
import sys
import re
import argparse
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

class pages:
    main = """
                             (                                
                        (    )\ )                             
     (      )      ) (  )\  (()/(    (      )         (  (    
     )\    (    ( /( )\((_)  /(_)) ( )(  ( /( `  )   ))\ )(   
    ((_)   )\  ')(_)|(_)_   (_))   )(()\ )(_))/(/(  /((_|()\  
    | __|_((_))((_)_ (_) |  / __| ((_|(_|(_)_((_)_\(_))  ((_) 
    | _|| '  \() _` || | |  \__ \/ _| '_/ _` | '_ \) -_)| '_| 
    |___|_|_|_|\__,_||_|_|  |___/\__|_| \__,_| .__/\___||_|   
                                         |_|
                                                by saschato              
"""
    output = """

 /$$$$$$$$                         /$$ /$$          
| $$_____/                        |__/| $$          
| $$       /$$$$$$/$$$$   /$$$$$$  /$$| $$  /$$$$$$$
| $$$$$   | $$_  $$_  $$ |____  $$| $$| $$ /$$_____/
| $$__/   | $$ \ $$ \ $$  /$$$$$$$| $$| $$|  $$$$$$ 
| $$      | $$ | $$ | $$ /$$__  $$| $$| $$ \____  $$
| $$$$$$$$| $$ | $$ | $$|  $$$$$$$| $$| $$ /$$$$$$$/
|________/|__/ |__/ |__/ \_______/|__/|__/|_______/ 
                                                    
                                        Email Scraper v0.1
                                        by saschato

"""

class mailscraper_render:
    def __init__(self,url):
        self.url = url

class mailscraper:
    regex = [
        "[a-z0-9]+@[a-z0-9]{1,61}\.[a-z0-9]{1,12}",
        "[a-z0-9]+@[a-z]{1,20}.[a-z]{1,20}\.[a-z]{1,10}" # point in the middle is for - in a domain like xyz-abc.de
    ]
    def __init__(self,url):
        self.url = url
        self.domain = self.url.replace("https://","") if "https://" in self.url else self.url.replace("http://","")
        self.sites = list()
        self.emails = list()

    def check_url(self,url):
        regex = [
            "https:\/\/[a-z0-9]{1,20}\.[a-z0-9]{1,12}", # no '-' in domain without subdomain
            "https:\/\/[a-z]{1,20}\.[a-z0-9]{1,20}\.[a-z0-9]{1,12}", # no '-' in domain with subdomain
            "https:\/\/[a-z]{1,20}.[a-z]{1,16}\.[a-z]{1,10}", # 1 '-' in domain and no subdomain
            "https:\/\/[a-z]{1,16}\.[a-z]{1,20}.[a-z]{1,16}\.[a-z]{1,10}" # 1 '-' in domain and subdomain
        ]
        
        if self.domain in url:
            results = []
            for expression in regex:
                results.append(re.findall(expression,url))

            for result in results:
                if result != [] and self.domain in result[0]:
                    return True
            
            return False
        else:
            return False
    
    # starting download with main page
    def start(self):
        mainpage = requests.get(self.url,headers={"user-agent":"iPhone"}).text
        self.extract(mainpage,self.url)
        soup = BeautifulSoup(mainpage,"html.parser")

        urls = []

        for link in soup.find_all("a"):
            try:
                href = link["href"]
            except:
                continue # log

            if href.startswith("/"):
                site = self.url + href
            else:
                site = href
        
            # checking domain
            if self.check_url(site):
                if not site in self.sites:
                    self.sites.append(site)
                    urls.append(site)

        with ThreadPoolExecutor(16) as TPE:
            TPE.map(self.download,urls)

    def download(self,url):
        try:
            html = requests.get(url,headers={"user-agent":"iPad"}).text
        except:
            return #log

        self.extract(html,url)
        soup = BeautifulSoup(html,"html.parser")
        
        for link in soup.find_all("a"):
            try:
                href = link["href"]
            except:
                continue # log

            if href.startswith("/"):
                site = self.url + href
            else:
                site = href
            
            if ".jpg" in site.lower() or ".pdf" in site.lower() or ".png" in site.lower():
                continue
        
            # checking domain
            if self.check_url(site):
                if not site in self.sites:
                    self.sites.append(site)
                    print(f"\n [+] {site}",end="")
                    self.download(site)
                else:
                    continue

    def extract(self,site,url):
        # seraches for emails using regular expression
        for expression in mailscraper.regex:
            found = re.findall(expression,site)
            for mail in found:
                if not mail in self.emails:
                    #print(url,mail)
                    self.emails.append(mail)
        
if __name__ == "__main__":
    # creating argument parser
    argparser = argparse.ArgumentParser()

    # adding argument
    argparser.add_argument("-m","--mode")

    # parsing arg parser
    args = argparser.parse_args()

    # printing main screen
    print(pages.main)

    # checking mode
    if args.mode == "norender":
        url = input("\n [+] enter target url: ")
        if not url.startswith("http"):
            sys.exit()
        
        # start scraping
        ms = mailscraper(url)
        ms.start()
    elif args.mode == "render":
        pass
    else:
        sys.exit()

    # printing the result
    print(pages.output)
    for mail in ms.emails:
        print(f" [+] {mail}")
