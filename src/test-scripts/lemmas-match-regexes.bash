#!/bin/bash
if ! ${srcdir}/test-scripts/lemmas-match-regexes.py \
        --input ${srcdir}/generated/master.tsv; then
    exit 1
fi
exit 0
