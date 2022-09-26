import os
import requests
import requests_html
import sys
import re
import argparse
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

class pages:
    clear = os.system("cls")
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
        "[a-z0-9]+@[a-z]{1,20}\.[a-z]{1,10}",
        "[a-z0-9]+@[a-z]{1,20}.[a-z]{1,20}\.[a-z]{1,10}", # point in the middle is for - in a domain like xyz-abc.de
        "[a-z0-9]{1,20}\@[a-z]+.[a-z]+.[a-z]+\.[a-z]{1,10}", # point in the middle is for - in a domain like xyz-ada-abc.de
        "[a-z0-9]{1,20}\@[a-z]+.[a-z]+.[a-z]+.[a-z]+\.[a-z]{1,10}"
    ]
    depth = 4
    software_names = [SoftwareName.CHROME.value]
    operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value] 

    def __init__(self,url):
        self.url = url
        self.domain = self.url.replace("https://","") if "https://" in self.url else self.url.replace("http://","")
        self.sites = list()
        self.emails = list()
        self.user_agent_rotator = UserAgent(software_names=mailscraper.software_names, operating_systems=mailscraper.operating_systems, limit=1000)

    def check_url(self,url):
        regex = [
            "https:\/\/[a-z0-9]{1,20}\.[a-z0-9]{1,12}", # no '-' in domain no subdomain
            "https:\/\/[a-z]{1,20}\.[a-z0-9]{1,20}\.[a-z0-9]{1,12}", # no '-' in domain + subdomain
            "https:\/\/[a-z]{1,20}.[a-z]{1,16}\.[a-z]{1,10}", # 1 '-' in domain and no subdomain
            "https:\/\/[a-z]{1,16}\.[a-z]{1,20}.[a-z]{1,16}\.[a-z]{1,10}", # 1 '-' in domain + subdomain
            "https:\/\/[a-z]+.[a-z]+.[a-z]+\.[a-z]{1,10}", # 2 '-' in domain no subdomain
            "https:\/\/[a-z]{1,20}\.[a-z]+.[a-z]+.[a-z]+\.[a-z]{1,10}", # 2 '-' in domain + subdomain
            "https:\/\/[a-z]+.[a-z]+.[a-z]+.[a-z]+\.[a-z]{1,10}",
            "https:\/\/[a-z]{1,20}\.[a-z]+.[a-z]+.[a-z]+.[a-z]+\.[a-z]{1,10}"
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
        mainpage = requests.get(self.url,headers={"user-agent":self.user_agent_rotator.get_random_user_agent()}).text
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

    def download(self,url,depth=None):
        if depth == mailscraper.depth:
            return
        try:
            html = requests.get(url,headers={"user-agent":self.user_agent_rotator.get_random_user_agent()}).text
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
            
            if ".jpg" in site.lower() or ".pdf" in site.lower() or ".png" in site.lower() or ".jpeg" in site.lower() or ".mp4" in site.lower():
                continue
        
            # checking domain
            if self.check_url(site):
                if not site in self.sites:
                    self.sites.append(site)
                    print(f"\n [+] {site}",end="")
                    depth += 1
                    self.download(site,depth)
                else:
                    continue

    def extract(self,site,url):
        # seraches for emails using regular expression
        for expression in mailscraper.regex:
            found = re.findall(expression,site)
            for mail in found:
                if not mail in self.emails:
                    self.emails.append(mail)
        
if __name__ == "__main__":
    # creating argument parser
    argparser = argparse.ArgumentParser()

    # adding arguments
    argparser.add_argument("-m","--mode",default="norender",required=False)
    argparser.add_argument("-d","--depth",required=False)

    # parsing arg parser
    args = argparser.parse_args()

    # printing main screen
    pages.clear
    print(pages.main)

    # checking mode
    if args.mode == "norender":
        url = input("\n [+] enter target url: ")
        if not url.startswith("http"):
            sys.exit()
        
        # config of scraper
        ms = mailscraper(url)
        
        # setting depth
        if args.depth:
            ms.depth = int(args.depth)
        
        # start scraping
        ms.start()
    elif args.mode == "render":
        pass
    else:
        sys.exit()

    # printing the result
    print("\n\n\n")
    print(pages.output)
    for mail in ms.emails:
        print(f" [+] {mail}")
