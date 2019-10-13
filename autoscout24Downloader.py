import urllib.request as urllib2
from bs4 import BeautifulSoup
import math
import urllib.request
import os
import string
import fnmatch

def remove_non_ascii(text):
    return ''.join(i for i in text if ord(i)<128)

class imageDownloader():
    """docstring for imageDownloader"""
    def __init__(self):
        super(imageDownloader, self).__init__()
        self.imagesDownloaded = 0
        self.listingsDownloaded = 0
        self.pagesDownloaded = 0
        
    def getCarMakes(self):

        # url = "https://www.autoscout24.com"
        # page = urllib2.urlopen(url)
        # soup = BeautifulSoup(page, 'html.parser')

        # brandSoup = soup.find_all('script', attrs={'type': 'text/javascript'})
        # for brand in brandSoup:
        #     text = brand.text.encode('utf-8').strip()
        #     print(text)
        # print(brand for brand in brandSoup)

        # EASY WAY OUT Use brands.csv to upload brands
        # csv = pd.read_csv("brands.csv", encoding='utf-8')
        brands = ["Audi", "BMW", "Ford", "Mercedes-Benz", "Opel", "Renault", "Volkswagen", "9ff", "Abarth", "AC", "ACM", "Acura", "Aixam", "Alfa-Romeo", "Alpina", "Alpine", "Amphicar", "Ariel-Motor", "Artega", "Aspid", "Aston-Martin", "Austin", "Autobianchi", "Auverland", "Baic", "Bedford", "Bellier", "Bentley", "Bolloré", "Borgward", "Brilliance", "Bugatti", "Buick", "BYD", "Cadillac", "Caravans-Wohnm", "Casalini", "Caterham", "Changhe", "Chatenet", "Chery", "Chevrolet", "Chrysler", "Citroen", "CityEL", "CMC", "Corvette", "Courb", "Cupra", "Dacia", "Daewoo", "DAF", "Daihatsu", "Daimler", "Dangel", "De-la-Chapelle", "De-Tomaso", "Derways", "DFSK", "Dodge", "Donkervoort", "DR-Motor", "DS-Automobiles", "Dutton", "e.GO", "Estrima", "Ferrari", "Fiat", "FISKER", "Gac-Gonow", "Galloper", "GAZ", "Geely", "GEM", "GEMBALLA", "Genesis", "Gillet", "Giotti-Victoria", "GMC", "Great-Wall", "Grecav", "Haima", "Hamann", "Honda", "HUMMER", "Hurtan", "Hyundai", "Infiniti", "Innocenti", "Iso-Rivolta", "Isuzu", "Iveco", "IZH", "Jaguar", "Jeep", "Karabag", "Kia", "Koenigsegg", "KTM", "Lada", "Lamborghini", "Lancia", "Land-Rover", "LDV", "Lexus", "Lifan", "Ligier", "Lincoln", "Lotus", "Mahindra", "MAN", "Mansory", "Martin-Motors", "Maserati", "Maxus", "Maybach", "Mazda", "McLaren", "Melex", "MG", "Microcar", "Minauto", "MINI", "Mitsubishi", "Mitsuoka", "Morgan", "Moskvich", "MP-Lafer", "MPM-Motors", "Nio", "Nissan", "Oldsmobile", "Oldtimer", "Pagani", "Panther-Westwinds", "Peugeot", "PGO", "Piaggio", "Plymouth", "Pontiac", "Porsche", "Proton", "Puch", "Qoros", "Qvale", "RAM", "Reliant", "Rolls-Royce", "Rover", "Ruf", "Saab", "Santana", "Savel", "SDG", "SEAT", "Shuanghuan", "Skoda", "smart", "SpeedArt", "Spyker", "SsangYong", "StreetScooter", "Subaru", "Suzuki", "TagAZ", "Talbot", "Tasso", "Tata", "Tazzari-EV", "TECHART", "Tesla", "Town-Life", "Toyota", "Trabant", "Trailer-Anhänger", "Triumph", "Trucks-Lkw", "TVR", "UAZ", "Vanderhall", "VAZ", "VEM", "Volvo", "Vortex", "Wallys", "Wartburg", "Westfield", "Wiesmann", "Zastava", "ZAZ", "Zhidou", "Zotye"]
    
        for brand in brands:
            print(brand.encode('utf-8'))

