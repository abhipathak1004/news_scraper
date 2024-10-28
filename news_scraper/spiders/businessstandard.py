from ..items import NewsArticleItem, NewsArticleItemLoader
from ..utils import ua
from .base import SitemapIndexSpider


class BusinessStandardSpider(SitemapIndexSpider):
    name = "businessstandard"

    sitemap_type = "monthly"
    allowed_domains = ["business-standard.com"]
    sitemap_patterns = [
        "https://www.business-standard.com/sitemap/{year}-{month}-1.xml",
    ]
    sitemap_date_formatter = {
        "year": lambda d: d.strftime("%Y"),
        "month": lambda d: d.strftime("%B").lower(),
    }

    sitemap_rules = [(r"/markets/", "parse"),(r"/companies/", "parse"),(r"/economy-policy/", "parse")]

    custom_settings = {"USER_AGENT": ua.random}

    def parse(self, response):
        """
        sample article: https://www.business-standard.com/markets/news/railtel-stock-soars-18-on-heavy-volumes-up-331-in-1-year-124071200447_1.html
        """

        article = NewsArticleItemLoader(item=NewsArticleItem(), response=response)

        # content
        article.add_css("title", "h1.stryhdtp::text")
        article.add_css("description", "h2.strydsc::text")
        article.add_css("author", "span.MainStory_dtlauthinfo__u_CUx span::text")
        '''
        Handling different URL structures for scraping based on region-specific variations.

        - For URLs containing "/markets/", we use a specific parent div (parent_top_div) to ensure accurate scraping.
        - When accessed via an EU proxy, the HTML structure differs, so we handle this by targeting paragraph tags using the XPath `/p/text()`.
        - For the Indian version of the site, we scrape content from `div` elements to capture the article text.
        '''

        article.add_xpath(
            "article_text",
            '''
            //div[@id="parent_top_div"]/div/text() |
            //div[contains(@class, "MainStory_storycontent__Pe3ys") and contains(@class, "storycontent")]
            //p[not(contains(@class, "whtsclick") or @id="auto_disclaimer")]/text() |
            //div[contains(@class, "MainStory_storycontent__Pe3ys") and contains(@class, "storycontent")]//div/text()
            '''
        )

        #paywall
        paywall_element = response.xpath('//small[contains(text(), "Premium")]').get()
        if paywall_element:
            paywall = "True"
        else:
            paywall = "False"
        article.add_value("paywall", paywall)

        # dates
        article.add_css(
            "date_published",
            'meta[property="article:published_time"]::attr(content)',
        )
        article.add_css(
            "date_modified",
            'meta[http-equiv="Last-Modified"]::attr(content)',
        )

        yield article.load_item()
