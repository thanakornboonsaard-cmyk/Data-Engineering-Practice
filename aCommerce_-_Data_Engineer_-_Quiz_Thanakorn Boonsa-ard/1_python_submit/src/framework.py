"""
This file contains the framework that defines how the different classes will 
work together.
"""

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def flow() -> None:
    """
        This framework will run the Scraper's job before calling the Transformer
        to transformed the scraped data.
    """
    from src.scraper import BookScraper
    from src.transformer import BookTransformer

    base_url = 'http://books.toscrape.com/'
    
    try:
        scraper = BookScraper(base_url)
        logger.info('Starting scraper sequence...')
        scraped = scraper.scrape()
        scraper.save(scraped)
        logger.info(f'Scraper finished. Total books collected: {len(scraped)}')

        logger.info('Starting transformer sequence...')
        transformer = BookTransformer()
        transformer.run()
        logger.info('Transformation sequence complete. Results stored in transformed directory.')
        
    except Exception as e:
        logger.error(f'Pipeline failed: {str(e)}', exc_info=True)
        raise
