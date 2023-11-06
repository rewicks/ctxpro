#!/usr/bin/env python

"""
A setuptools based setup module.
See:
- https://packaging.python.org/en/latest/distributing.html
- https://github.com/pypa/sampleproject
To install:
1. Setup pypi by creating ~/.pypirc
        [distutils]
        index-servers =
          pypi
          pypitest
        [pypi]
        username=
        password=
        [pypitest]
        username=
        password=
2. Create the dist
   python3 setup.py sdist bdist_wheel
3. Push
   twine upload dist/*
"""

import os
import re

# Always prefer setuptools over distutils
from setuptools import setup, find_packages

ROOT = os.path.dirname(__file__)


def get_version():
    """
    Reads the version from ctxpro's __init__.py file.
    We can't import the module because required modules may not
    yet be installed.
    """
    VERSION_RE = re.compile(r'''__version__ = ['"]([0-9.]+)['"]''')
    init = open(os.path.join(ROOT, 'ctxpro', '__init__.py')).read()
    return VERSION_RE.search(init).group(1)


def get_description():
    DESCRIPTION_RE = re.compile(r'''__description__ = ['"](.*)['"]''')
    init = open(os.path.join(ROOT, 'ctxpro', '__init__.py')).read()
    return DESCRIPTION_RE.search(init).group(1)



def install_ctxpro(**kwargs):
    setup(
        name = 'ctxpro',

        # Versions should comply with PEP440.  For a discussion on single-sourcing
        # the version across setup.py and the project code, see
        # https://packaging.python.org/en/latest/single_source_version.html
        version = get_version(),

        description = get_description(),

        long_description= "CTXPRO is a rule-based toolkit for annotating examples of ambiguity found in parallel documents."
                            "It further provides access to the CTXPRO evaluation sets and scoring scripts.",


        # The project's main homepage.
        url = 'https://github.com/rewicks/MultiPro',

        author = 'Rachel Wicks',
        author_email='rewicks@jhu.edu',
        maintainer_email='rewicks@jhu.edu',

        license = 'Apache License 2.0',

        python_requires = '>=3,<3.12',

        # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
        classifiers = [
            # How mature is this project? Common values are
            #   3 - Alpha
            #   4 - Beta
            #   5 - Production/Stable
            'Development Status :: 5 - Production/Stable',

            # Indicate who your project is intended for
            'Intended Audience :: Developers',
            'Intended Audience :: Science/Research',
            'Topic :: Scientific/Engineering',
            'Topic :: Scientific/Engineering :: Artificial Intelligence',
            'Topic :: Text Processing',

            # Pick your license as you wish (should match "license" above)
            'License :: OSI Approved :: Apache Software License',

            # Specify the Python versions you support here. In particular, ensure
            # that you indicate whether you support Python 2, Python 3 or both.
            'Programming Language :: Python :: 3 :: Only',
        ],

        # What does your project relate to?
        keywords = ['evaluation sets, document translation, context-aware translation, machine translation, data processing, preprocessing, evaluation, NLP, natural language processing, computational linguistics'],

        # Which packages to deploy (currently sacrebleu, sacrebleu.matrics and sacrebleu.tokenizers)?
        packages = find_packages(),

        # Mark ctxpro (and recursively all its sub-packages) as supporting mypy type hints (see PEP 561).
        package_data={"ctxpro": ["py.typed"]},

        setup_requires = [],
        # setup_requires = ["numpy>=1.21", "Cython"],
        # List run-time dependencies here.  These will be installed by pip when
        # your project is installed. For an analysis of "install_requires" vs pip's
        # requirements files see:
        # https://packaging.python.org/en/latest/requirements.html
        install_requires = [
            'typing;python_version<"3.5"',
            'sentence-splitter>=1.4',
            "progressbar",
            "tqdm",
            "sentencepiece"
        ],

        # List additional groups of dependencies here (e.g. development
        # dependencies). You can install these using the following syntax,
        # for example:
        # $ pip install -e .[dev,test]
        extras_require = {
            "identify": [
                "spacy>=3.5.0,<4",
                "fastcoref>=2.1.6",
                "simalign>=0.3",
                "spacy_download",
                "spacy-transformers>=1.2.4",
                "spacy_curated_transformers>=0.2.0",
                "curated_tokenizers>=0.0.8",
            ]
        },

        # To provide executable scripts, use entry points in preference to the
        # "scripts" keyword. Entry points provide cross-platform support and allow
        # pip to create the appropriate form of executable for the target platform.
        entry_points={
            'console_scripts': [
                'ctxpro = ctxpro.__main__:main'
            ],
        },
    )

install_ctxpro()