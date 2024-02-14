# -*- coding: utf-8 -*-

import gzip
import os
import ssl
import sys
import urllib.request
import hashlib
import shutil
import logging
import progressbar
import json

# TODO: change the loglevel here if -q is passed
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=os.environ.get("LOGLEVEL", "INFO").upper(),
    stream=sys.stderr,
)
logger = logging.getLogger("ctxpro")

USERHOME = os.path.expanduser("~")
CTXPRO_DIR = os.environ.get("CTXPRO", os.path.join(USERHOME, ".ctxpro"))

TESTSETS = {

    ########################################## GENDER #############################################

    "en-de/gender/test": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/gender.opensubtitles.en-de.test.json",
        "info": "A test set for English-German translation of gendered pronouns.",
        "destination": "gender.opensubtitles.en-de.test.json",
        "date": "01 Nov 2023",
        "md5": "a0c11e89f47fded82b0e7e94e91302c9"
    },
    "en-de/gender/devtest":{
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/gender.opensubtitles.en-de.devtest.json",
        "info": "A devtest set for English-German translation of gendered pronouns.",
        "destination": "gender.opensubtitles.en-de.devtest.json",
        "date": "01 Nov 2023",
        "md5": "2036f9413beeb5b7f0219b1b20b7c5ab"
    },
    "en-de/gender/dev": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/gender.opensubtitles.en-de.dev.json",
        "info": "A dev set for English-German translation of gendered pronouns.",
        "destination": "gender.opensubtitles.en-de.dev.json",
        "date": "01 Nov 2023",
        "md5": "4ce12c78658b0648887b7b5898ce1d70"
    },

    "en-es/gender/test": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/gender.opensubtitles.en-es.test.json",
        "info": "A test set for English-Spanish translation of gendered pronouns.",
        "destination": "gender.opensubtitles.en-es.test.json",
        "date": "01 Nov 2023",
        "md5": "85386ab06c8171d02ccf34f61b426973"
    },
    "en-es/gender/devtest":{
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/gender.opensubtitles.en-es.devtest.json",
        "info": "A devtest set for English-Spanish translation of gendered pronouns.",
        "destination": "gender.opensubtitles.en-es.devtest.json",
        "date": "01 Nov 2023",
        "md5": "05883c02d468bdadd35c56772dbf5bf4"
    },
    "en-es/gender/dev": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/gender.opensubtitles.en-es.dev.json",
        "info": "A dev set for English-Spanish translation of gendered pronouns.",
        "destination": "gender.opensubtitles.en-es.dev.json",
        "date": "01 Nov 2023",
        "md5": "945437eb4149469bdd6ad77e9088e221"
    },

    "en-fr/gender/test": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/gender.opensubtitles.en-fr.test.json",
        "info": "A test set for English-French translation of gendered pronouns.",
        "destination": "gender.opensubtitles.en-fr.test.json",
        "date": "01 Nov 2023",
        "md5": "ebdacc240ec99cb363875c3b4672c20e"
    },
    "en-fr/gender/devtest":{
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/gender.opensubtitles.en-fr.devtest.json",
        "info": "A devtest set for English-French translation of gendered pronouns.",
        "destination": "gender.opensubtitles.en-fr.devtest.json",
        "date": "01 Nov 2023",
        "md5": "bed5c36dea55637231bfd05897ed8048"
    },
    "en-fr/gender/dev": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/gender.opensubtitles.en-fr.dev.json",
        "info": "A dev set for English-French translation of gendered pronouns.",
        "destination": "gender.opensubtitles.en-fr.dev.json",
        "date": "01 Nov 2023",
        "md5": "92574da8258b89a48e16d876d614999a"
    },

    "en-it/gender/test": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/gender.opensubtitles.en-it.test.json",
        "info": "A test set for English-Italian translation of gendered pronouns.",
        "destination": "gender.opensubtitles.en-it.test.json",
        "date": "01 Nov 2023",
        "md5": "eb4efe3dac996191a8d4e52af2bf6faf"
    },
    "en-it/gender/devtest":{
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/gender.opensubtitles.en-it.devtest.json",
        "info": "A devtest set for English-Italian translation of gendered pronouns.",
        "destination": "gender.opensubtitles.en-it.devtest.json",
        "date": "01 Nov 2023",
        "md5": "620ff513513010720cf9a509807c9c43"
    },
    "en-it/gender/dev": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/gender.opensubtitles.en-it.dev.json",
        "info": "A dev set for English-Italian translation of gendered pronouns.",
        "destination": "gender.opensubtitles.en-it.dev.json",
        "date": "01 Nov 2023",
        "md5": "1c7aead60b308034e757dd77479f6060"
    },

    "en-pl/gender/test": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/gender.opensubtitles.en-pl.test.json",
        "info": "A test set for English-Polish translation of gendered pronouns.",
        "destination": "gender.opensubtitles.en-pl.test.json",
        "date": "01 Nov 2023",
        "md5": "358704c4ef426a743d5a355e4f6eea18"
    },
    "en-pl/gender/devtest":{
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/gender.opensubtitles.en-pl.devtest.json",
        "info": "A devtest set for English-Polish translation of gendered pronouns.",
        "destination": "gender.opensubtitles.en-pl.devtest.json",
        "date": "01 Nov 2023",
        "md5": "a5e22b4cd7d6458032c629820d4f1ba7"
    },
    "en-pl/gender/dev": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/gender.opensubtitles.en-pl.dev.json",
        "info": "A dev set for English-Polish translation of gendered pronouns.",
        "destination": "gender.opensubtitles.en-pl.dev.json",
        "date": "01 Nov 2023",
        "md5": "a0207e444ae069b9a5d795fb249768ff"
    },

    "en-pt/gender/test": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/gender.opensubtitles.en-pt.test.json",
        "info": "A test set for English-Portuguese translation of gendered pronouns.",
        "destination": "gender.opensubtitles.en-pt.test.json",
        "date": "01 Nov 2023",
        "md5": "bc1deae5d05a85b31610b62e3aa95d34"
    },
    "en-pt/gender/devtest":{
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/gender.opensubtitles.en-pt.devtest.json",
        "info": "A devtest set for English-Portuguese translation of gendered pronouns.",
        "destination": "gender.opensubtitles.en-pt.devtest.json",
        "date": "01 Nov 2023",
        "md5": "1b04838d2c11655a9dfa81e291a19f83"
    },
    "en-pt/gender/dev": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/gender.opensubtitles.en-pt.dev.json",
        "info": "A dev set for English-Portuguese translation of gendered pronouns.",
        "destination": "gender.opensubtitles.en-pt.dev.json",
        "date": "01 Nov 2023",
        "md5": "c07900319c84e430af119e213775b2ba"
    },

    "en-ru/gender/test": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/gender.opensubtitles.en-ru.test.json",
        "info": "A test set for English-Russian translation of gendered pronouns.",
        "destination": "gender.opensubtitles.en-ru.test.json",
        "date": "01 Nov 2023",
        "md5": "58b4c76ee716b4c183291a9a8bf107a9"
    },
    "en-ru/gender/devtest":{
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/gender.opensubtitles.en-ru.devtest.json",
        "info": "A devtest set for English-Russian translation of gendered pronouns.",
        "destination": "gender.opensubtitles.en-ru.devtest.json",
        "date": "01 Nov 2023",
        "md5": "3bdc1fc8b0b622f30f649b0095d1c3a3"
    },
    "en-ru/gender/dev": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/gender.opensubtitles.en-ru.dev.json",
        "info": "A dev set for English-Russian translation of gendered pronouns.",
        "destination": "gender.opensubtitles.en-ru.dev.json",
        "date": "01 Nov 2023",
        "md5": "1a0d16dd408e507dafc4599035d954c0"
    },

    ########################################## AUXILIARY #############################################
    
    "en-de/auxiliary/test": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/auxiliary.opensubtitles.en-de.test.json",
        "info": "A test set for English-German translation of auxiliary verbs.",
        "destination": "auxiliary.opensubtitles.en-de.test.json",
        "date": "01 Nov 2023",
        "md5": "bc9dcdd998a98114db574b12d2460109"
    },
    "en-de/auxiliary/devtest":{
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/auxiliary.opensubtitles.en-de.devtest.json",
        "info": "A devtest set for English-German translation of auxiliary verbs.",
        "destination": "auxiliary.opensubtitles.en-de.devtest.json",
        "date": "01 Nov 2023",
        "md5": "0a4fe384cba2427d1ccda584b0f1c05d"
    },
    "en-de/auxiliary/dev": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/auxiliary.opensubtitles.en-de.dev.json",
        "info": "A dev set for English-German translation of auxiliary verbs.",
        "destination": "auxiliary.opensubtitles.en-de.dev.json",
        "date": "01 Nov 2023",
        "md5": "2c27b954eff6151f476aedc2ac6b0c82"
    },

    "en-es/auxiliary/test": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/auxiliary.opensubtitles.en-es.test.json",
        "info": "A test set for English-Spanish translation of auxiliary verbs.",
        "destination": "formality.opensubtitles.en-es.test.json",
        "date": "01 Nov 2023",
        "md5": "ad5bd102b394064f5e5fc6e4ed4301e4"
    },
    "en-es/auxiliary/devtest":{
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/auxiliary.opensubtitles.en-es.devtest.json",
        "info": "A devtest set for English-Spanish translation of auxiliary verbs.",
        "destination": "auxiliary.opensubtitles.en-es.devtest.json",
        "date": "01 Nov 2023",
        "md5": "49512d70a9f5bbbbae438ed70deafed7"
    },
    "en-es/auxiliary/dev": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/auxiliary.opensubtitles.en-es.dev.json",
        "info": "A dev set for English-Spanish translation of auxiliary verbs.",
        "destination": "auxiliary.opensubtitles.en-es.dev.json",
        "date": "01 Nov 2023",
        "md5": "8d9255f567d128a59e25b9bda8fb8611"
    },

    "en-fr/auxiliary/test": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/auxiliary.opensubtitles.en-fr.test.json",
        "info": "A test set for English-French translation of auxiliary verbs.",
        "destination": "auxiliary.opensubtitles.en-fr.test.json",
        "date": "01 Nov 2023",
        "md5": "0d275e0521660a2c5d137f30d9066dc9"
    },
    "en-fr/auxiliary/devtest":{
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/auxiliary.opensubtitles.en-fr.devtest.json",
        "info": "A devtest set for English-French translation of auxiliary verbs.",
        "destination": "auxiliary.opensubtitles.en-fr.devtest.json",
        "date": "01 Nov 2023",
        "md5": "c2381d8bdb97a2a937dbf041deb3d8cc"
    },
    "en-fr/auxiliary/dev": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/auxiliary.opensubtitles.en-fr.dev.json",
        "info": "A dev set for English-French translation of auxiliary verbs.",
        "destination": "auxiliary.opensubtitles.en-fr.dev.json",
        "date": "01 Nov 2023",
        "md5": "506fad959e093f71d323a92409355ee2"
    },

    "en-it/auxiliary/test": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/auxiliary.opensubtitles.en-it.test.json",
        "info": "A test set for English-Italian translation of auxiliary verbs.",
        "destination": "auxiliary.opensubtitles.en-it.test.json",
        "date": "01 Nov 2023",
        "md5": "8955d3123c36de419b194f7bcc1a66bf"
    },
    "en-it/auxiliary/devtest":{
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/auxiliary.opensubtitles.en-it.devtest.json",
        "info": "A devtest set for English-Italian translation of auxiliary verbs.",
        "destination": "auxiliary.opensubtitles.en-it.devtest.json",
        "date": "01 Nov 2023",
        "md5": "bcf818d8a09530e1cbd9ac649912c9dd"
    },
    "en-it/auxiliary/dev": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/auxiliary.opensubtitles.en-it.dev.json",
        "info": "A dev set for English-Italian translation of auxiliary verbs.",
        "destination": "auxiliary.opensubtitles.en-it.dev.json",
        "date": "01 Nov 2023",
        "md5": "2ba24d18493318c7c1b3693eeacd6845"
    },

    "en-pl/auxiliary/test": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/auxiliary.opensubtitles.en-pl.test.json",
        "info": "A test set for English-Polish translation of auxiliary verbs.",
        "destination": "auxiliary.opensubtitles.en-pl.test.json",
        "date": "01 Nov 2023",
        "md5": "245b377a55fc3e3a1a67280760e40bc7"
    },
    "en-pl/auxiliary/devtest":{
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/auxiliary.opensubtitles.en-pl.devtest.json",
        "info": "A devtest set for English-Polish translation of auxiliary verbs.",
        "destination": "auxiliary.opensubtitles.en-pl.devtest.json",
        "date": "01 Nov 2023",
        "md5": "2942379892b11e7966396b441a02efb8"
    },
    "en-pl/auxiliary/dev": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/auxiliary.opensubtitles.en-pl.dev.json",
        "info": "A dev set for English-Polish translation of auxiliary verbs.",
        "destination": "auxiliary.opensubtitles.en-pl.dev.json",
        "date": "01 Nov 2023",
        "md5": "97a6843365c6a2fb061aa5ead708975c"
    },

    "en-pt/auxiliary/test": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/auxiliary.opensubtitles.en-pt.test.json",
        "info": "A test set for English-Portuguese translation of auxiliary verbs.",
        "destination": "auxiliary.opensubtitles.en-pt.test.json",
        "date": "01 Nov 2023",
        "md5": "e341dc1937ee8f1c4b678ad965ff4177"
    },
    "en-pt/auxiliary/devtest":{
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/auxiliary.opensubtitles.en-pt.devtest.json",
        "info": "A devtest set for English-Portuguese translation of auxiliary verbs.",
        "destination": "auxiliary.opensubtitles.en-pt.devtest.json",
        "date": "01 Nov 2023",
        "md5": "c77a34d4060658007dbd78a73abb7101"
    },
    "en-pt/auxiliary/dev": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/auxiliary.opensubtitles.en-pt.dev.json",
        "info": "A dev set for English-Portuguese translation of auxiliary verbs.",
        "destination": "auxiliary.opensubtitles.en-pt.dev.json",
        "date": "01 Nov 2023",
        "md5": "02e061cd5ff76f6df16ea4e66f18c30c"
    },

    "en-ru/auxiliary/test": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/auxiliary.opensubtitles.en-ru.test.json",
        "info": "A test set for English-Russian translation of auxiliary verbs.",
        "destination": "auxiliary.opensubtitles.en-ru.test.json",
        "date": "01 Nov 2023",
        "md5": "114923fccca4a33ea4079f7239f7923c"
    },
    "en-ru/auxiliary/devtest":{
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/auxiliary.opensubtitles.en-ru.devtest.json",
        "info": "A devtest set for English-Russian translation of auxiliary verbs.",
        "destination": "auxiliary.opensubtitles.en-ru.devtest.json",
        "date": "01 Nov 2023",
        "md5": "f9a4e2fde62d2e1a76967509a1db0127"
    },
    "en-ru/auxiliary/dev": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/auxiliary.opensubtitles.en-ru.dev.json",
        "info": "A dev set for English-Russian translation of auxiliary verbs.",
        "destination": "auxiliary.opensubtitles.en-ru.dev.json",
        "date": "01 Nov 2023",
        "md5": "40da0af07782cdd05f123646917a911c"
    },

    ########################################## FORMALITY #############################################

    "en-de/formality/test": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/formality.opensubtitles.en-de.test.json",
        "info": "A test set for English-German translation of formality pronouns.",
        "destination": "formality.opensubtitles.en-de.test.json",
        "date": "01 Nov 2023",
        "md5": "3b174e499c71b136206f8c2e6d805b9a"
    },
    "en-de/formality/devtest":{
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/formality.opensubtitles.en-de.devtest.json",
        "info": "A devtest set for English-German translation of formality pronouns.",
        "destination": "formality.opensubtitles.en-de.devtest.json",
        "date": "01 Nov 2023",
        "md5": "8490ea2bdc58452efc716b307d134175"
    },
    "en-de/formality/dev": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/formality.opensubtitles.en-de.dev.json",
        "info": "A dev set for English-German translation of formality pronouns.",
        "destination": "formality.opensubtitles.en-de.dev.json",
        "date": "01 Nov 2023",
        "md5": "b2d2c6f25a181aac744c6918c900320f"
    },

    "en-es/formality/test": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/formality.opensubtitles.en-es.test.json",
        "info": "A test set for English-Spanish translation of formality pronouns.",
        "destination": "formality.opensubtitles.en-es.test.json",
        "date": "01 Nov 2023",
        "md5": "d06ddc32aa9bb2ea4132982d53992f07"
    },
    "en-es/formality/devtest":{
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/formality.opensubtitles.en-es.devtest.json",
        "info": "A devtest set for English-Spanish translation of formality pronouns.",
        "destination": "formality.opensubtitles.en-es.devtest.json",
        "date": "01 Nov 2023",
        "md5": "9c6c84db9ffc243858cde156fcf56a31"
    },
    "en-es/formality/dev": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/formality.opensubtitles.en-es.dev.json",
        "info": "A dev set for English-Spanish translation of formality pronouns.",
        "destination": "formality.opensubtitles.en-es.dev.json",
        "date": "01 Nov 2023",
        "md5": "a6d6823c6036d7042e535ce7bcc29f7e"
    },

    "en-fr/formality/test": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/formality.opensubtitles.en-fr.test.json",
        "info": "A test set for English-French translation of formality pronouns.",
        "destination": "formality.opensubtitles.en-fr.test.json",
        "date": "01 Nov 2023",
        "md5": "29b13bb72a9a6f41bf4ce356100d6972"
    },
    "en-fr/formality/devtest":{
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/formality.opensubtitles.en-fr.devtest.json",
        "info": "A devtest set for English-French translation of formality pronouns.",
        "destination": "formality.opensubtitles.en-fr.devtest.json",
        "date": "01 Nov 2023",
        "md5": "02c003fdb1b8fb48a22656912ca82b87"
    },
    "en-fr/formality/dev": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/formality.opensubtitles.en-fr.dev.json",
        "info": "A dev set for English-French translation of formality pronouns.",
        "destination": "formality.opensubtitles.en-fr.dev.json",
        "date": "01 Nov 2023",
        "md5": "9ec9c7368467c3daa54ce539c71c2d34"
    },

    "en-it/formality/test": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/formality.opensubtitles.en-it.test.json",
        "info": "A test set for English-Italian translation of formality pronouns.",
        "destination": "formality.opensubtitles.en-it.test.json",
        "date": "01 Nov 2023",
        "md5": "fed0f847f98d5655283723169199af25"
    },
    "en-it/formality/devtest":{
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/formality.opensubtitles.en-it.devtest.json",
        "info": "A devtest set for English-Italian translation of formality pronouns.",
        "destination": "formality.opensubtitles.en-it.devtest.json",
        "date": "01 Nov 2023",
        "md5": "72f7cdfe72f561f47910341f9d5a80c8"
    },
    "en-it/formality/dev": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/formality.opensubtitles.en-it.dev.json",
        "info": "A dev set for English-Italian translation of formality pronouns.",
        "destination": "formality.opensubtitles.en-it.dev.json",
        "date": "01 Nov 2023",
        "md5": "1ef9c3a8269cb2a1c333c01268134465"
    },

    "en-pl/formality/test": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/formality.opensubtitles.en-pl.test.json",
        "info": "A test set for English-Polish translation of formality pronouns.",
        "destination": "formality.opensubtitles.en-pl.test.json",
        "date": "01 Nov 2023",
        "md5": "263dfc5d60378058b48345cc686fd1ef"
    },
    "en-pl/formality/devtest":{
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/formality.opensubtitles.en-pl.devtest.json",
        "info": "A devtest set for English-Polish translation of formality pronouns.",
        "destination": "formality.opensubtitles.en-pl.devtest.json",
        "date": "01 Nov 2023",
        "md5": "a4a969ec1722c090c5f522b426df5b6d"
    },
    "en-pl/formality/dev": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/formality.opensubtitles.en-pl.dev.json",
        "info": "A dev set for English-Polish translation of formality pronouns.",
        "destination": "formality.opensubtitles.en-pl.dev.json",
        "date": "01 Nov 2023",
        "md5": "15df59cf3301a07ee3f7bc98b71974a0"
    },

    "en-pt/formality/test": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/formality.opensubtitles.en-pt.test.json",
        "info": "A test set for English-Portuguese translation of formality pronouns.",
        "destination": "formality.opensubtitles.en-pt.test.json",
        "date": "01 Nov 2023",
        "md5": "12d4ae19a9bee04cbc9678bb63f502b4"
    },
    "en-pt/formality/devtest":{
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/formality.opensubtitles.en-pt.devtest.json",
        "info": "A devtest set for English-Portuguese translation of formality pronouns.",
        "destination": "formality.opensubtitles.en-pt.devtest.json",
        "date": "01 Nov 2023",
        "md5": "d569d9df8726d1d1649784a2c72fb27e"
    },
    "en-pt/formality/dev": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/formality.opensubtitles.en-pt.dev.json",
        "info": "A dev set for English-Portuguese translation of formality pronouns.",
        "destination": "formality.opensubtitles.en-pt.dev.json",
        "date": "01 Nov 2023",
        "md5": "6c28579c9a97b80c47f550f30481d73d"
    },

    "en-ru/formality/test": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/formality.opensubtitles.en-ru.test.json",
        "info": "A test set for English-Russian translation of formality pronouns.",
        "destination": "formality.opensubtitles.en-ru.test.json",
        "date": "01 Nov 2023",
        "md5": "55c68f38517e272f9ce0edc2b680a622"
    },
    "en-ru/formality/devtest":{
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/formality.opensubtitles.en-ru.devtest.json",
        "info": "A devtest set for English-Russian translation of formality pronouns.",
        "destination": "formality.opensubtitles.en-ru.devtest.json",
        "date": "01 Nov 2023",
        "md5": "6e84cdb7dc3e6bfeb65eb61056fd6d0d"
    },
    "en-ru/formality/dev": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/formality.opensubtitles.en-ru.dev.json",
        "info": "A dev set for English-Russian translation of formality pronouns.",
        "destination": "formality.opensubtitles.en-ru.dev.json",
        "date": "01 Nov 2023",
        "md5": "7c99fc48192a60d8009cc6bdf393716d"
    },

    ########################################## ANIMACY #############################################

    "de-en/animacy/test": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/animacy.opensubtitles.de-en.test.json",
        "info": "A test set for German-English translation of animacy pronouns.",
        "destination": "animacy.opensubtitles.de-en.test.json",
        "date": "01 Nov 2023",
        "md5": "fafe3431b55c96c072951e87b4534fad"
    },
    "de-en/animacy/devtest":{
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/animacy.opensubtitles.de-en.devtest.json",
        "info": "A devtest set for German-English translation of animacy pronouns.",
        "destination": "animacy.opensubtitles.de-en.devtest.json",
        "date": "01 Nov 2023",
        "md5": "d319e6d5508bde87f97a866c2f55ccfd"
    },
    "de-en/animacy/dev": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/animacy.opensubtitles.de-en.dev.json",
        "info": "A dev set for German-English translation of animacy pronouns.",
        "destination": "animacy.opensubtitles.de-en.dev.json",
        "date": "01 Nov 2023",
        "md5": "da4d9d0882ab1f11fd282ca92a79b77a"
    },

    "es-en/animacy/test": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/animacy.opensubtitles.es-en.test.json",
        "info": "A test set for Spanish-English translation of animacy pronouns.",
        "destination": "animacy.opensubtitles.es-en.test.json",
        "date": "01 Nov 2023",
        "md5": "83140e008812b25f014f2f06236199aa"
    },
    "es-en/animacy/devtest":{
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/animacy.opensubtitles.es-en.devtest.json",
        "info": "A devtest set for Spanish-English translation of animacy pronouns.",
        "destination": "animacy.opensubtitles.es-en.devtest.json",
        "date": "01 Nov 2023",
        "md5": "a3ff3af92454a882755ab07319ac694c"
    },
    "es-en/animacy/dev": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/animacy.opensubtitles.es-en.dev.json",
        "info": "A dev set for Spanish-English translation of animacy pronouns.",
        "destination": "animacy.opensubtitles.es-en.dev.json",
        "date": "01 Nov 2023",
        "md5": "b2c5365ee25d241e497b027f34e3e658"
    },

    "fr-en/animacy/test": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/animacy.opensubtitles.fr-en.test.json",
        "info": "A test set for French-English translation of animacy pronouns.",
        "destination": "animacy.opensubtitles.fr-en.test.json",
        "date": "01 Nov 2023",
        "md5": "995fa03388dff2a644505bbf6e48713f"
    },
    "fr-en/animacy/devtest":{
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/animacy.opensubtitles.fr-en.devtest.json",
        "info": "A devtest set for French-English translation of animacy pronouns.",
        "destination": "animacy.opensubtitles.fr-en.devtest.json",
        "date": "01 Nov 2023",
        "md5": "577473907aa7f85a8fd2c8b8208d14e6"
    },
    "fr-en/animacy/dev": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/animacy.opensubtitles.fr-en.dev.json",
        "info": "A dev set for French-English translation of animacy pronouns.",
        "destination": "animacy.opensubtitles.fr-en.dev.json",
        "date": "01 Nov 2023",
        "md5": "b820707765415a095fb12f0312b2719a"
    },

    "it-en/animacy/test": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/animacy.opensubtitles.it-en.test.json",
        "info": "A test set for Italian-English translation of animacy pronouns.",
        "destination": "animacy.opensubtitles.it-en.test.json",
        "date": "01 Nov 2023",
        "md5": "a1702e81a1e9281367b97f996ae628b2"
    },
    "it-en/animacy/devtest":{
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/animacy.opensubtitles.it-en.devtest.json",
        "info": "A devtest set for Italian-English translation of animacy pronouns.",
        "destination": "animacy.opensubtitles.it-en.devtest.json",
        "date": "01 Nov 2023",
        "md5": "fb5308af1237870f38fe336f41762252"
    },
    "it-en/animacy/dev": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/animacy.opensubtitles.it-en.dev.json",
        "info": "A dev set for Italian-English translation of animacy pronouns.",
        "destination": "animacy.opensubtitles.it-en.dev.json",
        "date": "01 Nov 2023",
        "md5": "0d2a6550d9ce880a4e99bf8a645b9f87"
    },

    "pl-en/animacy/test": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/animacy.opensubtitles.pl-en.test.json",
        "info": "A test set for Polish-English translation of animacy pronouns.",
        "destination": "animacy.opensubtitles.pl-en.test.json",
        "date": "01 Nov 2023",
        "md5": "878e04b205b15281165f6a636b3a4b0c"
    },
    "pl-en/animacy/devtest":{
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/animacy.opensubtitles.pl-en.devtest.json",
        "info": "A devtest set for Polish-English translation of animacy pronouns.",
        "destination": "animacy.opensubtitles.pl-en.devtest.json",
        "date": "01 Nov 2023",
        "md5": "17f1d3b18296782f1a91a015951033a4"
    },
    "pl-en/animacy/dev": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/animacy.opensubtitles.pl-en.dev.json",
        "info": "A dev set for Polish-English translation of animacy pronouns.",
        "destination": "animacy.opensubtitles.pl-en.dev.json",
        "date": "01 Nov 2023",
        "md5": "5f30c4e1994016c1c4dceaa636987405"
    },

    "pt-en/animacy/test": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/animacy.opensubtitles.pt-en.test.json",
        "info": "A test set for Portuguese-English translation of animacy pronouns.",
        "destination": "animacy.opensubtitles.pt-en.test.json",
        "date": "01 Nov 2023",
        "md5": "4af7b2497a77b83985a887594fd3ade5"
    },
    "pt-en/animacy/devtest":{
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/animacy.opensubtitles.pt-en.devtest.json",
        "info": "A devtest set for Portuguese-English translation of animacy pronouns.",
        "destination": "animacy.opensubtitles.pt-en.devtest.json",
        "date": "01 Nov 2023",
        "md5": "4a825b2fcf89ac34bacbb64d2d0930b6"
    },
    "pt-en/animacy/dev": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/animacy.opensubtitles.pt-en.dev.json",
        "info": "A dev set for Portuguese-English translation of animacy pronouns.",
        "destination": "animacy.opensubtitles.pt-en.dev.json",
        "date": "01 Nov 2023",
        "md5": "df3a9825dff8bee1aac0bb09e6c546e8"
    },

    "ru-en/animacy/test": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/animacy.opensubtitles.ru-en.test.json",
        "info": "A test set for Russian-English translation of animacy pronouns.",
        "destination": "animacy.opensubtitles.ru-en.test.json",
        "date": "01 Nov 2023",
        "md5": "e2eeb12639dcb6d82d6f8a41af03abdb"
    },
    "ru-en/animacy/devtest":{
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/animacy.opensubtitles.ru-en.devtest.json",
        "info": "A devtest set for Russian-English translation of animacy pronouns.",
        "destination": "animacy.opensubtitles.ru-en.devtest.json",
        "date": "01 Nov 2023",
        "md5": "3fe9a932e0bb633c81cb9eb42488c25c"
    },
    "ru-en/animacy/dev": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/animacy.opensubtitles.ru-en.dev.json",
        "info": "A dev set for Russian-English translation of animacy pronouns.",
        "destination": "animacy.opensubtitles.ru-en.dev.json",
        "date": "01 Nov 2023",
        "md5": "cdc94eb2c607d0974cd99ec1b88e4a5f"
    },

    ########################################## INFLECTION #############################################

    "en-ru/inflection/test": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/inflection.opensubtitles.en-ru.test.json",
        "info": "A test set for English-Russian translation of inflections.",
        "destination": "inflection.opensubtitles.en-ru.test.json",
        "date": "01 Nov 2023",
        "md5": "c12f2fec8c359204d2d08ad7262ba997"
    },
    "en-ru/inflection/devtest":{
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/inflection.opensubtitles.en-ru.devtest.json",
        "info": "A devtest set for English-Russian translation of inflections.",
        "destination": "inflection.opensubtitles.en-ru.devtest.json",
        "date": "01 Nov 2023",
        "md5": "2b8c89719f7555a973e7c36d01f75a86"
    },
    "en-ru/inflection/dev": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/inflection.opensubtitles.en-ru.dev.json",
        "info": "A dev set for English-Russian translation of inflections.",
        "destination": "inflection.opensubtitles.en-ru.dev.json",
        "date": "01 Nov 2023",
        "md5": "5b3a55c74e457e5834f8289a6f681edb"
    },

    "en-pl/inflection/test": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/inflection.opensubtitles.en-pl.test.json",
        "info": "A test set for English-Polish translation of inflections.",
        "destination": "inflection.opensubtitles.en-pl.test.json",
        "date": "01 Nov 2023",
        "md5": "c24dd2fa86eb777b6efe12add369bf36"
    },
    "en-pl/inflection/devtest":{
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/inflection.opensubtitles.en-pl.devtest.json",
        "info": "A devtest set for English-Polish translation of inflections.",
        "destination": "inflection.opensubtitles.en-pl.devtest.json",
        "date": "01 Nov 2023",
        "md5": "2ff1cb38ecaa1d658b9d20e8bd1247cf"
    },
    "en-pl/inflection/dev": {
        "source": "https://github.com/rewicks/ctxpro/raw/main/release/evalsets/inflection.opensubtitles.en-pl.dev.json",
        "info": "A dev set for English-Polish translation of inflections.",
        "destination": "inflection.opensubtitles.en-pl.dev.json",
        "date": "01 Nov 2023",
        "md5": "e3d35205c47c6c4e706a3aa15524bbe4"
    },

}

