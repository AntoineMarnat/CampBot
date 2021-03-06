# -*- coding: utf-8 -*-

from __future__ import division, print_function, unicode_literals

import sys, os
from datetime import datetime
from recommonmark.parser import CommonMarkParser

extensions = ["sphinx.ext.autodoc",]

autodoc_member_order = 'bysource'

templates_path = ['/home/docs/checkouts/readthedocs.org/readthedocs/templates/sphinx', 'templates', '_templates', '.templates']
source_suffix = ['.rst', '.md']
source_parsers = {
            '.md': CommonMarkParser,
        }
master_doc = 'index'
project = u'CampBot'
copyright = "Charles de Beauchesne " + str(datetime.now().year)
version = 'latest'
release = 'latest'
exclude_patterns = ['_build']
pygments_style = 'sphinx'
htmlhelp_basename = 'campbot'
html_theme = 'sphinx_rtd_theme'
file_insertion_enabled = False
latex_documents = [
  ('index', 'campbot.tex', u'CampBot Documentation',
   u'', 'manual'),
]

sys.path.insert(0, os.path.abspath('../'))