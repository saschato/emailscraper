import os
import requests
import requests_html
import sys
import re
import argparse
from bs4 import BeautifulSoup
from threading import Thread
from urllib.parse import  urljoin,urlsplit
from validate_email import validate_email
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

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
    clear = os.system("cls")

class mailscraper_render:
    regex = [
        "[a-zA-Z0-9]+@[a-z0-9]{1,61}\.[a-z]{1,12}",
        "[a-zA-Z0-9]+@[a-z0-9]{1,30}.[a-z0-9]{1,31}\.[a-z]{1,10}", # point in the middle is for - in a domain like xyz-abc.de
        "[a-zA-Z0-9]+@[a-z0-9]{1,30}.[a-z0-9]{1,31}.[a-z0-9]{1,30}\.[a-z]{1,10}",
        "[a-zA-Z0-9]+@[a-z0-9]{1,30}.[a-z0-9]{1,31}.[a-z0-9]{1,30}.[a-z0-9]{1,30}\.[a-z]{1,10}"
    ]
    user_agent_rotator = UserAgent(software_names=[SoftwareName.CHROME.value], operating_systems=[OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value], limit=100)

    def __init__(self,url):
        self.url = url
        self.domain = urlsplit(self.url)[1]
        self.session = requests_html.HTMLSession()
        self.session.headers = {"user-agent":mailscraper_render.user_agent_rotator.get_random_user_agent()}
        self.depth = 2
        self.emails = list()
        self.sites = list()

    def extract(self,site,url):
        # seraches for emails using regular expression
        for expression in mailscraper.regex:
            found = re.findall(expression,site)
            for mail in found:
                if not mail in self.emails:
                    self.emails.append(mail)
    
    def check_url(self,url):
        regex = [
            "https:\/\/[a-z0-9]{1,20}\.[a-z]{1,12}", # no '-' in domain without subdomain
            "https:\/\/[a-z0-9]{1,20}\.[a-z0-9]{1,20}\.[a-z]{1,12}", # no '-' in domain with subdomain
            "https:\/\/[a-z0-9]{1,20}.[a-z]{1,16}\.[a-z]{1,10}", # 1 '-' in domain and no subdomain
            "https:\/\/[a-z0-9]{1,16}\.[a-z0-9]{1,20}.[a-z0-9]{1,16}\.[a-z]{1,10}" # 1 '-' in domain and subdomain
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

    def download(self,url,depth):
        # checking recursion depth
        if depth == self.depth:
            sys.exit()
        else:
            depth+=1
        
        session = requests_html.HTMLSession()
        session.headers = {"user-agent":mailscraper_render.user_agent_rotator.get_random_user_agent()}

        try: 
            html = self.session.get(url)
            html.html.render(timeout=20)
        except Exception as err:
            sys.exit() #log

        self.extract(html.html.html,url)

        # extracting urls of mainpage
        soup = BeautifulSoup(html.html.html,"html.parser")
        for link in soup.find_all("a"):
            try:
                href = link["href"]
            except:
                continue

            # converting urls
            if not href.startswith("http"):
                site = urljoin(self.url,href)
            else:
                site = href

            if "jpg" in site:
                continue

            # checking domain
            if self.check_url(site):
                if not site in self.sites:
                    self.sites.append(site)
                    print(f"\n [+] {site}",end="")
                    self.download(site,depth)        

    def start(self):
        mainpage = self.session.get(self.url)
        try:
            mainpage.html.render(timeout=20)
        except Exception as err:
            print(err)
            ms = mailscraper(self.url)
            ms.depth = self.depth
            sys.exit()
            ms.start()
            self.emails = ms.emails

        # extracting emails of mainpage
        self.extract(mainpage.html.html,self.url)
        
        threads = list()

        # extracting urls of mainpage
        soup = BeautifulSoup(mainpage.html.html,"html.parser")
        for link in soup.find_all("a"):
            try:
                href = link["href"]
            except:
                continue

            # converting urls
            if not href.startswith("http"):
                site = urljoin(self.url,href)
            else:
                site = href

            # checking domain
            if self.check_url(site):
                if not site in self.sites:
                    self.sites.append(site)
                    print(f"\n [+] {site}",end="")
                    t = Thread(target=self.download,args=[site,0])
                    t.daemon = True
                    threads.append(t)

        for thread in threads:
            thread.start()
            thread.join()    

class mailscraper:
    regex = [
        "[a-zA-Z0-9]+@[a-z0-9]{1,61}\.[a-z]{1,12}",
        "[a-zA-Z0-9]+@[a-z0-9]{1,30}.[a-z0-9]{1,31}\.[a-z]{1,10}", # point in the middle is for - in a domain like xyz-abc.de
        "[a-zA-Z0-9]+@[a-z0-9]{1,30}.[a-z0-9]{1,31}.[a-z0-9]{1,30}\.[a-z]{1,10}",
        "[a-zA-Z0-9]+@[a-z0-9]{1,30}.[a-z0-9]{1,31}.[a-z0-9]{1,30}.[a-z0-9]{1,30}\.[a-z]{1,10}"
    ]
    user_agent_rotator = UserAgent(software_names=[SoftwareName.CHROME.value], operating_systems=[OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value], limit=100)

    def __init__(self,url):
        self.url = url
        self.domain = urlsplit(url)[1]
        self.sites = list()
        self.emails = list()
        self.depth = 4

    def check_url(self,url):
        regex = [
            "https:\/\/[a-z0-9]{1,20}\.[a-z]{1,12}", # no '-' in domain without subdomain
            "https:\/\/[a-z0-9]{1,20}\.[a-z0-9]{1,20}\.[a-z]{1,12}", # no '-' in domain with subdomain
            "https:\/\/[a-z0-9]{1,20}.[a-z]{1,16}\.[a-z]{1,10}", # 1 '-' in domain and no subdomain
            "https:\/\/[a-z0-9]{1,16}\.[a-z0-9]{1,20}.[a-z0-9]{1,16}\.[a-z]{1,10}" # 1 '-' in domain and subdomain
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
        mainpage = requests.get(self.url,headers={"user-agent":mailscraper.user_agent_rotator.get_random_user_agent()}).text
        self.extract(mainpage,self.url)
        soup = BeautifulSoup(mainpage,"html.parser")

        threads = []
        for link in soup.find_all("a"):
            try:
                href = link["href"]
            except:
                continue # log

            # converting urls
            if not href.startswith("http"):
                site = urljoin(self.url,href)
            else:
                site = href
        
            # checking domain
            if self.check_url(site):
                if not site in self.sites:
                    self.sites.append(site)
                    t = Thread(target=self.download,args=[site,0])
                    t.daemon = True
                    threads.append(t)

        for thread in threads:
            thread.start()
            thread.join()                     
                    
    def download(self,url,depth):
        if depth == self.depth:
            sys.exit()
        else:
            depth+=1
        try: 
            html = requests.get(url,headers={"user-agent":mailscraper.user_agent_rotator.get_random_user_agent()}).text
        except:
            return #log

        self.extract(html,url)
        soup = BeautifulSoup(html,"html.parser")
        
        for link in soup.find_all("a"):
            try:
                href = link["href"]
            except:
                continue # log

            # converting urls
            if not href.startswith("http"):
                site = urljoin(url,href)
            else:
                site = href
            
            if ".jpg" in site.lower() or ".pdf" in site.lower() or ".png" in site.lower() or ".jpeg" in site.lower() or ".mp4" in site.lower():
                continue
        
            # checking domain
            if self.check_url(site):
                if not site in self.sites:
                    self.sites.append(site)
                    print(f"\n [+] {site}",end="")
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

    # adding argument
    argparser.add_argument("-m","--mode",default="norender",required=False)
    argparser.add_argument("-d","--depth",default=None,required=False)

    # parsing arg parser
    args = argparser.parse_args()

    # printing main screen
    print(pages.main)

    # checking mode
    if args.mode == "norender":
        url = input("\n [+] enter target url: ")
        if not url.startswith("http"):
            url = "https://" + url

        # start scraping
        ms = mailscraper(url)
        if not args.depth == None:
            ms.depth = int(args.depth)
        ms.start()
    elif args.mode == "render":
        url = input("\n [+] enter target url: ")
        if not url.startswith("http"):
            url = "https://" + url

        # start scraping
        ms = mailscraper_render(url)
        if not args.depth == None:
            ms.depth = int(args.depth)
        ms.start()
    else:
        sys.exit()

    # printing the result
    os.system("cls")
    print(pages.output)
    for mail in ms.emails:
        if validate_email(mail,check_format=True,check_blacklist=True,check_dns=False,check_smtp=False):
            print(f" [+] {mail}")
   
