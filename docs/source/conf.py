# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------
# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import os
import sys

sys.path.insert(0, f'{os.path.abspath(".")}/../../')

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
project = 'pyneuphonic'
copyright = '2024, Neuphonic'
author = 'Neuphonic'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'myst_parser',
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx_copybutton',
]

myst_enable_extensions = [
    'colon_fence',
    'dollarmath',
    'amsmath',
    'deflist',
    'html_admonition',
    'html_image',
    'smartquotes',
    'replacements',
    'substitution',
    'tasklist',
]

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_book_theme'
html_static_path = ['_static']

# adds the Github logo on the top
html_theme_options = {
    'repository_url': 'https://github.com/neuphonic/pyneuphonic',
    'use_repository_button': True,
    'home_page_in_toc': True,
    'show_toc_level': 3,
    # 'show_navbar_depth': 2,
    # 'max_navbar_depth': 2,
}

# html_sidebars = {
#     "**": ["sbt-sidebar-nav.html"]
# }

html_logo = '_static/logo.png'
html_title = 'Neuphonic Documentation'
html_favicon = '_static/favicon.png'

# Automatically extract typehints when specified and place them in
# descriptions of the relevant function/method.
autodoc_typehints = 'description'

# Don't show class signature with the class' name.
autodoc_class_signature = 'separated'
