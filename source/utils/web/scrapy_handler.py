import functools
import urllib
import scrapy
from typing import Union, List
from scrapy.selector import (
    Selector as ScrapySelector,
    SelectorList as ScrapySelectorList
)

HandlerElementType = Union[ScrapySelector, ScrapySelectorList, None]

def handler_decorator(func):
    """This only works for @classmethod"""

    @functools.wraps(func)
    def wrapper_handler(cls, el: HandlerElementType, repetitive: Union[bool, int] = 3,
                        raise_exception=False, **kwargs):
        if repetitive is False:
            repetitive = 1

        counter = 0
        response = None
        while counter < repetitive:
            response = func(cls, el, **kwargs)
            if response is not None:
                break

            counter += 1

        if raise_exception and (response is None or response is False):
            raise Exception("Operation Failed.")
        return response

    return wrapper_handler


class ScrapyHandler:
    @classmethod
    @handler_decorator
    def get_element(cls, el: HandlerElementType, xpath: str, many=False) \
        -> HandlerElementType:
        n_el = el.xpath(xpath)
        if not n_el:
            return None
        if many:
            return n_el
        else:
            return n_el[0]

    @classmethod
    @handler_decorator
    def get_attr(cls, el: HandlerElementType, attr: str) -> Union[str, None]:
        if attr == 'text':
            expr: str = el._expr
            if expr[expr.rfind('/'):] == '/text()':
                return el.get()
            else:
                return el.xpath('./text()').get()
        else:
            return el.css(f'::attr({attr})').get()

    @classmethod
    @handler_decorator
    def call_attr(cls, el: HandlerElementType, attr: str, **kwargs) -> bool:
        try:
            getattr(el, attr)(**kwargs)
            return True
        except AttributeError:
            return False

    @classmethod
    def validate(cls, value, none=True, tipe=None, value_exc=None, validation=None, post=None) -> bool:
        success = dict()

        if none and value is not None:
            success['none'] = True
        elif none and value is None:
            success['none'] = False

        if tipe is not None and isinstance(value, tipe):
            success['tipe'] = True
        elif tipe is not None:
            success['tipe'] = False

        if value_exc is not None and value == value_exc:
            success['value_exc'] = False
        elif value_exc is not None and value != value_exc:
            success['value_exc'] = True

        try:
            if validation is not None and validation(value) is True:
                success['validation'] = True
            elif validation is not None and validation(value) is not True:
                success['validation'] = False
        except Exception:
            success['validation'] = False

        end_success = True
        if none:
            end_success &= success['none']

        for k in ['tipe', 'value_exc', 'validation']:
            if locals()[k] is not None:
                end_success &= success[k]

        if end_success:
            if post is not None:
                value = post(value)
            return value

        return None

    @classmethod
    def pvalidate(cls, none=True, tipe=None, value_exc=None, validation=None, post=None):
        kw = {"none": none, 'tipe': tipe, "value_exc": value_exc, "validation": validation, "post": post}
        kw = {k: v for k, v in kw.items() if v is not None}
        if kw:
            return functools.partial(cls.validate, **kw)

    @classmethod
    def add_validated(cls, store: dict, key: str, value, post=None,
                      none=True, tipe=None, value_exc=None, validation=None) -> bool:
        validated = cls.validate(value, none=none, tipe=tipe, value_exc=value_exc, validation=validation)
        if validated:
            if post is not None:
                value = post(value)
            store[key] = value

        return validated

    @classmethod
    def urlify(cls, scheme=str(), netloc=str(), path=str(), params=str(), query=str(), fragment=str()) -> str:
        return urllib.parse.urlunparse((scheme, netloc, path, params, query, fragment))
