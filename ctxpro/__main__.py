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

################################ MAIN ################################

import argparse



def parse_args():
    parser = argparse.ArgumentParser(
        description="CTXPRO: Toolkit for creating and evaluating evaluation sets targeting context-dependent phenomena in documents. Use for scoring translations, extracting contexts, or identifying context-dependent translations in parallel documents.\n"
        "   Example: ctxpro score -t translations.gender.en-de.test.txt -e gender/en-de/test -l de\n\n",
        usage="ctxpro [-h] [--version] [--verbosity] {all,debug,quiet} COMMAND ...\n\n",
        formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(help="sub-command help", dest="command")

    parser.add_argument("--version", '-v', default=False, action='store_true', help="Print version and exit.")


    # Arguments for the scoring functionality
    score_parser = subparsers.add_parser("score", help="Score translations against an evaluation set")
    score_parser.add_argument("--translations", "-t", type=str,
                                                default=None,
                                                help="Translation outputs, one per line. If None, will read from stdin.")
    score_parser.add_argument("--eval-set", "-e", required=True,
                                            type=str,
                                            help="Either name of evalualation set (from released), or path to a json file. Use `ctxpro list` to see available eval sets.")
    score_parser.add_argument("--lang", "-l", required=True,
                                            type=str,
                                            help="ISO (639-1) code for [target] language (used for sentence splitting).")
    score_parser.add_argument("--complete", '-c', default=False,
                                            action="store_true",
                                            help="Full output in tsv format.")
    score_parser.add_argument("--pretty", '-p', default=False,
                                            action="store_true",
                                            help="Adds some lines and formatting for easier human comprehension. Also implies --complete")
    # Set the verbosity level for logging
    score_parser.add_argument("--verbosity", '-V', default="all", choices=["all", "debug", "quiet"], help="Verbosity level.")



    # Arguments for the extraction functionality
    extract_parser = subparsers.add_parser("extract", help="Extract contexts for an evaluation set to use as input to a machine translation model.")
    extract_parser.add_argument("--input_files", '-i', default=None,
                                                type=str,
                                                nargs='*',
                                                help = "Input tsv files corresponding to the evaluation set. Expected columns are docid, src, tgt. If None, read from stdin.")
    extract_parser.add_argument("--eval-set", '-e', default=None,
                                                required=True,
                                                type=str,
                                                help = "The evaluation-set to extract contexts for---either from `ctxpro list` or path to .json produced via `ctxpro identify`.")
    extract_parser.add_argument("--max_sentences", '-s', default=10,
                                                type=int,
                                                help="The maximum number of sentences to include.")
    extract_parser.add_argument("--max_tokens", "-t", default=10000,
                                                type=int,
                                                help="The maximum number of tokens to include.")
    extract_parser.add_argument("--spm", "-S", default=None,
                                                type=str,
                                                help="Path to sentencepiece model. If not specified, uses whitespace tokenization.")
    extract_parser.add_argument("--joining_string", '-j', default=" ",
                                                type=str,
                                                help="The string to use to join sentences together. Defaults to a space.")
    extract_parser.add_argument("--output", "-o", default=None,
                                                type=str,
                                                help="The output directory to write contexts to. If not specified, writes to stdout.")
    extract_parser.add_argument("--target", "-T", default=False, 
                                                action="store_true",
                                                help="If true, extracts target preceding context instead.")
    # Set the verbosity level for logging
    extract_parser.add_argument("--verbosity", '-V', default="all", choices=["all", "debug", "quiet"], help="Verbosity level.")



    # Arguments for the identification functionality
    identify_parser = subparsers.add_parser("identify", help="Identify contexts from documents to produce an evaluation set for context-dependent phenomena.")
    identify_parser.add_argument("--input_files", '-i', default=None,
                                                type=str,
                                                nargs='*',
                                                help = "Input tsv files of documents. If not specified, reads from stdin. Expected columns are docid, src, tgt.")
    identify_parser.add_argument("--rules", "-r", required=True,
                                                type=str,
                                                nargs='+',
                                                help="Name of rule set to use. Predefined can be listed with `ctxpro list`. Otherwise, must be file path to a .json.")
    identify_parser.add_argument("--window-size", "-w", default=10,
                                                type=int,
                                                help="Window size for preceding context. Default 10 sentences.")
    identify_parser.add_argument("--target", '-t', required=True,
                                                type=str,
                                                help="Target language code (ISO 639-1). Required for SpaCy model selection. (Source is English)")
    identify_parser.add_argument("--output_dir", '-o', default="ctxpro-jsons",
                                                type=str,
                                                help="Output directory for identified examples in json format. Default 'ctxpro-jsons'.")
    identify_parser.add_argument("--cpu", '-c', default=False,
                                                action="store_true",
                                                help="Run on CPU (default: GPU)")
    # Set the verbosity level for logging
    identify_parser.add_argument("--verbosity", '-V', default="all", choices=["all", "debug", "quiet"], help="Verbosity level.")


    # Arguments for listing rule sets or available evaluation sets.
    list_parser = subparsers.add_parser("list", help="List available rulesets or evaluation sets.")
    list_subparser = list_parser.add_subparsers(help="list subcommand help", dest="list_command")

    rule_set = list_subparser.add_parser("rulesets", help="List available rulesets.")
    rule_set.add_argument("--language", '-l', type=str,
                                        default=None,
                                        choices=["en", "de", "es", "fr", "it", "pl", "pt", "ru"],
                                        help="The language of rulesets to list.")
    

    eval_set = list_subparser.add_parser("evalsets", help="List available evaluation sets.")
    eval_set.add_argument("--category", '-c', type=str,
                                        default=None, 
                                        choices=["animacy", "formality", "gender", "inflections"],
                                        help="The category of test sets to list.")
    eval_set.add_argument("--lang-pair", '-l', type=str,
                                        default=None,
                                        choices=["en-de", "en-es", "en-fr", "en-it", "en-pl", "en-pt", "en-ru", 
                                                    "de-en", "es-en", "fr-en", "it-en", "pl-en", "pt-en", "ru-en"],
                                        help="The language pair of test sets to list.")
    eval_set.add_argument("--split", '-s', type=str,
                                        default=None,
                                        choices=["dev", "devtest", "test"],
                                        help="The split of test sets to list.")
    args = parser.parse_args()

    return args

def main():
    args = parse_args()

    if args.version:
        from . import __version__
        print("CTXPRO version {}".format(__version__))
        exit(0)

    if args.verbosity == "debug":
        logger.setLevel(logging.DEBUG)
    elif args.verbosity == "quiet":
        logger.setLevel(logging.ERROR)

    if args.command == "score":
        from . import score
        exit_value = score.main(args)
        sys.exit(exit_value)

    elif args.command == "extract":
        from . import extract
        exit_value = extract.main(args)
        sys.exit(exit_value)
        

    elif args.command == "identify":
        try:
            from . import identify
        except ImportError:
            FAIL_MESSAGE = """
            You seemed to have tried to use the `identify` command, but you don't have the associated packages installed.
            Please install ctxpro with:

                pip install ctxpro[identify]
            """

            raise ValueError(FAIL_MESSAGE)
        exit_value = identify.main(args)
        sys.exit(exit_value)

    elif args.command == "list":
        if args.list_command == "rulesets":
            from .rules import list_rulesets
            list_rulesets(args)
        elif args.list_command == "evalsets":
            from . import evalsets
            evalsets.main(args)
        else:
            raise ValueError("Unknown list command: {}".format(args.list_command))


    else:
        raise ValueError("Unknown command: {}".format(args.command))

if __name__ == "__main__":
    main()

