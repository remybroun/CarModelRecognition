import urllib.request as urllib2
from bs4 import BeautifulSoup
import pandas as pd
import re
import math
import urllib.request
import os
import boto3

s3 = boto3.resource('s3')

if os.path.exists('listing.csv'):
    listingsDf = pd.read_csv('listings.csv')
else:
    listingsDf = pd.DataFrame(columns= ['Listing'])


# filename = 'marques.csv'
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
            # brandUrl = 'https://www.lacentrale.fr/listing?makesModelsCommercialNames={}&options=&page={}'.format(brand,page)
            brandUrl = 'https://www.lacentrale.fr/listing?makesModelsCommercialNames={}&options=&page={}'.format(brand, page)
            print(brandUrl)
            brand = brand.replace('%20', '_')
            try:
                brandPage = urllib2.urlopen(brandUrl)
            except urllib2.URLError as e:
                print ("An error has occured")
                listingsDf.to_csv('downloadedListings.csv')
                continue
            brandSoup = BeautifulSoup(brandPage, 'html.parser')

            listings = brandSoup.find_all('a', attrs={'class': 'linkAd ann'})

            for listing in listings:
                print("Getting listing")
                text = listing.get('href').strip()
                if text in listingsDf:
                    print("Already Downloaded")
                    break
                else:
                    listingsDf = listingsDf.append({'Listing':text[23:-5]}, ignore_index=True)

                listing_link = "https://www.lacentrale.fr" + text
                print(listing_link)
                try:
                    listingPage = urllib2.urlopen(listing_link)
                except urllib2.URLError as e:
                    print ("An error has occured")
                    listingsDf.to_csv('downloadedListings.csv')
                    continue
                listingSoup = BeautifulSoup(listingPage, 'html.parser')

                carModel = listingSoup.h1.text.replace('\n', '').replace(' ', '_')
                # Check if dir exists for model
                modelDir = "./images/{}/{}".format(brand, carModel)

                if not os.path.isdir(modelDir.replace('%20', '_')):
                    print("Creating Directory for : {}, {}".format(brand, carModel))
                    os.mkdir(modelDir.replace('%20', '_'))

                listingImageUrls = set(re.findall(r"src\"\:\"https\:\/\/photo2\.lacentrale\.fr\/photo\/(.*?jpg|jpeg|png|null)", str(listingSoup.encode('ascii'))))

                for imageUrl in listingImageUrls:
                    filename = imageUrl[3:].replace('/', '_')
                    imageUrl = "https://photo2.lacentrale.fr/photo/" + imageUrl
                    if ("jpg" in imageUrl) | ("png" in imageUrl) | ("jpeg" in imageUrl) and len(listingImageUrls) < 200:
                        full_file_name = modelDir + "/" + filename
                        print("Downloading : {}, {} from URL : {}".format(brand, carModel, imageUrl))

                        # Download The file locally
                        try:
                            urllib.request.urlretrieve(imageUrl, full_file_name)
                        except urllib2.URLError as e:
                            print ("An error has occured")
                            listingsDf.to_csv('downloadedListings.csv')
                            continue
                        # Open the file in our session
                        data = open(full_file_name, 'rb')

                        # Upload our file to s3 Bucket
                        s3.Bucket('carsformodelrecognition').put_object(Key=full_file_name[2:], Body=data)

                        # Remove file from our directory
                        os.remove(full_file_name)

                        photos_downloaded += 1
                car_listings_downloaded += 1
                print("TOTAL IMAGES DOWNLOADED : " + str(photos_downloaded))
                print("TOTAL LISTINGS DOWNLOADED : " + str(car_listings_downloaded))
            brands_downloaded += 1
            print("TOTAL BRANDS DOWNLOADED : " + str(brands_downloaded))
except e:
    listingsDf.to_csv('downloadedListings.csv')
    raise e
    # for brand in brands:
    #     brand.replace(' ', '%20')
    #     for page in range(number_of_pages):
    #         brandUrl = 'https://www.lacentrale.fr/listing?makesModelsCommercialNames={}&options=&page={}'.format(brand,page)
    #         brandPage = urllib2.urlopen(brandUrl)
    #         for car in range(16):
    #             pass
