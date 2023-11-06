#!/bin/bash

files=${1:-*.json}

for file in $files; do
    outfile=tsv/$(basename $file)
    [[ -s $outfile ]] && continue

    langpair=$(echo $file | cut -d. -f3)
    src=$(echo $langpair | cut -d- -f1)
    trg=$(echo $langpair | cut -d- -f2)
    spmfile=spm/$langpair.joint.eos.spm
    opensubs=../data/opensubs/$langpair

    [[ ! -e $spmfile ]] && continue
    [[ ! -d $opensubs ]] && continue

    echo -n "Processing $file to $outfile..."

    [[ ! -d tsv ]] && mkdir tsv
    echo ../scripts/json2tsv.py -s $src -t $trg -d $opensubs --max-sents 10 --max-tokens 250 --separator " <eos>" --spm $spmfile --json-file $file
    ../scripts/json2tsv.py -s $src -t $trg -d $opensubs --max-sents 10 --max-tokens 250 --separator " <eos>" --spm $spmfile --json-file $file > $outfile
done
