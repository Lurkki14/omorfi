#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Beta-testing a wack idea of not disambiguating and dependency parsing at the
same time. Pay no attention to the man behind the curtains and move along.
"""

from sys import argv
# stuff
import xml.etree.ElementTree
from xml.etree.ElementTree import Element

from ..fileformats import next_conllu
from .evidence import Evidence
from .matcher import Matcher


class Disamparsulator:
    """Disamparsulator is one such non-parser."""

    def __init__(self):
        self.rules = list()

    def frobblesnizz(self, f):
        '''parse disampursalations from XML file.'''
        xmltree = xml.etree.ElementTree.parse(f)
        root = xmltree.getroot()
        if root.get("version") != "0.0.0":
            print("Unsupported version", root.get("version"))
        rules = list()
        for child in root:
            # parse stuff
            if child.tag == 'evidences':
                self.parse_evidences(child)
            else:
                print("Unknown element disamparsulations:", child.tag)
                exit(2)
        return rules

    def parse_evidences(self, evidences: Element):
        for child in evidences:
            if child.tag == 'evidence':
                e = self.parse_evidence(child)
                self.rules.append(e)
            else:
                print("Unknown element in evidences:", child.tag)
                exit(2)

    def parse_evidence(self, evidence: Element):
        '''Parse evidence element block.'''
        e = Evidence()
        e.name = evidence.get('name')
        for child in evidence:
            if child.tag == 'target':
                e.target = self.parse_target(child)
            elif child.tag == 'likelihood':
                e.probability = self.parse_likelihood(child)
            elif child.tag == 'depname':
                e.depname = self.parse_depname(child)
            elif child.tag == 'context':
                e.context = self.parse_context(child)
            elif child.tag == 'documentation':
                pass
            else:
                print("Unknown element under evidence:", child.tag)
                exit(2)
        return e

    def parse_target(self, target: Element):
        '''Parse target definition element.'''
        m = Matcher()
        for child in target:
            if child.tag == 'match':
                m = self.parse_match(child)
            else:
                print("Unknown element under target:", child.tag)
                exit(2)
        return m

    def parse_match(self, match: Element):
        m = Matcher()
        for child in match:
            if child.tag == 'upos':
                upos = self.parse_upos(child)
                m.uposes.append(upos)
            elif child.tag == 'lemma':
                ufeats = self.parse_lemma(child)
                m.lemmas.append(ufeats)
            elif child.tag == 'ufeats':
                ufeats = self.parse_ufeats(child)
                m.ufeatses.append(ufeats)
            else:
                print("Unknown element under target:",
                      xml.etree.ElementTree.tostring(child))
        return m

    def parse_likelihood(self, likelihood: Element):
        '''Parse likelihood element.'''
        if likelihood.text == 'usually':
            return 16.0
        elif likelihood.text == 'unlikely':
            return -16.0
        elif likelihood.text == 'uncommonly':
            return -4.0
        elif likelihood.text == 'probably':
            return 4.0
        elif likelihood.text == 'possibly':
            return 8.0
        else:
            print("Unknown likelihood:", likelihood.text)
            exit(2)

    def parse_depname(self, depname: Element):
        '''Parse depname element.'''
        return depname.text

    def parse_context(self, context: Element):
        '''Parse context element.'''
        c = dict()
        for child in context:
            if child.tag == 'location':
                c['location'] = self.parse_location(child)
            elif child.tag == 'match':
                c['matcher'] = self.parse_match(child)
            elif child.tag == 'barrier':
                c['barrier'] = self.parse_barrier(child)
            else:
                print("Unknown child for context", child)
                exit(2)
        return c

    def parse_upos(self, upos: Element):
        '''Parse upos element.'''
        if upos.text not in ['NOUN', 'VERB', 'ADV', 'ADJ', 'ADP',
                             'INTJ', 'PUNCT', 'SYM', 'CCONJ', 'SCONJ',
                             'PRON', 'NUM']:
            print("invalid upos in", xml.etree.ElementTree.tostring(upos))
        return upos.text

    def parse_lemma(self, lemma: Element):
        '''Parse upos element.'''
        return lemma.text

    def parse_location(self, location: Element):
        '''Parse location element.'''
        return location.text

    def parse_ufeats(self, ufeats: Element):
        '''Parse ufeats element.'''
        ufs = dict()
        for child in ufeats:
            if child.tag == 'ufeat':
                name, value = self.parse_ufeat(child)
                ufs[name] = value
            else:
                print("Unknown child for ufeats", child)
                exit(2)
        return ufs

    def parse_ufeat(self, ufeat: Element):
        '''Parse ufeat element.'''
        return ufeat.get('name'), ufeat.text

    def parse_barrier(self, barrier: Element):
        '''Parse barrier element.'''
        m = Matcher()
        for child in barrier:
            if child.tag == 'match':
                m = self.parse_match(child)
        return m

    def linguisticate(self, sentence: list):
        '''Not a parsing function.'''
        #
        for token in sentence:
            for rule in self.rules:
                rule.apply(token, sentence)


def main():
    """Invoke a simple CLI analyser."""
    if len(argv) < 2:
        print("Usage:", argv[0], "ANALYSER INFILE")
        exit(1)
    from .omorfi import Omorfi
    omorfi = Omorfi(True)
    omorfi.load_analyser(argv[1])
    infile = open(argv[2])
    eoffed = False
    while not eoffed:
        sent = next_conllu(infile)
        if not sent:
            continue
        for token in sent:
            if token.error == "eof":
                eoffed = True
                break
            omorfi.analyse(token)
            omorfi.guess(token)
        # linguisticate(sent)
        for token in sent:
            print(token.printable_conllu())
    exit(0)


if __name__ == "__main__":
    main()
