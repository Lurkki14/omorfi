#!/bin/bash

for f in lexemes.tsv attributes/*.tsv ; do
    python/tsvsort.py -i $f -o $f.sort -v
    sed -e 's/\\\\\\/\\/' $f.sort > $f
done

