import validators

from scrapy.item import Item, Field
from utils.web.scrapy_handler import ScrapyHandler as H
from utils.web.itemloader import TFCompose, ItemLoader
from itemloaders.processors import Compose, MapCompose


class Topic(Item):
    name: str = Field()
    url: str = Field()

class TopicLoader(ItemLoader):
    default_item_class = Topic

    name_in = TFCompose(H.pvalidate(tipe=str, value_exc=str()), str.strip)
    url_in = TFCompose(H.pvalidate(tipe=str), str.strip,
                       H.pvalidate(validation=validators.url))

class Collocation(Item):
    abstract: str = Field()
    examples: list[str] = Field()

class CollocationLoader(ItemLoader):
    default_item_class = Collocation

    abstract_in = TFCompose(H.pvalidate(tipe=str, value_exc=str()))
    examples_in = MapCompose(H.pvalidate(tipe=str, value_exc=str()), str.strip)

class DefinitionItem(Item):
    index: int = Field()
    definition: str = Field()
    examples: list[str] = Field()
    topics: list[Topic] = Field()
    collocations: list[Collocation] = Field()

class DefinitionLoader(ItemLoader):
    default_item_class = DefinitionItem

    index_in = TFCompose(H.pvalidate(tipe=int))
    definition_in = TFCompose(H.pvalidate(tipe=str, value_exc=str()))
    examples_in = MapCompose(H.pvalidate(tipe=str, value_exc=str()))
    topics_in = Compose(H.pvalidate(tipe=list, validation=lambda x: len(x) > 0))
    collocations_in = Compose(H.pvalidate(tipe=list, validation=lambda x: len(x) > 0))

class RelatedEntryItem(Item):
    url: str = Field()
    name: str = Field()
    tipe: str = Field()

class RelatedEntryLoader(ItemLoader):
    default_item_class = RelatedEntryItem

    url_in = TFCompose(H.pvalidate(tipe=str), str.strip,
                       H.pvalidate(validation=validators.url))
    name_in = TFCompose(H.pvalidate(tipe=str, value_exc=str()), str.strip)
    tipe_in = TFCompose(H.pvalidate(tipe=str, value_exc=str()), str.strip)

class WordItem(Item):
    # ?? https://www.oxfordlearnersdictionaries.com/definition/english/glamour_1?q=glamour
    url: str = Field()   # https://www.oxfordlearnersdictionaries.com/definition/english/glamour_1
    query: str = Field() # glamour_1 TODO: seperate the number _1
    word: str = Field()
    tipe: str = Field()  # noun, verb, etc
    uk_pronunciation: str = Field()
    uk_phonetics: str = Field()
    us_pronunciation: str = Field()
    us_phonetics: str = Field()
    american_variant: str = Field()
    grammar_traits: list[str] = Field()
    definitions: list[DefinitionItem] = Field()
    origin: str = Field()
    related_entries: list[RelatedEntryItem] = Field()

class WordLoader(ItemLoader):
    default_item_class = WordItem

    url_in = TFCompose(H.pvalidate(tipe=str), str.strip,
                       H.pvalidate(validation=validators.url))
    query_in = TFCompose(H.pvalidate(tipe=str, value_exc=str()), str.strip)
    word_in = TFCompose(H.pvalidate(tipe=str, value_exc=str()), str.strip)
    tipe_in = TFCompose(H.pvalidate(tipe=str, value_exc=str()), str.strip)
    uk_pronunciation_in = TFCompose(H.pvalidate(tipe=str), str.strip,
                       H.pvalidate(validation=validators.url))
    uk_phonetics_in = TFCompose(H.pvalidate(tipe=str, value_exc=str()), str.strip)
    us_pronunciations_in = TFCompose(H.pvalidate(tipe=str), str.strip,
                       H.pvalidate(validation=validators.url))
    us_phonetics_in = TFCompose(H.pvalidate(tipe=str, value_exc=str()), str.strip)
    american_variant_in = TFCompose(H.pvalidate(tipe=str, value_exc=str()), str.strip)
    grammar_traits_in = MapCompose(H.pvalidate(tipe=str, value_exc=str()), str.strip)
    definitions_in = Compose(H.pvalidate(tipe=list, validation=lambda x: len(x) > 0))
    related_entries_in = Compose(H.pvalidate(tipe=list, validation=lambda x: len(x) > 0))
