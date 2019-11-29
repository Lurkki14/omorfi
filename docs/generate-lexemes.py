#!/usr/bin/env python3
# -*- coding: utf8 -*-
"""
This script converts Finnish TSV-formatted lexicon to github wiki
"""


# Author: Tommi A Pirinen <flammie@iki.fi> 2009, 2011

#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import argparse
import csv
from sys import stderr


def filenamify(s):
    repls = {'!': 'EXCL', '?': 'QQ', '"': 'DQUO', "'": 'SQUO', '/': 'SLASH',
             '\\': 'BACKSLASH', '<': 'LEFT', '>': 'RIGHT', ':': 'COLON',
             ' ': 'SPACE', '|': 'PIPE', '.': 'STOP', ',': 'COMMA',
             ';': 'SC', '(': 'LBR', ')': 'RBR', '[': 'LSQ',
             ']': 'RSQ', '{': 'LCURL', '}': 'RCURL', '$': 'DORA',
             '\t': 'TAB'}
    for needl, subst in repls.items():
        s = s.replace(needl, subst)
    return s


def markdownify(s):
    repls = {']': '(right square bracket)', '|': '(pipe symbol)',
             '[': '(left square bracket)'}
    for needl, subst in repls.items():
        s = s.replace(needl, subst)
    return s


def homonymify(s):
    # ₀₁₂₃₄₅₆₇₈₉
    if s == '1':
        return '₁'
    elif s == '2':
        return '₂'
    elif s == '3':
        return '₃'
    elif s == '4':
        return '₄'
    elif s == '5':
        return '₅'
    elif s == '6':
        return '₆'
    elif s == '7':
        return '₇'
    elif s == '8':
        return '₈'
    elif s == '9':
        return '₉'
    elif s == '10':
        return '₁₀'
    elif s == '11':
        return '₁₁'
    elif s == '12':
        return '₁₂'
    elif s == '13':
        return '₁₃'
    elif s == '14':
        return '₁₄'
    elif s == '15':
        return '₁₅'
    elif s == '16':
        return '₁₆'
    else:
        return s


def stuff2icon(s):
    if s == 'org':
        return 'org'
    elif s == 'geo':
        return '🌍'
    elif s == 'first':
        return '🧑¹'
    elif s == 'last':
        return '🧑²'

# standard UI stuff

