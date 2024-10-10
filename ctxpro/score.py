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
import random

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

def pairwise_bs(args):
    splitter = SentenceSplitter(language=args.lang)
    
    references = get_test_data(args.eval_set)
    translation_streams = [get_translation_stream(t) for t in args.translations]

    scores = []
    for t in translation_streams:
        scores.append([])
        for translation, ref in zip(t, references):
            last_sentence = get_last(translation.strip(), splitter)
            if passes_test(last_sentence, ref["expected"]):
                scores[-1].append(1)
            else:
                scores[-1].append(0)
    
    test_set_length = len(references)
    for s in scores:
        assert(len(s) == test_set_length)

    wins = [None] + [0 for _ in range(1, len(scores))]
    indices = [_ for _ in range(test_set_length)]
    for test in range(args.n_resamples):
        subsample_indices = random.sample(indices, args.k_subsamples)
        subsampled_scores = [[] for _ in scores]
        for i in subsample_indices:
            for j in range(len(scores)):
                subsampled_scores[j].append(scores[j][i]) # add the correct/incorrect value
        baseline_score = sum(subsampled_scores[0])
        for j in range(1, len(scores)):
            if baseline_score < sum(subsampled_scores[j]):
                wins[j] += 1
    out = []
    for system, sc, w in zip(args.translations, scores, wins):
        out.append({
            "system": system,
            "ctxpro": {
                "score": round((sum(sc) / test_set_length) * 100, 2),
                "p_value": None if w == None else 1 - (w / args.n_resamples),
            }
        }) 
    print(json.dumps(out, indent=2))

def score(args):
    """
    Scores a set of translations against a set of rules.
    """
    splitter = SentenceSplitter(language=args.lang)

    references = get_test_data(args.eval_set)
    translations = [get_translation_stream(t) for t in args.translations]

    scores = []
    for t in translations:
        score_rules = {}
        for translation, ref in zip(t, references):
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

        assert (sum([_['total'] for _ in score_rules.values()]) == len(references), "Reference and translations are not the same shape"

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
    if args.paired_bs:
        pairwise_bs(args)
    else:
        score(args)
                               
