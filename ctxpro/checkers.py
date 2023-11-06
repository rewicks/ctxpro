####################################### PACKAGING AND LOGGING ############################################
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


################################################ IMPORTS ###################################################

from collections import Counter
from itertools import groupby, count

############################################################################################################

################################################ AUXILIARY #################################################

############################################################################################################

class Auxiliary():
    """
        Rule class that handles the "Auxiliary" class as described in paper.
        This is exemplified by the following context:
        
        "Do you even want to go to the party?"
        "I do." ["I do want to go"]
    """
    def __init__(self, name, rule):
        self.name = name
        
        # English lemma is the English auxiliary base form (do, will, may, etc)
        self.english_lemma = rule["english_lemma"]

        # disallowed lemmas are the target direct translations (faire, hacer, etc)
        self.disallowed_aligned_lemmas = rule["disallowed_aligned_lemmas"]

    def has_english_form(self, english_sent):
        """
        This function checks that the specified English lemma is in the input sentence
        Returns the index of the lemma and the token itself
        """
        for i, e in enumerate(english_sent):
            if e.lemma_ == self.english_lemma:
                return i, e
        return -1, -1

    def no_other_verbs(self, english_sent):
        """
        This functions ensures the specified English lemma is the only verb in the input sentence
        Returns if the sentence has no other verbs. If it does, the index of the other verb, and the token itself
        """
        for i, e in enumerate(english_sent):
            if (e.lemma_ != self.english_lemma and e.pos_ == "VERB") or (e.lemma_ != self.english_lemma and e.pos_ == "AUX"):
                return False, i, e
        return True, None, None

    def get_aligned_verb(self, e_idx, tgt_sent, alignments):
        """
        This functions identify which target word is aligned to the specified English lemma.
        Returns the index of the aligned word and the token itself
        """
        for src_index, tgt_index in alignments["mwmf"]:
            if src_index == e_idx and tgt_sent[tgt_index].pos_ == "VERB":
                return tgt_index, tgt_sent[tgt_index]
        return -1, -1

    def get_preceding_reference(self, tgt_lemma_, tgt_doc):
        """
        This function identifies the preceding reference by identifying where the target lemma has appeared before (closest)
        Returns all examples of the target lemma appearing before the current sentence by sentence index and token index
        """
        previous_references = []
        for i, tgt_sent in enumerate(tgt_doc[::-1]):
            for j, tgt_tok in enumerate(tgt_sent):
                if tgt_tok.lemma_ == tgt_lemma_:
                    previous_references.append((len(tgt_doc) - i - 1, j))
        return previous_references

    def get_aligned_reference(self, tgt_idx, english_sent, alignments):
        """
        This function identifies the English preceding form by identifying which English word is aligned to the target word
        Returns the most recent example and returns the token index and the token itself
        """
        for src_index, tgt_index in alignments["mwmf"]:
            if tgt_index == tgt_idx and english_sent[src_index].pos_ == "VERB":
                return src_index, english_sent[src_index]
        return -1, -1

    def check(self, english_doc, tgt_doc, alignments):
        """
        This function checks that the last sentence of the english and target documents
        follow all criteria of the specified rule with the context provided by the document
        """

        # Check that the last sentence of the English document has the specified English lemma
        idx, english_tok = self.has_english_form(english_doc[-1])
        if idx == -1:
            # Return values can be used later for the reasons why the rule failed
            # This is not default behavior, you would need to alter the code-base
            return 1, None

        # Check that the last sentence of the English document has no other verbs
        no_verb, v_idx, v_tok = self.no_other_verbs(english_doc[-1])
        if not no_verb:
            logger.debug(f"There's a second verb ({v_tok}) in the sentence.")
            return 2, v_tok

        # Finds the aligned verb in the target document
        aligned_verb_idx, aligned_verb = self.get_aligned_verb(idx, tgt_doc[-1], alignments[-1])
        if aligned_verb_idx == -1:
            logger.debug(f"Could not find a valid verb alignment.")
            return 3, None

        # Check that the aligned verb is not a disallowed lemma (i.e, a direct translation)
        if aligned_verb.lemma_ in self.disallowed_aligned_lemmas:
            logger.debug(f"The aligned verb has the incorrect lemma of {aligned_verb.lemma_} from the form {aligned_verb}.")
            return 4, aligned_verb

        # gets a list of the preceding references of the aligned verb
        antes = self.get_preceding_reference(aligned_verb.lemma_, tgt_doc[:-1])
        if len(antes) == 0:
            # this means there are no other forms of the aligned verb in the document--probably difficult or impossible to resolve.
            logger.debug(f"No preceding form found.")
            return 5, None

        # gets the most recent preceding reference of the aligned verb
        english_aligned_ante = None
        for ante_index, ante_token_idx in antes:
            english_alignment_idx, english_alignment_tok = self.get_aligned_reference(ante_token_idx, english_doc[ante_index], alignments[ante_index])
            if english_alignment_idx != -1:
                if english_alignment_tok.lemma_ != self.english_lemma:
                    english_aligned_ante = english_alignment_tok
                    break

        if english_aligned_ante is None:
            logger.debug("Could not find a valid aligned English verb")
            return 6, None

        out = {
                "src verb": str(english_tok),
                "expected": str(aligned_verb),
                "ante distance": len(english_doc)-ante_index-1,
                "ref verb lemma": str(aligned_verb.lemma_),
                "ref segment": str(tgt_doc[-1]),
                "ref ante segment": str(tgt_doc[ante_index]),
                "src verb lemma": str(english_tok.lemma_),
                "src segment": str(english_doc[-1]),
                "src ante segment": str(english_doc[ante_index]),
                "src ante verb lemma": str(english_aligned_ante.lemma_)
        }

        return 0, out