# Called at the beginning used to iterate through the pages of listings.
    def getNumberOfPagesFor(self, brand, minPrice):
        brandUrl = 'https://www.autoscout24.com/lst/{}?sort=price&desc=0&ustate=N%2CU&size=20&page=1&pricefrom={}&atype=C&'.format(brand,minPrice)
        print(brandUrl)
        brandPage = urllib2.urlopen(brandUrl)
        numSoup = BeautifulSoup(brandPage, 'html.parser')
        number_of_cars = numSoup.find_all('span', attrs={'class': 'cl-filters-summary-counter'})[0].text
        number_of_cars = ''.join(x for x in number_of_cars if x in string.printable).split('S')[0].replace(',','')
        number_of_pages = math.ceil(float(int(number_of_cars) / 20))
        print('number of pages : ', number_of_pages)
        return number_of_pages

    def getNewMinPrice(self, brand, page, minPrice):
        brandUrl = 'https://www.autoscout24.com/lst/{}?sort=price&desc=0&ustate=N%2CU&size=20&page={}&pricefrom={}&atype=C&'.format(brand, page, minPrice)
        print(brandUrl)
        listingPage = urllib2.urlopen(brandUrl)
        listingSoup = BeautifulSoup(listingPage, 'html.parser')
        price = listingSoup.find_all('span', attrs={'class','cldt-price sc-font-xl sc-font-bold'})[-1].text
        price = ''.join(x for x in price if x.isdigit()).replace(',','')
        return price

# From a page, gets urls of all the car listings for certain brand
    def getListingUrls(self, brand, page, minPrice):
        urls = []

        brandUrl = 'https://www.autoscout24.com/lst/{}?sort=price&desc=0&ustate=N%2CU&size=20&page={}&pricefrom={}&atype=C&'.format(brand, page, minPrice)
        brandPage = urllib2.urlopen(brandUrl)
        numSoup = BeautifulSoup(brandPage, 'html.parser')

        # Getting Listing : 
        listingUrls = numSoup.find_all('a', attrs={"data-item-name":"detail-page-link"})

        for listing in listingUrls:
            text = listing.get('href').strip()
            urls.append(text)
            print(text)
        print('PAGE :', page)
        return urls

# From a given url, function scrapes all images of the car.
    def getPhotoUrls(self, url, brand):
        print(url)
        print(url[-36:])
        urls = []
        listingPage = urllib2.urlopen('https://www.autoscout24.com' + url)
        listingSoup = BeautifulSoup(listingPage, 'html.parser')
        model = listingSoup.find_all('span', attrs={'class','cldt-detail-makemodel sc-ellipsis'})[0].text.replace(' ', '_')
        print('images/' + brand.upper() + '/' + model.upper() + '/' + url[-36:])
        try:
            if self.listingExists('images/' + brand.upper() + '/' + model.upper() + '/', url[-36:]):
                print('Listing already downloaded')
                return []
        except:
            pass
        urls.append(model)
        self.listingsDownloaded += 1
        photos = listingSoup.find_all('img', attrs={'class':'gallery-picture__image'})
        for photo in photos:
            try:
                text = photo.get('data-fullscreen-src').strip()
                urls.append(text)
            except:
                print('No photo download Source')
        return urls

# Downloads photos from given url. Saves image in Brand folder and in model folder with name of car
    def downloadPhotos(self, url, brand, model):
        if not os.path.exists('images/' + brand.upper()):
            os.mkdir('images/' + brand.upper())
        print('images/' + brand.upper() + '/' + model.upper())
        if not os.path.exists('images/' + brand.upper() + '/' + model.upper()):
            os.mkdir('images/' + brand.upper() + '/' + model.upper())

        file_name = 'images/' + brand.upper() + '/' + model.upper()+ '/' + url[53:-17]
        full_file_name = str(file_name) + '.jpg'
        print('Downloading File :' + str(brand) + ' ' + str(model) + ' ' + str(self.imagesDownloaded))
        try:
            urllib.request.urlretrieve(url,full_file_name)
            self.imagesDownloaded += 1
        except:
            print('There was a problem downloading File')

# Main function that downloads images of a certain make. Takes car make and an optional minimum price
    def downloadImagesFrom(self, brand, minPrice=0):
        while self.getNumberOfPagesFor(brand, minPrice) > 20:
            for page in range(1,self.getNumberOfPagesFor(brand, minPrice)):
                listings = self.getListingUrls(brand, page, minPrice)
                print("PAGE NUMBER : ", page)
                if page == 20:
                    minPrice = self.getNewMinPrice(brand, page, minPrice)
                    break
                for listing in listings:
                    photoUrls = self.getPhotoUrls(url=listing,brand=brand)
                    print("Listings Downloaded : ", self.listingsDownloaded)
                    for i in range(1,len(photoUrls)):
                        self.downloadPhotos(photoUrls[i], brand=brand, model=photoUrls[0])

        for page in range(1,self.getNumberOfPagesFor(brand, minPrice)):
            listings = self.getListingUrls(brand, page, minPrice)
            print("PAGE NUMBER : ", page)
            for listing in listings:
                photoUrls = self.getPhotoUrls(url=listing,brand=brand)
                print("Listings Downloaded : ", self.listingsDownloaded)
                for i in range(1,len(photoUrls)):
                    self.downloadPhotos(photoUrls[i], brand=brand, model=photoUrls[0])

# Local check if image is already downloaded
    def listingExists(self,path, pattern):
        for file in os.listdir(path):
            if fnmatch.fnmatch(file, '*' + pattern + '*'):
                return True
        return False

imgdldr = imageDownloader()
imgdldr.downloadImagesFrom('mercedes-benz', minPrice=0)



