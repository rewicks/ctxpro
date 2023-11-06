
class="mini.gender"; echo $class; for end in {sentences,contexts}; do out=""; for langpair in {en-de,en-es,en-fr,en-it,en-pl,en-pt,en-ru}; do trg=$(echo $langpair | cut -d- -f2); out=$out"\t"$(ctxpro -t deepl-outputs/$class.opensubtitles.$langpair.test.$end -e jsons/$class.opensubtitles.en-$trg.test.json --lang $trg --quiet); done; echo -e $out; done; printf "\n\n"

class="mini.animacy"; echo $class; for end in {sentences,contexts}; do out=""; for langpair in {de-en,es-en,fr-en,it-en,pl-en,pt-en,ru-en}; do trg=$(echo $langpair | cut -d- -f2); out=$out"\t"$(ctxpro -t deepl-outputs/$class.opensubtitles.$langpair.test.$end -e jsons/$class.opensubtitles.$langpair.test.json --lang $trg --quiet); done; echo -e $out; done; printf "\n\n"

class="mini.formality"; echo $class; for end in {sentences,contexts}; do out=""; for langpair in {en-de,en-es,en-fr,en-it,en-pl,en-pt,en-ru}; do trg=$(echo $langpair | cut -d- -f2); out=$out"\t"$(ctxpro -t deepl-outputs/$class.opensubtitles.$langpair.test.$end -e jsons/$class.opensubtitles.en-$trg.test.json --lang $trg --quiet); done; echo -e $out; done; printf "\n\n"

class="auxiliary"; echo $class; for end in {sentences,contexts}; do out=""; for langpair in {en-de,en-es,en-fr,en-it,en-pl,en-pt,en-ru}; do trg=$(echo $langpair | cut -d- -f2); out=$out"\t"$(ctxpro -t deepl-outputs/$class.opensubtitles.$langpair.test.$end -e jsons/$class.opensubtitles.en-$trg.test.json --lang $trg --quiet); done; echo -e $out; done; printf "\n\n"

class="mini.inflection"; echo $class; for end in {sentences,contexts}; do out=""; for langpair in {en-pl,en-ru}; do trg=$(echo $langpair | cut -d- -f2); out=$out"\t"$(ctxpro -t deepl-outputs/$class.opensubtitles.$langpair.test.$end -e jsons/$class.opensubtitles.$langpair.test.json --lang $trg --quiet); done; echo -e $out; done; printf "\n\n"
