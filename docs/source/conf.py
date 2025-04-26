# docs/source/conf.py
import os
import sys
sys.path.insert(0, os.path.abspath('../../'))  # Путь к корню проекта

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx_rtd_theme',
    'sphinxcontrib.openapi',
]

html_theme = 'sphinx_rtd_theme'