def meets_criteria(name, category, language_pair, split):
    name = name.split('/')
    if category and category not in name:
        return False
    if language_pair and language_pair not in name:
        return False
    if split and split not in name:
        return False
    return True

def list_test_sets(category=None, language_pair=None, split=None):
    print("Available evaluation sets:", file=sys.stderr)
    for name, test_set in TESTSETS.items():
        if meets_criteria(name, category, language_pair, split):
            print(f"\t- {name}: {test_set['info']}", file=sys.stderr)

def get_test_data(test_set_name):
    if os.path.exists(test_set_name):
        logger.info("Loading test set from %s" % test_set_name)
        return json.load(open(test_set_name))
    else:
        test_set = TESTSETS.get(test_set_name)
        if test_set is None:
            logger.error("Test set %s not found." % test_set_name)
            logger.error("Available test sets:")
            list_test_sets()
            sys.exit(1)
        else:
            destination = download_test_set(test_set_name)
            return json.load(open(destination))


pbar = None
def show_progress(block_num, block_size, total_size):
    global pbar
    if pbar is None:
        pbar = progressbar.ProgressBar(maxval=total_size)
        pbar.start()

    downloaded = block_num * block_size
    if downloaded < total_size:
        pbar.update(downloaded)
    else:
        pbar.finish()
        pbar = None


