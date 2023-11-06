#!/bin/bash

# Downloads OpenSubtitles, and then unpacks into an expected directory structure.
#
# Usage: setup.sh en-de

set -eu

langpair=$1
src=$(echo $langpair | cut -d- -f1)
trg=$(echo $langpair | cut -d- -f2)
basedir=$(dirname $(realpath $0))

mkdir -p $langpair
cd $langpair

# download OpenSubtitles 2018 EN-DE and unzip
file=$langpair.txt.zip
if [[ ! -s $file ]]; then
    url="http://opus.nlpl.eu/download.php?f=OpenSubtitles2018/$langpair.txt.zip"
    wget $url -O $file
    unzip $file
fi

# extract documents
if [[ ! -d $langpair/2000 ]]; then
    mkdir -p documents
    perl $basedir/opusXML2docs.pl --ids OpenSubtitles.$langpair.ids --l1 $src --l2 $trg --outdir documents --source OpenSubtitles.$langpair.$src --target OpenSubtitles.$langpair.$trg

    # organize into folders
    for file in documents/*; do
        mkdir -p -- "${file%%_*}"
        mv -- "$file" "${file%%_*}"
    done
    mv documents/* .
    rmdir documents

    rm -rf 1191
fi

# Create a single consolidated TSV with docid, src, trg
for srcfile in */*.$src; do 
    name=$langpair"/"$(echo $srcfile | sed "s/\.$src\$//g")
    trgfile=$(echo $srcfile | perl -pe "s/\.$src\$/.$trg/")
    paste $srcfile $trgfile | $dirname/../../scripts/broadcast -i 0 $name 
done > $langpair.tsv

# cleanup
#rm -f OpenSubtitles*
#rm -f doc.order.$langpair.txt
rm -f README
rm -f $langpair.txt.zip