############################################################################################################

############################################# INFLECTIONS ##################################################

############################################################################################################

class Inflection():
    def __init__(self, name, rule):
        """
            Rule class that handles the "Inflection" class as described in paper.
            This is exemplified by the following context:
            
            "Do you even want to go to the party?"
            "Or the bar?" ("bar" is the same inflectional case as "party")
        """
        self.name = name
        self.case = rule["case"]

    def has_no_verb(self, sent):
        """
        This function identifies that the input sentence has no verbs that may imply the noun case.
        """
        for tok in sent:
            if tok.pos_ in ["VERB", "AUX"]:
                return False
        return True

    def has_correct_case(self, tgt_sent):
        """
        This function identifies that the target token has the same case as this rule.
        Returns the token with the correct case and its index in the sentence.
        """
        case_token = None
        case_token_idx = -1
        for i, tok in enumerate(tgt_sent):
            for c in tok.morph.get("Case"):
                if c == self.case:
                    case_token = tok
                    case_token_idx = i
                else:
                    return None, -1
        return case_token, case_token_idx

    def find_similar_preceding_token(self, tgt_doc):
        """
        This function finds the most recent token in the target document that has the same case as the rule.
        """
        for i, tgt_sent in enumerate(tgt_doc[::-1]):
            for j, tok in enumerate(tgt_sent):
                for c in tok.morph.get("Case"):
                    if c == self.case:
                        return tok, j, i+1
        return None, -1, -1

    def get_alignment(self, alignments, tgt_idx, english_sent):
        """
        This function finds the English token that aligns to the target token in the correct case/
        Returns the token and its index.
        """
        for src_index, tgt_index in alignments["mwmf"]:
            if tgt_index == tgt_idx:
                return src_index, english_sent[src_index]
        return -1, -1

    def check(self, english_doc, tgt_doc, alignments):
        """
        This function checks that the last sentence of the english and target documents
        follow all criteria of the specified rule with the context provided by the document
        """

        # make sure both sentences have no verb
        english_has_no_verb = self.has_no_verb(english_doc[-1])
        target_has_no_verb = self.has_no_verb(tgt_doc[-1])

        if not english_has_no_verb:
            return 1, None
        
        if not target_has_no_verb:
            logger.debug("English had no verb, but target does")
            return 2, None

        # ensures there is a token of the correct case in this sentence
        case_token, case_token_idx = self.has_correct_case(tgt_doc[-1])
        if case_token is None:
            logger.debug(f"No token with case of {self.case}")
            return 3, None

        # finds the most recent token in the target document with the same case
        preceding_token, preceding_token_idx, ante_distance = self.find_similar_preceding_token(tgt_doc[:-1])
        if preceding_token is None:
            logger.debug(f"Could not find a preceding token with the same case of {self.case}")
            return 4, None
        
        # finds the english token that aligns to the target form
        english_tok_idx, english_tok = self.get_alignment(alignments[-1], case_token_idx, english_doc[-1])
        if english_tok_idx == -1:
            logger.debug(f"Could not find a valid English alignment for target noun")
            return 5, None
            
        ante_index = len(tgt_doc) - 1 - ante_distance

        out = {
                "src noun": str(english_tok),
                "expected": str(case_token),
                "ante distance": ante_distance,
                "ref noun case": ",".join(case_token.morph.get("Case")),
                "ref segment": str(tgt_doc[-1]),
                "ref ante segment": str(tgt_doc[ante_index]),
                "src segment": str(english_doc[-1]),
                "src ante segment": str(english_doc[ante_index]),
                "src ante noun case": ",".join(english_tok.morph.get("Case"))
        }
        return 0, out