def download_test_set(test_set):
    """
    Downloads a test set to the CTXPRO directory.
    """

    expected_checksum = TESTSETS[test_set].get('md5', None)
    test_set_source = TESTSETS[test_set]['source']

    test_set_file = os.path.join(CTXPRO_DIR, os.path.basename(test_set_source))
    test_set_destination = os.path.join(CTXPRO_DIR, TESTSETS[test_set]['destination'])

    os.makedirs(CTXPRO_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(test_set_destination), exist_ok=True)


    if not os.path.exists(test_set_file) or os.path.getsize(test_set_file) == 0:
        logger.info(f"Downloading test set {test_set} from {test_set_source} to {test_set_file}.")
        # download the file
        context = ssl._create_unverified_context()
        with urllib.request.urlopen(test_set_source, context=context) as response, open(test_set_file, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        
    if expected_checksum is not None:
        md5 = hashlib.md5()
        with open(test_set_file, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5.update(chunk)
        if md5.hexdigest() != expected_checksum:
            logger.error(f"Checksum of downloaded file {test_set_file} does not match expected checksum {expected_checksum}.")
            sys.exit(1)

        logger.debug(f"Checksum passes: {md5.hexdigest()}")

    return test_set_destination

def main(args):

    list_test_sets(args.category, args.lang_pair, args.split)
