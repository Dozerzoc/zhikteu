import json
import os.path
import re
from datetime import datetime
from natasha import (
    Segmenter,
    MorphVocab,
    NewsEmbedding,
    NewsMorphTagger,
    NewsNERTagger,
    PER,
    LOC,
    ORG,
    Doc
)
from pullenti_wrapper.langs import (
    set_langs,
    RU
)
from pullenti_wrapper.processor import (
    Processor,
    GEO,
    ADDRESS
)
from pullenti_wrapper.referent import Referent
set_langs([RU])

class NatashaNers:

    def __init__(self, input_data: object):
        self.data = input_data
        self.ner_of_texts = dict()

        segmenter = Segmenter()
        morph_vocab = MorphVocab()
        emb = NewsEmbedding()
        morph_tagger = NewsMorphTagger(emb)
        ner_tagger = NewsNERTagger(emb)

        dictionary = dict()
        dictionary['names'] = []
        dictionary['places'] = []
        dictionary['organizations'] = []
        dictionary['emails'] = []
        dictionary['phone_numbers'] = []

        text = self.data
        doc = Doc(text)
        doc.segment(segmenter)
        doc.tag_morph(morph_tagger)
        doc.tag_ner(ner_tagger)
        processor = Processor([GEO, ADDRESS])

        addr = []
        result = processor(text)
        if result.matches:
            for match in result.matches:
                referent = match.referent
                addr.append(self.display_shortcuts(referent))
            result = [dict(s) for s in set(frozenset(d.items()) for d in addr)]
            dictionary['places'].append(result)
        else:
            pass

        dictionary['text'] = text
        for span in doc.spans:
            span.normalize(morph_vocab)
            if span.type == PER:
                if span.normal not in dictionary['names']:
                    dictionary['names'].append(span.normal)
            elif span.type == LOC:
                if span.normal not in dictionary['places']:
                    dictionary['places'].append(span.normal)
            elif span.type == ORG:
                if span.normal not in dictionary['organizations']:
                    dictionary['organizations'].append(span.normal)

        email_pattern = re.compile(r"[a-z0-9]+[._]?[a-z0-9]+@\w+[.]?\w+[.]\w{2,3}")
        email_matches = email_pattern.findall(text)
        if email_matches:
            for g in email_matches:
                dictionary['emails'].append(g)
            dictionary['emails'] = list(set(dictionary['emails']))

        tel_pattern = re.compile(
            r"((8|\+374|\+994|\+995|\+375|\+7|\+380|\+38|\+996|\+998|\+993[\- ]?)?\(?\d{3,5}\)?"
            r"[\- ]?\d[\- ]?\d[\- ]?\d[\- ]?\d[\- ]?\d(([\- ]?\d)?[\- ]?\d)?)")
        tel_matches = tel_pattern.findall(text)
        if tel_matches:
            for g in tel_matches:
                dictionary['phone_numbers'].append(g[0])
            dictionary['phone_numbers'] = list(set(dictionary['phone_numbers']))

            for k, v in dictionary.items():
                if len(dictionary[k]) == 0:
                    dictionary[k] = None
        self.ner_of_texts = dictionary

    def display_shortcuts(self, referent, level=0):
        tmp = {}
        a = ""
        b = ""
        for key in referent.__shortcuts__:
            value = getattr(referent, key)
            if value in (None, 0, -1):
                continue
            if isinstance(value, Referent):
                self.display_shortcuts(value, level + 1)
            else:
                if key == 'type':
                    a = value
                if key == 'name':
                    b = value
                if key == 'house':
                    a = "дом"
                    b = value
                    tmp[a] = b
                if key == 'flat':
                    a = "квартира"
                    b = value
                    tmp[a] = b
                if key == 'corpus':
                    a = "корпус"
                    b = value
                    tmp[a] = b
        tmp[a] = b
        return tmp

    def extract_data(self):
        output_file = f'{str(datetime.now())}.json'
        with open(os.path.join('output', output_file), 'w') as f:
            f.write(json.dumps(self.ner_of_texts, ensure_ascii=False))
        with open(output_file, encoding='utf8') as f:
            contents = f.readlines()
            print(contents)
        return output_file

def get_result(file_data):
    return NatashaNers(file_data).ner_of_texts
