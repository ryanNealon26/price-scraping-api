import requests 
import json
from bs4 import BeautifulSoup 
from fakeUserAgent import generate_agent

class TruliaBot:
    def __init__(self):
        self.base_url = "https://www.trulia.com"
    def make_request(self, searchQuery):
        link =f"{self.base_url}{searchQuery}"
        Headers = ({'User-Agent':"Mozilla/5.0 (Linux; Android 13; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36"})
        proxies ={
            'http': "http://72.10.160.91",
            'http': "http://117.74.65.207",
        }
        response = requests.get(link, headers=Headers, proxies=proxies)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html5lib')
            return soup
        else:
            json = {
                "Error Message": f"Failed to Pull Data From {link}, return responce code of {response.status_code}"
            }
            return json
    def pull_house_data(self, state, city, page):
        scraper = self.make_request(f"/{state}/{city}/{page}_p/")
        prices =scraper.findAll('div', attrs = {"data-testid":'property-price'})
        addresses=scraper.findAll('div', attrs = {"data-testid":'property-address'})
        beds = scraper.findAll('div', attrs = {"data-testid":'property-beds'})
        baths = scraper.findAll('div', attrs = {"data-testid":'property-baths'})
        sqrft = scraper.findAll('div', attrs = {"data-testid":'property-floorSpace'})
        links = scraper.findAll('a', attrs = {"class":'Anchor__StyledAnchor-sc-3c3ff02e-1 doURDx'})
        json = {
            f"Page {page}": []
        }
        list_link = []
        for link in links:
            if link['href'].find("/home") != -1:
                list_link.append(f"{self.base_url}{link['href']}")
        for address, price, bed, bath, sq, link in zip(addresses, prices, beds, baths, sqrft, list_link):
            data = {
                "Address": address.text,
                "Property Price": price.text,
                "Property Beds": bed.text,
                "Property Baths": bath.text,
                "Property Sqrft": sq.text,
                "Property Link": link
            }
            json[f"Page {page}"].append(data)
        return json    
    def scrape_images(self, state, city):
        scraper = self.make_request(f"/{state}/{city}/")
        addresses=scraper.findAll('div', attrs = {"data-testid":'property-address'})
        json = {
            "Images": []
        }
        for address in addresses:
            images =scraper.findAll('img', attrs = {"alt":f'{address.text}'})
            for image in images:
                data = {
                    "Address": address.text,
                    "Image Source": image['src']
                }
                json["Images"].append(data)
        return json
    def scrape_pages(self, state, city, pageNumber):
        scraper = self.make_request(f"/{state}/{city}/")
        totalHouses = scraper.findAll('h2', attrs = {"class":'sc-259f2640-0 bcPATd'})
        total = ""
        for house in totalHouses:
            total = int(house.text.replace(" homes ", ""))
        if total<40:
            pageNumber = 1
        if pageNumber > round(total/40):
            pageNumber = round(total/40) + 1
        page = 1
        json = {
            "Items": []
        }
        while page <=pageNumber:
            data = self.pull_house_data(state, city, page)
            while data[f"Page {page}"] == []:
                data = self.pull_house_data(state, city, page)
            json["Items"].append(data)
            page +=1
        return json
        