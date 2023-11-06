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
import string

from sentence_splitter import SentenceSplitter

from .evalsets import get_test_data, list_test_sets

################################ FUNCTIONS ###############################

def get_translation_stream(translations):
    if translations is None:
        for line in sys.stdin:
            yield line.strip()
    else:
        with open(translations) as infile:
            for line in infile:
                yield line.strip()

def get_last(input_line, splitter):
    """
    Splits an input and returns the last line.
    """
    sentences = splitter.split(text=input_line)
    if len(sentences) == 0:
        return input_line
    return sentences[-1]

def passes_test(translation, expected_form):
    translation = translation.lower()

    # get rid of punctuation for comparison
    stripped_translation = ""
    for t in translation:
        if t not in string.punctuation:
            stripped_translation += t

    # add spaces on either side so the exact match doesn't break
    translation = " " + stripped_translation + " "

    expected_form  = expected_form.lower()

    if f" {expected_form} " in translation:
        return True

    return False

def score(args):
    """
    Scores a set of translations against a set of rules.
    """
    splitter = SentenceSplitter(language=args.lang)

    references = get_test_data(args.eval_set)
    translations = get_translation_stream(args.translations)

    score_rules = {}
    for translation, ref in zip(translations, references):
        if ref["rule"] not in score_rules:
            score_rules[ref["rule"]] = {
                "correct": 0,
                "total": 0,
                "form": ref["expected"]
            }
        last_sentence = get_last(translation.strip(), splitter)
        if passes_test(last_sentence, ref["expected"]):
            score_rules[ref["rule"]]["correct"] += 1
        score_rules[ref["rule"]]["total"] += 1

    if args.pretty:
        print(f"rule (expected)\tcorrect\ttotal\taccuracy")
        print("-------------------------------------------")
        for rule, scores in score_rules.items():
            print(f"{rule} ({scores['form']})\t{scores['correct']}\t{scores['total']}\t{scores['correct']*100/scores['total']:.1f}%")
        print("-------------------------------------------")
        total_correct = sum([_['correct'] for _ in score_rules.values()])
        total = sum([_['total'] for _ in score_rules.values()])
        print(f"total\t\t\t{total_correct}\t{total}\t{total_correct*100/total:.1f}%")

    elif args.complete:
        for rule, scores in score_rules.items():
            print(f"{rule} ({scores['form']})\t{scores['correct']}\t{scores['total']}\t{scores['correct']*100/scores['total']:.1f}%")
        total_correct = sum([_['correct'] for _ in score_rules.values()])
        total = sum([_['total'] for _ in score_rules.values()])
        print(f"total\t{total_correct}\t{total}\t{total_correct*100/total:.1f}")
    else:
        total_correct = sum([_['correct'] for _ in score_rules.values()])
        total = sum([_['total'] for _ in score_rules.values()])
        print(f"{total_correct*100/total:.1f}")

################################ MAIN ################################

def main(args):
    score(args)
                               