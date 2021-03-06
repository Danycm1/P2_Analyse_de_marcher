import requests, csv, os, urllib.request, re
from bs4 import BeautifulSoup

folder_csv =  'csv'
if not os.path.exists(folder_csv):
    os.makedirs(folder_csv)


def saveBook(url_book, category_name):

    ''' Save book information(url of the book, name of the book category)
        get information for a book and download it into a csv folder

        input url_book(str), category_name(str)
        output url of the book, name of the category
    '''
    response = requests.get(url_book)

    if response.ok:
        soup = BeautifulSoup(response.content, 'lxml')

        # extract all informations and remove html tags with .text
        product_page_url = url_book
        information = soup.find('table', attrs={'class': 'table-striped'})
        universal_product_code = information.find_all('td')[0].text
        title = soup.find('h1').text
        price_including_tax = information.find_all('td')[3].text[1:]
        price_excluding_tax = information.find_all('td')[2].text[1:]
        number_available = information.find_all('td')[5].text
        product_description = soup.find_all('p')[3].text
        category = soup.find_all('li')[2].text[1:]
        review_rating = soup.find('p', class_='star-rating').get('class')[1]
        image_src = soup.find('div', {'class': 'item active'}).find('img')
        image_url = image_src['src'].replace('../../', 'https://books.toscrape.com/')

        # create images folder if it doesn't exist
        if not os.path.exists('images'):
                os.makedirs('images')

        # use regex to clean a bit
        title = re.sub('[^a-zA-Z0-9 \n]', '', title)

        # download all images
        images = 'images/' + title + '.jpg'
        with open(f'{images}', 'wb') as outi:
            outi.write(urllib.request.urlopen(image_url).read())

    # save info in a csv file
    dossier_csv = folder_csv + '/' + category_name + '.csv'
    with open(f'{dossier_csv}', 'a', encoding='utf8', newline='') as outf:
        write = csv.writer(outf)
        info = [product_page_url, universal_product_code, title, price_including_tax, price_excluding_tax,
                number_available, product_description, category, review_rating, image_url]

        # write info into our file
        write.writerow(info)


def get_all_book_from_cat(url_cat, category_name):

    ''' Get all book from category(url of the category, name of the category)
        save headers in a csv folder and get all books from the category
        if a category has more than one page, visit them and retrieve books

        input url_cat(str), category_name(str)
        output url of the category, name of the category
    '''

    # save info in a csv file
    dossier_csv = folder_csv + '/' + category_name + '.csv'
    with open(f'{dossier_csv}', "w", encoding="utf8", newline='') as outf:
        write = csv.writer(outf)
        header = ['product_page_url', 'universal_product_code', 'title', 'price_including_tax', 'price_excluding_tax',
                'number_available', 'product_description', 'category', 'review_rating', 'image_url\n']
        # write header
        write.writerow(header)

    print('Retrieving all books from category ' + url_cat)

    # loop in all page
    url_page = "index.html"
    while True:
        response = requests.get(url_cat + url_page)
        soup = BeautifulSoup(response.text, 'lxml')

        # loop to get all the book url in the category
        for books in soup.find_all('div', {'class': 'image_container'}):
            url_book = books.find('a', href= True)
            url_book = url_book['href'].split('..')[3]
            url_book = 'https://books.toscrape.com/catalogue' + url_book
            saveBook(url_book, category_name)

        # retrieve next page url
        next_page = soup.find_all('li', {'class': 'next'})
        if len(next_page) != 0:
            url_page = next_page[0].find('a', href= True)
            url_page = url_page['href']
        else:
            break

def get_all_category(url):

    
    '''get all category(url)
       get all the category url and name

       input get_all_category(str)
       output all category from the website
    '''

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')

    # loop to get all category name
    categories = soup.find('ul', class_='nav nav-list').li.ul.find_all('li')
    for category in categories:
        link = category.find('a')['href'].replace('index.html', '')
        category_name = category.find('a').text.strip()
        get_all_book_from_cat(url + link, category_name)
    print('Extraction fini')