############################################################################################################

############################################### PRONOUNS ###################################################

############################################################################################################

class Pronoun():
    def __init__(self, name, rule, coref):
        """
            Rule class that handles the "Gender", "Formality", and "Animacy" class as described in paper.
            This is exemplified by the following context:
            
            "Do you know where the phone is?"
            "It is in the kitchen."
        """
        self.name = name

        # we only take pronouns of a specified case
        self.english_case = rule["english_case"]
        self.aligned_case = rule["aligned_case"]
        
        # and specified form
        self.english_form = rule["english_form"]
        self.aligned_form = rule["aligned_form"]
        self.expected = rule.get("expected", self.aligned_form)

        # the coreference part of speech
        self.english_coref_pos = rule["english_coref_pos"]
        
        # the gender, number and part of speech of the non-English antecedent
        self.aligned_coref_gender = rule["aligned_coref_gender"]
        self.aligned_coref_number = rule["aligned_coref_number"]
        self.aligned_coref_pos = rule["aligned_coref_pos"]

        # the coref model
        self.coref = coref

        # formality does not require coreference resolution
        if rule["requires_coref"] == "true":
            self.requires_coref = True
        else:
            self.requires_coref = False

    def valid_alignments(self, alignments, english, tgt):
        """
        This function finds all pronoun options based off the form and part of speech (specified by rule)
        Returns the pairs of [aligned] pronouns
        """
        out = []
        for src_index, tgt_index in alignments["mwmf"]:
            if str(english[src_index]).lower() == self.english_form and str(tgt[tgt_index]).lower() == self.aligned_form:
                if english[src_index].pos_ in ["PRON", "NOUN"] and tgt[tgt_index].pos_ in ["PRON", "NOUN"]:
                    out.append((src_index, tgt_index))
        return out

    def matches_case(self, token, english=True):
        """
        This function verifies the pronoun pair is in the correct case
        Casing requirements are very dependent on Spacy language model's capabilities.
        TODO: add regex style support for case
        """
        if english:
            match_case = self.english_case
        else:
            match_case = self.aligned_case

        # some rules require any match (ignore case)
        if match_case == '*':
            return True

        for case in token.morph.get("Case"):
            # if the case is negative, we want to make sure it doesn't match
            if '-' == match_case[0]:
                if case == match_case[1:]:
                    return False
            else:
                if case == match_case:
                    return True

        # this means spacy had no case information
        if '-' == match_case[0]:
            return True
        else:
            return False

    def find_coref(self, document, index):
        """
        This function finds the antecedent of a pronoun using coreference resolution
        Returns all the spans that are antecedents of the pronoun
        """
        preds = self.coref.predict([str(d) for sent in document for d in sent], is_split_into_words=True)
        for string_cluster, index_cluster in zip(preds.get_clusters(), preds.get_clusters(as_strings=False)):
            preceding = [] # going to only keep preceding spans (antecedents)
            for span in index_cluster:
                if span is not None:
                    preceding.append(span)
                    if index in span:
                        return preceding
        return None

    def get_head_of_span(self, span, span_idx):
        """
        This function returns the head of span based on majority vote. (Spacy annotates for head of phrase)
        Returns whether a successful head was chosen, and the index of the head
        """
        head = Counter()
        for tok in span:
            if tok.head.i >= span_idx[0] and tok.head.i < span_idx[1]:
                while tok.head.i >= span_idx[0] and tok.head.i < span_idx[1] and tok.head != tok:
                    tok = tok.head
            head.update([tok.i])
        if len(head) > 1:
            return False, None
        else:
            return True, head.most_common(1)[0][0]

    def get_antecedent(self, coref, document, lengths):
        """
        This function finds the antecedent of a pronoun using coreference resolution (English side only).
        Checks for the correct part of speech.
        Returns all valid antecedents.
        """
        valid_pos = []
        for span_idx in coref:
            offset = 0
            for l in lengths:
                if offset + l > span_idx[0]:
                    break
                offset += l
            # agreement is whether the children in span agree on the head
            agreement, head = self.get_head_of_span(document[span_idx[0]:span_idx[1]], (span_idx[0]-offset, span_idx[1]-offset))
            if agreement and document[offset+head].pos_ == self.english_coref_pos:
                valid_pos.append(span_idx)

        if len(valid_pos) == 0:
            return None
        
        return valid_pos[-1]

    def get_ante_index(self, document, antecedent):
        """
        This function finds the sentence distance between current sentence and the antecedent's sentence
        Returns the sentence distance and token index of the antecedent
        """
        offset = 0
        for i, sent in enumerate(document):
            for j, tok in enumerate(sent):
                if offset+j == antecedent:
                    return i, j
            offset += len(sent)

    def longest_consecutive(self, nums):
        """
        This function finds the longest consecutive span that is a ligned to a specific token
        """
        sorted_nums = sorted(nums)
        consecutive_sequences = [list(g) for k, g in groupby(sorted_nums, key=lambda n, c=count(): n-next(c))]

        longest_sequence = max(consecutive_sequences, key=len)
        return longest_sequence

    def get_aligned_span(self, alignments, ante_index, offseted_coref):
        """
        After identifying the coreference, we must find the aligned coreference span
        This function identifies the target span aligned to the English antecedent.
        Returns the span of the aligned coreference
        """
        span = []
        for src_index, tgt_index in alignments[ante_index]["mwmf"]:
            if src_index >= offseted_coref[0] and src_index < offseted_coref[1]:
                span.append(tgt_index)
        if len(span) == 0:
            return []
        consecutive = self.longest_consecutive(span)
        return (consecutive[0], consecutive[-1]+1)

    def check_aligned_coref_pos(self, head):
        """
        This function checks the aligned antecedent has the correct part of speech
        """
        if head.pos_ != self.aligned_coref_pos:
            return False
        return True

    def check_aligned_coref_gender(self, head):
        """
        This function checks the aligned antecedent has the correct gender
        """
        if self.aligned_coref_gender == "*":
            return True
        for gender in head.morph.get('Gender'):
            if gender == self.aligned_coref_gender:
                return True
        return False

    def check_aligned_coref_number(self, head):
        """
        This function checks the aligned antecedent has the correct number
        """
        for number in head.morph.get('Number'):
            if number == self.aligned_coref_number:
                return True
        return False

    def check(self, english_doc, tgt_doc, alignments):
        """
        This function checks that the last sentence of the english and target documents
        follow all criteria of the specified rule with the context provided by the document
        """

        rule_based_alignments = self.valid_alignments(alignments[-1], english_doc[-1], tgt_doc[-1])
        if len(rule_based_alignments) == 0:
            logger.debug("No rule based alignments found")
            return 1, None # we'll use the exit codes to debug what didn't pass the check

        # iterate over each possible pronoun pair
        retVal = -1
        for english_index, tgt_index in rule_based_alignments:
            logger.debug(f"Considering {english_doc[-1][english_index]} and {tgt_doc[-1][tgt_index]}")
            english_case = self.matches_case(english_doc[-1][english_index], english=True)
            tgt_case = self.matches_case(tgt_doc[-1][tgt_index], english=False)

            if not english_case:
                logger.debug(f"English token did not match case. (has {english_doc[-1][english_index].morph.get('Case')})")
                retVal = 2 # the return values here are buggy, because we want to check all pronouns which can each fail for different reasons
                continue

            if not tgt_case:
                logger.debug(f"Target token did not match case. (has {tgt_doc[-1][tgt_index].morph.get('Case')})")
                retVal = 10
                continue

            # formality is a quick/easy check because it doesn't require coreference resolution
            if not self.requires_coref:
                out = {
                    "src pronoun": self.english_form,
                    "ref pronoun": self.aligned_form,
                    "ref segment": str(tgt_doc[-1]),
                    "src segment": str(english_doc[-1]),
                }
                return 0, out

            # gender checks continue
            pronoun_index = english_index + sum(len(d) for d in english_doc)-len(english_doc[-1])
            coref = self.find_coref(english_doc, pronoun_index)
            if coref is None:
                logger.debug("No coreference span found")
                retVal = 3
                continue
            antecedent = self.get_antecedent(coref[:-1], [d for sent in english_doc for d in sent], [len(d) for d in english_doc])

            if antecedent is None:
                logger.debug("No valid antecedent found")
                retVal = 4
                continue

            # find the target antecedent based on the resolved English coreference
            ante_index, offseted_coref = self.get_ante_index(english_doc, antecedent[0])
            offset_span = (offseted_coref, offseted_coref+(antecedent[1]-antecedent[0]))
            aligned_ante_span = self.get_aligned_span(alignments, ante_index, offset_span)

            if len(aligned_ante_span) == 0:
                logger.debug("No aligned antecedent span found")
                retVal = 6
                continue

            # get head of span of the target
            agreement, aligned_head_of_span_idx = self.get_head_of_span(tgt_doc[ante_index][aligned_ante_span[0]:aligned_ante_span[1]], aligned_ante_span)
            if not agreement:
                logger.debug("Couldn't identify the head of the target antecedent span")
                retVal = 6
                continue

            # now we ensure the aligned head passes gender, part of speech, and number requirements
            aligned_head = tgt_doc[ante_index][aligned_head_of_span_idx]

            if not self.check_aligned_coref_pos(aligned_head):
                logger.debug(f"Incorrect POS. (has {aligned_head.pos_})")
                retVal = 7
                continue

            if not self.check_aligned_coref_gender(aligned_head):
                logger.debug(f"Incorrect gender. (has {aligned_head.morph.get('Gender')})")
                retVal = 8
                continue

            if not self.check_aligned_coref_number(aligned_head):
                logger.debug(f"Incorrect number. (has {aligned_head.morph.get('Number')})")
                retVal - 9
                continue

            if ante_index == len(english_doc) - 1:
                intrasegmental = True
            else:
                intrasegmental = False

            src_ante = english_doc[ante_index][offset_span[0]:offset_span[1]]
            agreement, src_ante_head_idx = self.get_head_of_span(src_ante, offset_span)

            if not agreement:
                retVal = 10
                continue

            src_ante_head = english_doc[ante_index][src_ante_head_idx]

            out = {
                "src pronoun": self.english_form,
                "expected": self.expected,
                "ante distance": len(english_doc)-ante_index-1,
                "intrasegmental": intrasegmental,
                "ref ante head": str(aligned_head),
                "ref ante head gender": self.aligned_coref_gender,
                "ref ante head lemma": str(aligned_head.lemma_),
                "ref ante head morpho": str(aligned_head.morph),
                "ref ante head pos": self.aligned_coref_pos,
                "ref ante head number": self.aligned_coref_number,
                "ref ante phrase": str(tgt_doc[ante_index][aligned_ante_span[0]:aligned_ante_span[1]]),
                "ref segment": str(tgt_doc[-1]),
                "ref ante segment": str(tgt_doc[ante_index]),
                "src ante head": str(src_ante_head),
                "src ante head gender": ",".join([str(g) for g in src_ante_head.morph.get('Gender')]),
                "src ante head lemma": str(src_ante_head.lemma_),
                "src ante head morpho": str(src_ante_head.morph),
                "src ante head pos": str(src_ante_head.pos_),
                "src ante head number": ",".join([str(n) for n in src_ante_head.morph.get('Number')]),
                "src ante phrase": str(src_ante),
                "src segment": str(english_doc[-1]),
                "src ante segment": str(english_doc[ante_index])
            }
            return 0, out

        return retVal, None