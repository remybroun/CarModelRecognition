import urllib.request as urllib2
from bs4 import BeautifulSoup
import pandas as pd
import re
import math
import urllib.request
import os
import boto3
import signal
import sys


def sigterm_handler(signal, frame):
    # save the state here or do whatever you want
    print('booyah! bye bye')
    sys.exit(0)

signal.signal(signal.SIGTERM, sigterm_handler)


s3 = boto3.resource('s3')

if os.path.exists('listing.csv'):
    listingsDf = pd.read_csv('listings.csv')
else:
    listingsDf = pd.DataFrame(columns= ['Listing'])



quote_page = 'https://www.lacentrale.fr/occasion-voiture.html'

page = urllib2.urlopen(quote_page)
soup = BeautifulSoup(page, 'html.parser')
brandSoup = soup.find_all('a', attrs={'class': 'url marqueMobLinkText'})

# Getting Brands
brands = []
for brand in brandSoup:
    text = brand.text.strip()
    brands.append(text.replace(' ', '%20'))


# brandsCSVDict = {
#     'brands': brands
# }

# print(brandsCSVDict)

# df = pd.DataFrame(brandsCSVDict)
# df.to_csv(filename)

photos_downloaded = 0
car_listings_downloaded = 0
brands_downloaded = 0
try:
    for brand in brands:
        print("BRAND : ", brand.replace('%20', ' '))
        if brand in ['ABARTH', 'AIXAM', 'AC']:
            continue
        brandUrl = 'https://www.lacentrale.fr/listing?makesModelsCommercialNames={}&options=&page=1'.format(brand)
        try:
            brandPage = urllib2.urlopen(brandUrl)
        except urllib2.URLError as e:
            print ("An error has occured")
            listingsDf.to_csv('downloadedListings.csv')
            continue

        # # Getting Number of cars and pages of cars
        numSoup = BeautifulSoup(brandPage, 'html.parser')
        number_of_cars = numSoup.find_all('span', attrs={'class': 'numAnn'})
        number_of_pages = math.ceil(float(int(number_of_cars[0].text.strip().replace('\xc2\xa0', '')) / 16))


        for page in range(1, number_of_pages + 1):
            print("Getting page : " + str(page))

            brandUrl = 'https://www.lacentrale.fr/listing?makesModelsCommercialNames={}&options=&page={}'.format(brand, page)
            print(brandUrl)
            # brand = brand.replace('%20', '_')
            try:
                brandPage = urllib2.urlopen(brandUrl)
            except urllib2.URLError as e:
                print ("An error has occured")
                listingsDf.to_csv('downloadedListings.csv')
                continue
            brandSoup = BeautifulSoup(brandPage, 'html.parser')

            listings = brandSoup.find_all('a', attrs={'class': 'linkAd ann'})
            print("got here")
            print(len(listings))
            for listing in listings:
                print("Getting listing")
                text = listing.get('href').strip()


                if text in listingsDf:
                    print("Already Downloaded")
                    break
                else:
                    print("appending : ", text[23:-5])
                    listingsDf = listingsDf.append({'Listing':text[23:-5]}, ignore_index=True)
                # print(listingsDf)
                print("saved")
                listingsDf.to_csv('downloadedListings.csv')

                car_listings_downloaded += 1
                print("TOTAL LISTINGS DOWNLOADED : " + str(car_listings_downloaded))
except:
    print("ERROR")
    listingsDf.to_csv('downloadedListings.csv')
    raise

