import re
from collections import defaultdict
import xml.etree.ElementTree as et
"""
Helperfunctions to deal with XML
"""

def etree_to_dict(t):
    """
    converts an etree xml to a dictionary
    """
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.items():
                dd[k].append(v)
        d = {t.tag: {k:v[0] if (len(v) == 1 and ~isinstance(v[0], type(dict()))) else v for k, v in dd.items()}}
    if t.attrib:
        d[t.tag].update(('@' + k, v) for k, v in t.attrib.items())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
              d[t.tag]['#text'] = text
        else:
            d[t.tag] = text
    return d

def strip_ns(tag):
    """
    strips the namespace from a string
    """
    return re.sub("^\{.*\}", '', tag)


def dict_key_apply(iterable, str_fkt):
    """
    Applys a string modifiying function to all keys of a nested dict.
    """
    if type(iterable) is dict:
        for key in iterable.keys():
            new_key = str_fkt(key)
            iterable[new_key] = iterable.pop(key)
            if type(iterable[new_key]) is dict or type(iterable[new_key]) is list:
                iterable[new_key] = dict_key_apply(iterable[new_key], str_fkt)
    elif type(iterable) is list:
        for item in iterable:
            item = dict_key_apply(item, str_fkt)
    return iterable

def xml2dict(xml, stripns=True):
    dic = etree_to_dict(xml)
    if stripns:
        dic = dict_key_apply(dic, strip_ns)
    return dic
