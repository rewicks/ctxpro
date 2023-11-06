#!/bin/bash

# Extracts JSON files to TSVs

src=en
#for trg in de es fr it pl pt ru; do
for trg in it; do
    langpair=en-$trg
    for file in *$langpair*.json; do
        mkdir -p tsv
        outfile=tsv/$(basename $file .json).tsv
        if [[ ! -s $outfile ]]; then
            echo "Extracting to $outfile..."
            ~/src/MultiPro/scripts/json2tsv.py -s $src -t $trg -m 250 --spm ~/src/MultiPro/data/spm/$langpair.joint.eos.spm --correct-only --json-file $file --documents-dir ~/src/MultiPro/data/opensubs/$langpair > $outfile
        fi
    done
done
