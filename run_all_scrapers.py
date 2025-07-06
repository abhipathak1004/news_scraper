#!/usr/bin/env python3
"""
News Scraper Runner Script

This script runs all available news scrapers in the news_scraper project.
It provides options for running specific scrapers and detailed logging.
"""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Any

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

# Default spiders to run (excluding problematic ones)
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


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> None:
    """Set up logging configuration."""
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Set default log file if not provided
    if log_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = str(log_dir / f"scraping_{timestamp}.log")
    
    # Configure logging
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    print(f"Logging to: {log_file}")


def get_scrapy_settings(log_level: str = "INFO") -> Any:
    """Get Scrapy settings with custom configurations."""
    settings = get_project_settings()
    
    # Update settings for better logging and performance
    settings.update({
        "LOG_LEVEL": log_level.upper(),
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
        "AUTOTHROTTLE_DEBUG": False,
    })
    
    return settings


def run_spiders(spider_names: List[str], settings: Any) -> None:
    """Run spiders sequentially using CrawlerProcess."""
    process = CrawlerProcess(settings)
    
    logger = logging.getLogger(__name__)
    
    for spider_name in spider_names:
        if spider_name in AVAILABLE_SPIDERS:
            logger.info(f"Adding spider to process: {spider_name}")
            process.crawl(AVAILABLE_SPIDERS[spider_name])
        else:
            logger.warning(f"Spider '{spider_name}' not found. Available spiders: {list(AVAILABLE_SPIDERS.keys())}")
    
    if process.crawlers:
        logger.info(f"Starting {len(process.crawlers)} spiders...")
        process.start()  # This will block until all spiders finish
    else:
        logger.warning("No valid spiders to run")


def main():
    """Main function to run the scrapers."""
    parser = argparse.ArgumentParser(description="Run news scrapers")
    parser.add_argument(
        "--spiders", 
        nargs="+", 
        default=DEFAULT_SPIDERS,
        help="List of spider names to run (default: run all default spiders)"
    )
    parser.add_argument(
        "--list-spiders", 
        action="store_true",
        help="List all available spiders and exit"
    )
    parser.add_argument(
        "--log-level", 
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level"
    )
    parser.add_argument(
        "--log-file",
        help="Custom log file path"
    )
    parser.add_argument(
        "--all-spiders",
        action="store_true",
        help="Run all available spiders (including potentially problematic ones)"
    )
    
    args = parser.parse_args()
    
    # List spiders and exit
    if args.list_spiders:
        print("Available spiders:")
        for name in sorted(AVAILABLE_SPIDERS.keys()):
            print(f"  - {name}")
        print(f"\nDefault spiders: {', '.join(DEFAULT_SPIDERS)}")
        return
    
    # Set up logging
    setup_logging(args.log_level, args.log_file)
    logger = logging.getLogger(__name__)
    
    # Determine which spiders to run
    if args.all_spiders:
        spider_names = list(AVAILABLE_SPIDERS.keys())
    else:
        spider_names = args.spiders
    
    logger.info(f"Running spiders: {', '.join(spider_names)}")
    
    # Get Scrapy settings
    settings = get_scrapy_settings(args.log_level)
    
    try:
        logger.info("Starting scraping process...")
        run_spiders(spider_names, settings)
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error during scraping: {e}")
        sys.exit(1)
    
    logger.info("Scraping completed successfully!")


if __name__ == "__main__":
    main()
