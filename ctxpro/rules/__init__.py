#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from . import de, es, fr, it, pl, pt, ru

RULES = {

    'DE_GENDER': de.DE_GENDER,
    'DE_FORMALITY': de.DE_FORMALITY,
    'DE_AUXILIARY': de.DE_AUXILIARY,

    'ES_GENDER': es.ES_GENDER,
    'ES_FORMALITY': es.ES_FORMALITY,
    'ES_AUXILIARY': es.ES_AUXILIARY,
    
    'FR_GENDER': fr.FR_GENDER,
    'FR_FORMALITY': fr.FR_FORMALITY,
    'FR_AUXILIARY': fr.FR_AUXILIARY,
    
    'IT_GENDER': it.IT_GENDER,
    'IT_FORMALITY': it.IT_FORMALITY,
    'IT_AUXILIARY': it.IT_AUXILIARY,
    
    'PL_GENDER': pl.PL_GENDER,
    'PL_FORMALITY': pl.PL_FORMALITY,
    'PL_AUXILIARY': pl.PL_AUXILIARY,
    'PL_INFLECTION': pl.PL_INFLECTION,
    
    'PT_GENDER': pt.PT_GENDER,
    'PT_FORMALITY': pt.PT_FORMALITY,
    'PT_AUXILIARY': pt.PT_AUXILIARY,
    
    'RU_GENDER': ru.RU_GENDER,
    'RU_FORMALITY': ru.RU_FORMALITY,
    'RU_AUXILIARY': ru.RU_AUXILIARY,
    'RU_INFLECTION': ru.RU_INFLECTION
}

def meets_criteria(name, language=None):
    if language is not None and language != name.lower()[:2]:
        return False
    return True

def list_rulesets(args):
    """
        Main entry point
    """
    print(f"Available rule sets by name:", file=sys.stderr)
    for name, ruleset in RULES.items():
        if meets_criteria(name, args.language):
            print(f"\t- {name}", file=sys.stderr)