def main():
    # initialise argument parser
    ap = argparse.ArgumentParser(
        description="Convert omorfi database to github pages")
    ap.add_argument("--quiet", "-q", action="store_false", dest="verbose",
                    default=False,
                    help="do not print output to stdout while processing")
    ap.add_argument("--verbose", "-v", action="store_true", default=False,
                    help="print each step to stdout while processing")
    ap.add_argument("--lexeme-docs", "-L", required=True,
                    metavar="LDFILE", help="read lexeme docs from LDFILE")
    ap.add_argument("--lexemes", "-l", required=True,
                    metavar="LEXENES", help="read lexemes data from LEXEMES")
    ap.add_argument("--version", "-V", action="version")
    ap.add_argument("--output", "-o", action="store", required=True,
                    type=argparse.FileType('w'),
                    metavar="OFILE", help="write docs OFILE")
    ap.add_argument("--outdir", "-O", action="store", required=True,
                    metavar="ODIR", help="write individual paradigms to " +
                    "ODIR/paradigm.md")
    ap.add_argument("--fields", "-F", action="store", default=2,
                    metavar="N", help="read N fields from master")
    ap.add_argument("--separator", action="store", default="\t",
                    metavar="SEP", help="use SEP as separator")
    ap.add_argument("--comment", "-C", action="append", default=["#"],
                    metavar="COMMENT", help="skip lines starting with COMMENT that"
                    "do not have SEPs")
    ap.add_argument("--strip", action="store",
                    metavar="STRIP", help="strip STRIP from fields before using")

    args = ap.parse_args()

    # write preamble to wiki page
    print('# Lexemes', file=args.output)
    print(file=args.output)
    print("_This is an automatically generated documentation based on omorfi" +
          "lexical database._", file=args.output)
    print(file=args.output)
    print("Lexemes are the word-entries of omorfi, currently we have only " +
            "documented the ones that are commonly problematic, in terms of " +
            "unexpected ambiguity, exceptional spelling or anything otherwise " +
            "worth noting. Full dictionary can be found for the time being " +
            "in wiktionary, or other such services.", file=args.output)
    print(file=args.output)
    # read from csv files

    print("| Lexeme | Short notes | Attributes |", file=args.output)
    print("|:------:|:-----------:|:----------:|", file=args.output)

    lexdata = dict()
    with open(args.lexemes, 'r', newline='') as tsv_file:
        tsv_reader = csv.DictReader(tsv_file, delimiter=args.separator,
                                    strict=True)
        for tsv_parts in tsv_reader:
            if len(tsv_parts) < 2 or tsv_parts['lemma'] is None or \
                    tsv_parts['homonym'] is None:
                print("Too few tabs on line, skipping:", tsv_parts)
                continue
            lexkey = tsv_parts['lemma'] + '\t' + tsv_parts['homonym']
            lexdata[lexkey] = tsv_parts
    with open(args.lexeme_docs, 'r', newline='') as tsv_file:
        tsv_reader = csv.DictReader(tsv_file, delimiter=args.separator,
                                    strict=True)
        prev_lemma = ''
        linecount = 0
        for tsv_parts in tsv_reader:
            linecount += 1
            if len(tsv_parts) < 2 or tsv_parts['doc'] == None:
                print("Too few tabs on line", linecount,
                      "skipping following line completely:", file=stderr)
                print(tsv_parts, file=stderr)
                continue
            if '\t' in tsv_parts['lemma']:
                print("ARGH python tsv fail on line:",
                      tsv_parts, file=stderr)
                continue
            print("| [%s](lexemes/%s.html) |" %
                  (markdownify(tsv_parts['lemma']) +
                   homonymify(tsv_parts['homonym']),
                   filenamify(tsv_parts['lemma'])), end='',
                  file=args.output)
            if tsv_parts['lemma'] != prev_lemma:
                outfile = open(args.outdir + '/' +
                           filenamify(tsv_parts['lemma']) +
                           '.markdown', 'w')
                prev_lemma = tsv_parts['lemma']
                print('---', file=outfile)
                print('layout: lexeme', file=outfile)
                print('lexeme:', tsv_parts['lemma'], file=outfile)
                print('---', file=outfile)
            print(file=outfile)
            print("### ", tsv_parts['lemma'] +
                  homonymify(tsv_parts['homonym']), file=outfile)
            print(" ", tsv_parts['doc'], end=' | ', file=args.output)
            print(file=outfile)
            print(tsv_parts['doc'], file=outfile)
            lexkey = tsv_parts['lemma'] + '\t' + tsv_parts['homonym']
            if lexkey in lexdata:

                print("* UPOS: ", lexdata[lexkey]['upos'], file=outfile)
                if 0 < int(lexdata[lexkey]['kotus_tn']) and\
                        int(lexdata[lexkey]['kotus_tn']) < 99:
                    print("* in KOTUS dictionary under: ",
                          lexdata[lexkey]['kotus_tn'], file=outfile)
                print("* Origin: ", lexdata[lexkey]['origin'],
                      file=outfile)
                if lexdata[lexkey]['proper_noun_class']:
                    print("* Possible NER class: ",
                          lexdata[lexkey]['proper_noun_class'], file=outfile)
                    print(stuff2icon(lexdata[lexkey]['proper_noun_class']),
                          file=args.output)
                if lexdata[lexkey]['prontype']:
                    print("* PronType: ",
                          lexdata[lexkey]['prontype'], file=outfile)
                if lexdata[lexkey]['adptype']:
                    print("* AdpType: ",
                          lexdata[lexkey]['adptype'], file=outfile)
                if lexdata[lexkey]['numtype']:
                    print("* NumType: ",
                          lexdata[lexkey]['numtype'], file=outfile)
                if lexdata[lexkey]['blacklist']:
                    print("* Blacklisted: ",
                          lexdata[lexkey]['blacklist'], file=outfile)
                    print("☢", file=args.output, end='')
                if lexdata[lexkey]['sem']:
                    print("* Semantic tags: ",
                          lexdata[lexkey]['sem'], file=outfile)
                    print(stuff2icon(lexdata[lexkey]['sem']),
                          file=args.output, end='')
            print(file=outfile)
            print(" |", file=args.output)
    print('''<!-- vim: set ft=markdown:-->''', file=args.output)
    exit()


if __name__ == "__main__":
    main()
