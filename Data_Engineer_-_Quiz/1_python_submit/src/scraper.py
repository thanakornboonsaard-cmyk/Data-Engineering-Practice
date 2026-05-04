"""
This file contains the definitions for the Scraper class as well as its child
classes. 
"""


import logging
from abc import abstractmethod
import json
import os
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from src.config import config

logger = logging.getLogger(__name__)

class Scraper:
    """
        A Scraper scrapes through a website and saves the required data as JSON
        files.

        Attributes
        ----------
        base_url : str
            The base URL to be scraped without additional endpoints.

        Methods
        ----------
        run()
            Scrapes through a website and saves the required data as a single 
            JSON file under the data/raw/ directory.
        scrape()
            Scrapes through various pages of a website and generates the result
            as a list of dicts.
        save()
            Saves the scraped data as a JSON file under the data/raw/
            directory.
    """
    
    def __init__(self, base_url: str) -> None:
        """
            Instantiates a Scraper object.
        """
        self.base_url = base_url

    def run(self) -> None:
        """
            Scrapes through a website and saves the required data as a JSON
            file under the data/raw/ directory.
        """
        scraped_data = self.scrape()
        self.save(scraped_data)

    @abstractmethod
    def scrape(self) -> list[dict]:
        """
            Scrapes through various pages of a website and generates the result
            as a list of dicts.
        """

    def save(self, data: list[dict]) -> None:
        """
            Saves the scraped data as a JSON file under the data/raw/
            directory.
        """
        os.makedirs(config['RAW_DIRECTORY'], exist_ok=True)
        with open('{}/data.json'.format(config['RAW_DIRECTORY']), 'w', encoding='utf-8') as fp:
            json.dump(data, fp, ensure_ascii=False, indent=2)


class BookScraper(Scraper):
    """
        A BookScraper is a child of Scraper that scrapes data of all the books
        listed on http://books.toscrape.com.
    """

    def scrape(self) -> list[dict]:
        """
        Scrape all books from the base site and return a list of dicts.
        Uses pagination by following the "next" link on listing pages.
        """
        results = []
        next_url = self.base_url
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'book-scraper/1.0 (+https://example.com)'
        })

        page_count = 0
        while next_url:
            page_count += 1
            logger.info(f'Scraping page {page_count}: {next_url}')
            try:
                resp = session.get(next_url, timeout=15)
                resp.raise_for_status()
            except Exception as e:
                logger.error(f'Failed to fetch page {next_url}: {str(e)}')
                break

            soup = BeautifulSoup(resp.text, 'lxml')

            # find all product links on the page
            page_results = 0
            for article in soup.select('article.product_pod'):
                a = article.select_one('h3 a')
                href = a.get('href')
                book_url = urljoin(next_url, href)
                
                book = self._scrape_book_detail(session, book_url)
                if book:
                    results.append(book)
                    page_results += 1
            
            logger.debug(f'Collected {page_results} books from page {page_count}')

            # find next page
            next_link = soup.select_one('li.next a')
            if next_link and next_link.get('href'):
                next_url = urljoin(next_url, next_link.get('href'))
            else:
                next_url = None

        return results

    def _scrape_book_detail(self, session: requests.Session, url: str) -> dict | None:
        try:
            resp = session.get(url, timeout=10)
            resp.raise_for_status()
        except Exception:
            return None

        soup = BeautifulSoup(resp.text, 'lxml')
        product_main = soup.select_one('.product_main')
        title = product_main.select_one('h1').get_text(strip=True) if product_main else ''

        # product information table
        info = {}
        for tr in soup.select('table.table.table-striped tr'):
            th = tr.select_one('th')
            td = tr.select_one('td')
            if th and td:
                info[th.get_text(strip=True)] = td.get_text(strip=True)

        # description
        desc = ''
        desc_header = soup.select_one('#product_description')
        if desc_header:
            p = desc_header.find_next_sibling('p')
            if p:
                desc = p.get_text(strip=True)

        # rating
        rating = ''
        star = soup.select_one('p.star-rating')
        if star:
            classes = star.get('class', [])
            # class example: ['star-rating', 'Three']
            for c in classes:
                if c.lower() in ('one', 'two', 'three', 'four', 'five'):
                    rating = c.capitalize()
                    break

        book = {
            'UPC': info.get('UPC', ''),
            'Product Type': info.get('Product Type', ''),
            'Price (excl. tax)': info.get('Price (excl. tax)', ''),
            'Price (incl. tax)': info.get('Price (incl. tax)', ''),
            'Tax': info.get('Tax', ''),
            'Availability': info.get('Availability', ''),
            'Number of reviews': info.get('Number of reviews', ''),
            'Description': desc,
            'Rating': rating,
            'Title': title,
        }

        return book
