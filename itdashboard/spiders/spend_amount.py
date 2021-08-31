import scrapy
import json


class AgencySpendAmountSpider(scrapy.Spider):
    name = 'agency-spend-amount-spider'
    custom_settings = {
        'FEEDS': {
            f'csv/agencies-spend-amount.csv': {
                'format': 'csv',
                'overwrite': True
            }
        }
    }

    start_urls = ['https://itdashboard.gov/']

    def parse(self, response):
        div_in_sub_url: str = response.css(
            'a.btn.btn-default.btn-lg-2x.trend_sans_oneregular::attr(href)'
        ).get()

        main_url: str = response.request.url + div_in_sub_url
        yield scrapy.Request(
            main_url,
            callback=self.scrape_agencies,
            cb_kwargs = {'base_url': response.request.url}
        )

    def scrape_agencies(self, response, base_url):
        main_div = response.css('#agency-tiles-widget').extract()
        # Get the agnecies data from a javascript variable
        data = response.xpath(
            '//script[contains(., "$ITDB2")]/text()').get().replace('//--><!]]>', '').replace(';', '')
        final_dict = json.loads(data.split('=', 2)[2])
        agency_codes = list(map(lambda dict_: dict_.get('agencyCode', None), final_dict['agencies']))
        for code in agency_codes:
            agency_url: str = f'{base_url}drupal/summary/{code}'
            yield scrapy.Request(
                    agency_url,
                    callback=self.scrape_agencies_data
                )
    
    def scrape_agencies_data(self, response):
        raise NotImplementedError