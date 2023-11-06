################################ PACKAGING AND LOGGING ################################
import pathlib
import logging
import os, sys
from typing import List, Set, Dict, Tuple

if (__package__ is None or __package__ == "") and __name__ == '__main__':
    parent = pathlib.Path(__file__).absolute().parents[1]
    sys.path.insert(0, str(parent))
    __package__ = 'ctxpro'


logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=os.environ.get("LOGLEVEL", "INFO").upper(),
    stream=sys.stderr,
)
logger = logging.getLogger("ctxpro")


################################ IMPORTS ################################

import argparse
import json
import tqdm

import spacy
from spacy_download import load_spacy

import torch

from fastcoref import FCoref

try:
    from simalign import SentenceAligner
except:
    FAIL_MESSAGE = """

    
    Failed to import simalign. Have you upgraded networkx?
    Try:

        pip install -U networkx
    """
    raise ValueError(FAIL_MESSAGE)

from .rules import RULES
from .checkers import Pronoun, Auxiliary, Inflection



################################ FUNCTIONS ################################

def get_alignments(aligner, english, tgt):
    """
        Returns the word alignments between two sentences.
    """
    try:
        return aligner.get_word_aligns([str(e) for e in english], [str(t) for t in tgt])
    except:
        return {"mwmf": []}


def read_input(input_stream):
    """
        Returns a single line at a time to the document generator.
        Will either return lines from standard input, or iterate over the files in a list
        If input_files is None, stdin is read. Otherwise, a tsv file is expected.
        Format should be tab-delimited columns of document, source, target.
    """
    if input_stream is None:
        logger.debug("Reading from stdin...")
        for line in sys.stdin:
            if len(line.strip().split("\t")) != 3:
                raise Exception("Input must be tab-delimited columns of document, source, target.")
            docid, src, tgt = line.strip().split("\t")
            yield docid, src, tgt
    else:
        logger.debug("Reading from input files...")
        for fi in input_stream:
            with open(fi) as infile:
                for line in infile:
                    if len(line.strip().split("\t")) != 3:
                        raise Exception("Input must be tab-delimited columns of document, source, target.")
                    docid, src, tgt = line.strip().split("\t")
                    yield docid, src, tgt


def read_documents(input_files, window_size, models):
    """
        A generator that yields a context windows one at a time from the input.
        For each source and target line in a document, they are tokenized via Spacy Models,
        and word alignments are precalculated for efficiency.
    """
    istream = read_input(input_files)

    src_doc = []
    tgt_doc = []
    alignments = []
    segid = 1 # segment id is 1-indexed.
    last_docid = None

    for docid, src, tgt in istream:

        if last_docid is not None and docid != last_docid:
            # reset the document (empty context)
            src_doc = []
            tgt_doc = []
            alignments = []
            segid = 0

        # tokenize English (source)
        src = models["english_spacy"](src.strip())
        src_doc.append(src)

        # tokenize target
        tgt = models["target_spacy"](tgt.strip())
        tgt_doc.append(tgt)

        # get word alignments
        a = get_alignments(models["aligner"], src, tgt)
        alignments.append(a)

        src_doc = src_doc[-window_size:]
        tgt_doc = tgt_doc[-window_size:]
        alignments = alignments[-window_size:]

        yield segid, docid, src_doc, tgt_doc, alignments

        last_docid = docid
        segid += 1

def build_models(target, cpu=False):
    """
    Loads coreference model and word aligner. Also loads the spacy models for English and the target language.
    :param target: target language
    :param cpu: use CPU instead of GPU
    :return: models
    """
    if cpu or not torch.cuda.is_available():
        logger.debug("Using cpu...")
        device = torch.device('cpu')
    else:
        logger.debug("Using cuda device...")
        device = torch.device('cuda')
    
    logger.debug("Loading coreference model...")

    # We must disable a bunch of logging from fastcoref to avoid spamming the user.
    fcoref_logger = logging.getLogger("fastcoref.modeling")
    fcoref_logger.setLevel(logging.WARNING)
    from datasets.utils.logging import disable_progress_bar
    disable_progress_bar()

    # now actually load the model
    coref_model = FCoref(device=device, enable_progress_bar=False)

    logger.debug("Loading the simalign model...")
    aligner = SentenceAligner(model="bert", token_type="bpe", matching_methods="mai")

    logger.debug("Loading the English spacy model...")
    english_spacy = load_spacy("en_core_web_trf")

    logger.debug(f"Loading Spacy's {target} model...")
    if target == "fr":
        target_spacy = load_spacy("fr_dep_news_trf")
    elif target == "de":
        target_spacy = load_spacy("de_dep_news_trf")
    elif target == "es":
        target_spacy = load_spacy("es_dep_news_trf")
    elif target == "ru":
        target_spacy = load_spacy("ru_core_news_lg")
    elif target == "it":
        target_spacy = load_spacy("it_core_news_lg")
    elif target == "pt":
        target_spacy = load_spacy("pt_core_news_lg")
    elif target == "pl":
        target_spacy = load_spacy("pl_core_news_lg")
    else:
        logger.error("Unsupported target language!")
        exit(-1)

    models = {
        "coref_model": coref_model,
        "aligner": aligner,
        "english_spacy": english_spacy,
        "target_spacy": target_spacy
    }

    return models


def build_rules(rule_files, coref_model):
    rules = {}
    for f in rule_files:
        if f in RULES:
            logger.debug(f"Using predefined rule set from {f}...")
            rule_json = RULES[f]
        else:
            logger.debug(f"Loading rules from {f}...")
            rule_json = json.load(open(f))
        rules.update(rule_json)
    out = []
    for name, r in rules.items():
        if r["type"] == "pronoun":
            logger.info("Building Pronoun rule %s", name)
            out.append(Pronoun(name, r, coref_model))
        elif r["type"] == "auxiliary":
            logger.info("Building Auxiliary rule %s", name)
            out.append(Auxiliary(name, r))
        elif r["type"] == "inflection":
            logger.info("Building Inflection rule %s", name)
            out.append(Inflection(name, r))
    return out


def annotate(args):
    """
        Main annotation loop
    """
    logger.info("Loading models...")
    models = build_models(args.target, cpu=args.cpu)
    logger.info("Loading rules...")
    rules = build_rules(args.rules, models["coref_model"])

    document_generator = read_documents(args.input_files, args.window_size, models)

    outputs = {}
    for r in rules:
        outputs[r.name] = []
    
    try:
        # Iterate over context windows (sliding, overlapping window)
        for seg_id, docid, eng, tgt, alignments in tqdm.tqdm(document_generator):
            # for each example with preceding context, check if it passes each rule
            for rule in rules:
                check, out = rule.check(eng, tgt, alignments)
                # if it passes, add it to the output
                if check == 0:
                    logger.debug(f"Found an example for {rule.name}!")
                    logger.debug(json.dumps(out, indent=2, ensure_ascii=False))

                    # add some additional metadata
                    out["segment id"] = seg_id+1
                    out["document id"] = docid
                    out["errors"] = []
                    out["rule"] = rule.name
                    outputs[rule.name].append(out)
    except KeyboardInterrupt:
        logger.info("Stopping due to keyboard interrupt. Please wait to write files...")

    for r in outputs:
        logger.info(f"Final count: {len(outputs[r])} examples for {r}.")

    os.makedirs(args.output_dir, exist_ok=True)

    for r in outputs:
        with open(os.path.join(args.output_dir, r + ".json"), "w") as f:
            json.dump(outputs[r], f, indent=2, ensure_ascii=False)


################################ MAIN ################################


def main(args):
    annotate(args)
                                            


