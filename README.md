# Introduction

Machine translation research is primarily focused on the sentence-level paradigm. In efforts to push the field towards translation _in context_, we release `ctxpro` which can extract parallel sentences which require additional document-context to translate.

Further, we release evaluation sets (`release/jsons`) as a resource to the community.

For more information, please read our paper:
 - [Rachel Wicks and Matt Post (2023):
   Identifying Context-Dependent Translations for Evaluation Set Production](https://arxiv.org/abs/2311.02321) In _Proceedings of WMT 2023_.

## Quick start

`ctxpro` is available via PyPi:

```
pip install ctxpro
```

# Scoring

You can use `ctxpro` to evaluation your machine translation outputs.

If using one of our evaluation sets (such as the EN-DE Gender test set shown below), it is a simple call:

```
# We can read via standard input
cat translations.gender.en-de.test.txt | ctxpro score -e en-de/gender/test -l de

# Or from a file
ctxpro score -t translations.gender.en-de.test.txt -e en-de/gender/test -l de
```

If you want to replicate the scores form our paper, there is a script in `paper/score.sh` which contains these commands for each [mini] test set.


# Extraction

You may wish to extract the surrounding contexts to use as input to your machine translation model. We parameterize this as the amount of _preceding_ context that you wish to extract in terms of number of tokens or sentences.

For the evaluation sets we release, we have extracted a default amount of context (up to 10 sentences of 256 words) which are available under `release/inputs/`. The contexts we use for the paper can be found in `paper/inputs`. These contain an "\<eos> " separator, but were removed before passing to DeepL.

If you wish to extract a different context amount, you will need to set up the OpenSubtitles data for your preferred language pair (see section below).

To extract contexts from a specific evaluation set, you may use the following command:

```
# Extract maximum 5 sentences or 128 tokens
ctxpro extract -i data/opensubs/de-en/de-en.tsv -e en-de/gender/test -s 5 -t 128 --joining_string "<eos> "
```

### Setting up OpenSubtitles

You have to setup OpenSubtitles for the language you care about. This includes downloading, unpacking, and then expanding into a format that organizes the files by year. Run the file `data/opensubtitles/setup.sh` to do this. It takes one argument, the language pair, e.g.,

    cd data/opensubs
    ./setup.sh de-en

Note that OpenSubtitles does the language-pair in alphabetical order, so the language pairs we support are `de-en`, `en-es`, `en-fr`, `en-it`, `en-pl`, `en-pt`, and `en-ru`. We assume an English source, so you may have to reverse the source and target columns in `de-en.tsv` (i.e. with something like `awk -F'\t' '{print $1 "\t" $3 "\t" $2}'`) when piping into `ctxpro`.

# Identify New Examples

Identifying new examples requires more functionality than either extraction or scoring. To install the packages for identification, you will need to install the `ctxpro[identify]` package:

```
# There is an incompatability with the networkx versioning, so you will also need to update after installation.
pip install ctxpro[identify]; pip install -U networkx
```

If you would like to apply our rules to new data, it is rather simple. For example, you can easily apply our rules to wmt test sets using `sacrebleu` which will echo documents in the appropriate format.

```
# Read directly from standard input

sacrebleu -t wmt22 -l en-de --echo docid src ref | ctxpro identify -r DE_GENDER DE_FORMALITY DE_AUXILIARY -t de


# Or read from file(s)

sacrebleu -t wmt22 -l en-de --echo docid src ref > wmt22.en-de
sacrebleu -t wmt21 -l en-de --echo docid src ref > wmt21.en-de

ctxpro -i wmt22.en-de wmt21.en-de -r DE_GENDER DE_FORMALITY DE_AUXILIARY -t de
```

## Rules

A series of predefined rules are provided as defined in the original paper. They are also located in the `data/rules` folder.

Alternatively, you can create your own. If you follow our structure, you can write a `.json` file (examples in `data/rules`) which the `ctxpro/checkers.py` classes will follow.

For the most flexibility, you can add your own system of criteria to the `ctxpro/checkers.py` file.

### Animacy

As you may notice, the extract pipeline assumes _English_ as the source. Animacy is the sole category here where the ambiguity exists when translating _into_ English as the target language. In our paper, we leverage the fact that the Gender ambiguity out-of-English is parallel to the Animacy ambiguity into-English. To identify Animacy ambiguities, you can extract the Gender examples and reverse the language direction in the resulting `.json` file with the script in `scripts/reverse.py`. An example showing the reverses we made to create the evaluation sets is in `scripts/reverse.sh.`
