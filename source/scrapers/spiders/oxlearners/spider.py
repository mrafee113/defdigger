import re
import scrapy

from utils import logging
from scrapy.http.request import Request
from utils.web.scrapy_handler import ScrapyHandler as H


words = ['glamour']

class OxLearnersSpider(scrapy.Spider):
    name = "oxlearners"
    allowed_domains = ('oxfordlearnersdictionaries.com',)
    custom_settings = {'ITEM_PIPELINES': {
            'scrapers.spiders.oxlearners.pipeline.Pipeline': 300
    }}
    URL = "https://oxfordlearnersdictionaries.com/definition/english/{word}"

    @classmethod
    def format_url(cls, word: str) -> str:
        return cls.URL.format(word=word)

    def start_requests(self):
        # words = []  # fetch words
        pairs = [(word, self.format_url(word)) for word in words]
        for word, url in pairs:
            yield Request(url=url, dont_filter=True, callback=self.parse,
                          cb_kwargs={'word': word})

    def parse(self, response, **_):
        word = response.cb_kwargs['word']

        if not H.validate(response.status, validation=lambda x: x == 200):
            logging.err('request failed', f'{response.status=}', f'{response.reason=}')
            return

        element = response.xpath('//div[@class="responsive_entry_center_wrap"]')
        left_el = element.xpath('./div[@id="ox-wrapper"]//div[@id="entryContent"]/div')
        right_el = element.xpath('./div[@id="rightcolumn"]')

        top_el = left_el.xpath('./div[@class="top-container"]/div[@class="top-g"]/div[@class="webtop"]')
        word_type = H.get_attr(top_el.xpath('./span[@class="pos"]/text()'),
                               attr='text')
        # ---
        phonetics_el = top_el.xpath('./span[@class="phonetics"]')[0]
        uk_el = phonetics_el.xpath('./div[@class="phons_br"]')[0]
        uk_pron = uk_el.xpath('./div')[0].attrib['data-src-mp3']
        uk_phon = uk_el.xpath('./span[@class="phon"]/text()')[0]
        us_el = phonetics_el.xpath('./div[@class="phons_n_am"]')[0]
        us_pron = us_el.xpath('./div')[0].attrib['data-src-mp3']
        us_phon = us_el.xpath('./span[@class="phon"]/text()')[0]
        # data-src-ogg handle...
        # handle existence and validation all the way
        # ---
        # handle existence
        american_variant = top_el.xpath('./div[@class="variants"]/span[@class="v-g"]/span[@class="v"]/text()')[0]
        grammar_traits = top_el.xpath('./span[@class="grammar"]/text()')[0]
        # don't forget to parse the list to a list of strings...

        defs_el = left_el.xpath('./ol[@class="senses_multipl"]')[0]
        defs_els = defs_el.xpath('./li[@class="sense"]')
        for def_el in defs_els:
            index = def_el.attrib['sensenum']
            definition = def_el.xpath('./span[@class="sensetop"]/span[@class="def"]/text()')[0]
            
            examples = def_el.xpath('./ul[@class="examples"]/li[@class=""]/span[@class="x"]/text()')
            extra_examples = [
                el.text_content() for el in
                def_el.xpath('./div[@class="collapse"]/span[@unbox="extra_examples"]/ul[@class="examples"]/li[@class=""]')
            ]
            
            # TODO this should be topic(s)
            topic_el = def_el.xpath('./span[@class="topic-g"]/a')
            topic_href = topic_el.attrib['href']
            # seperate the href from ?level=... (topic_level)
            topic = topic_el.xpath('./span/span[@class="topic_name"]/text()')[0]

            collocations_el = def_el.xpath('./div[@class="collapse"]/span[@unbox="snippet"]/span[@class="body"]')[0]
            cols_els = collocations_el.getchildren()
            for ndx in range(0, len(cols_els), 2):
                if cols_els[ndx].tag == 'span' and cols_els[ndx].attrib['class'] == 'unbox' and \
                   cols_els[ndx + 1].tag == 'ul' and cols_els[ndx + 1].attrib['class'] == 'collocs_list':
                    head = cols_els[ndx].text_content()
                    body: list = cols_els[ndx + 1].xpath('./li[@class="li"]/text()')
            # certainly super fix this shit
            # this needs a ton of validation

        origin = defs_el.xpath('./div/span[@unbox="wordorigin"]/span[@class="body"]/span[@class="p"]')[0].text_content()

        related_entries_els = right_el.xpath('./div[@id="relatedentries"]/dl/dd/ul/li/a')
        for entry_el in related_entries_els:
            entry_href = entry_el.attrib['href']
            entry_name = entry_el.text_content()
            # TODO entry tipe
    