#!/usr/bin/env python3
"""
Simple News Scraper Runner Script

This script runs all available news scrapers in the news_scraper project.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from news_scraper.spiders import (
    BusinessStandardSpider,
    BusinessTodaySpider,
    CnbcTv18Spider,
    EconomicTimesSpider,
    FinancialExpressSpider,
    FirstPostSpider,
    FreePressJournalSpider,
    IndianExpressSpider,
    MoneyControlSpider,
    NDTVProfitSpider,
    News18Spider,
    OutlookIndiaSpider,
    TheHinduBusinessLineSpider,
    TheHinduSpider,
    ZeeNewsSpider,
)

# Dictionary of all available spiders
AVAILABLE_SPIDERS = {
    "businessstandard": BusinessStandardSpider,
    "businesstoday": BusinessTodaySpider,
    "cnbctv18": CnbcTv18Spider,
    "economictimes": EconomicTimesSpider,
    "financialexpress": FinancialExpressSpider,
    "firstpost": FirstPostSpider,
    "freepressjournal": FreePressJournalSpider,
    "indianexpress": IndianExpressSpider,
    "moneycontrol": MoneyControlSpider,
    "ndtvprofit": NDTVProfitSpider,
    "news18": News18Spider,
    "outlookindia": OutlookIndiaSpider,
    "thehindu": TheHinduSpider,
    "thehindubusinessline": TheHinduBusinessLineSpider,
    "zeenews": ZeeNewsSpider,
}

# Default spiders to run (excluding potentially problematic ones)
DEFAULT_SPIDERS = [
    "businessstandard",
    "businesstoday",
    "cnbctv18",
    "economictimes",
    "financialexpress",
    "firstpost",
    "freepressjournal",
    "ndtvprofit",
    "news18",
    "outlookindia",
    "thehindu",
    "thehindubusinessline",
    "zeenews",
]


def setup_logging():
    """Set up logging configuration."""
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Create log file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"scraping_{timestamp}.log"
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    print(f"Logging to: {log_file}")


def main():
    """Main function to run the scrapers."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Get Scrapy settings
    settings = get_project_settings()
    
    # Update settings for better performance
    settings.update({
        "LOG_LEVEL": "INFO",
        "LOG_FILE": None,  # We handle logging ourselves
        "ROBOTSTXT_OBEY": True,
        "CONCURRENT_REQUESTS": 16,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 8,
        "DOWNLOAD_DELAY": 1,
        "RANDOMIZE_DOWNLOAD_DELAY": 0.5,
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": 1,
        "AUTOTHROTTLE_MAX_DELAY": 10,
        "AUTOTHROTTLE_TARGET_CONCURRENCY": 2.0,
    })
    
    # Create crawler process
    process = CrawlerProcess(settings)
    
    logger.info("Available spiders:")
    for name in sorted(AVAILABLE_SPIDERS.keys()):
        logger.info(f"  - {name}")
    
    logger.info(f"Running {len(DEFAULT_SPIDERS)} spiders: {', '.join(DEFAULT_SPIDERS)}")
    
    # Add all default spiders to the process
    for spider_name in DEFAULT_SPIDERS:
        if spider_name in AVAILABLE_SPIDERS:
            logger.info(f"Adding spider: {spider_name}")
            process.crawl(AVAILABLE_SPIDERS[spider_name])
        else:
            logger.warning(f"Spider '{spider_name}' not found")
    
    try:
        logger.info("Starting scraping process...")
        process.start()  # This will block until all spiders finish
        logger.info("Scraping completed successfully!")
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error during scraping: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
