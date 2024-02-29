#!/usr/bin/env python3

import json
import argparse
import shutil
from typing import Dict
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import bot

load_dotenv()

parser = argparse.ArgumentParser()
parser.add_argument('--notify', action='store_true', help='Enable notifications for new listings')
args = parser.parse_args()

def ygl_listings(url: str):
    '''Generator function for getting all paginated listings from a ygl search query'''
    page = 0

    while True:
        page += 1
        response = requests.get(f'{url}&page={page}', timeout=10)
        response.raise_for_status()
        html_content = response.text

        soup = BeautifulSoup(html_content, 'lxml')

        if soup.find('div', class_='nothing_found') is not None:
            break

        listings = soup.find_all('div', class_='property_item')
        for listing in listings:
            yield listing

def fill_properties(old_listings: Dict, new_listings: Dict, ygl_url_base: str):
    '''
    Fill a persistent props dict with listings and their data

    json format example
    {
        "100 Beefcake Rd": {
            "refs": ["ygl.is/12345/678910", "ygl.is/12/34"],
            "price": 4400,
            "beds": 4,
            "baths": 2,
            "date": "09/01/2024",
            "notes": "Evil, diabolical, lemon-scented",
            "isFavorite": True,
            "isDismissed": False,
        }
    }
    '''
    for listing in ygl_listings(f'{ygl_url_base}?beds_from=4&beds_to=5&rent_to=5200&date_from=08%2F02%2F2024'):
        listing_element = listing.find('a', class_='item_title')
        listing_addr = listing_element.get_text()
        listing_url = listing_element['href']

        if listing_addr not in new_listings:
            if listing_addr in old_listings:
                new_listings[listing_addr] = old_listings[listing_addr]
            else:
                if args.notify:
                    bot.notify(listing_url)

                # initialize a new entry for this listing
                new_listing = {
                    'refs': [],
                    'price': -1,
                }

                listing_props_elements = listing.find_all('div', class_='column')
                listing_props = list(map(lambda tag: tag.text.strip(), listing_props_elements))
                # the listing properties are well-ordered, so we parse them directly
                listing_price = int(''.join(filter(lambda char: char.isdigit(), listing_props[0])))
                listing_beds = float(listing_props[1].split(' ')[0])
                listing_baths = float(listing_props[2].split(' ')[0])
                listing_date = listing_props[3].split(' ')[1]

                new_listing['price'] = listing_price
                new_listing['beds'] = listing_beds
                new_listing['baths'] = listing_baths
                new_listing['date'] = listing_date
                new_listing['notes'] = ''
                new_listing['isFavorite'] = False
                new_listing['isDismissed'] = False

                new_listings[listing_addr] = new_listing

        # always check if this is a new copy of the listing
        if listing_url not in new_listings[listing_addr]['refs']:
            new_listings[listing_addr]['refs'].append(listing_url)


if __name__ == "__main__":
    with open('../data/sites.json', 'r', encoding='utf-8') as sites_fp:
        sites = json.load(sites_fp)

    try:
        shutil.copyfile('../data/listings.json', '../data/listings.bak.json')
    except FileNotFoundError as e:
        pass

    try:
        with open('../data/listings.json', 'r', encoding='utf-8') as listings_fp:
            old_listings = json.load(listings_fp)
    except IOError as e:
        old_listings = {}

    new_listings = {}
    for site in sites.keys():
        fill_properties(old_listings, new_listings, site)

    with open('../data/listings.json', 'w', encoding='utf-8') as listings_file:
        json.dump(new_listings, listings_file)
