# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('../../'))
sys.path.insert(0, os.path.abspath('../../dbimat'))
sys.path.insert(0, os.path.abspath('../../dbimat/source/'))
sys.path.insert(0, os.path.abspath('../../dbimat/source/basic/'))
sys.path.insert(0, os.path.abspath('../../dbimat/source/helper/'))
sys.path.insert(0, os.path.abspath('../../dbimat/source/model_base/'))
sys.path.insert(0, os.path.abspath('../../dbimat/source/model_base/dataclasses/'))
sys.path.insert(0, os.path.abspath('../../dbimat/source/modules/'))
for p in sys.path:
    print(p)
# -- Project information -----------------------------------------------------

project = 'DBI-MAT'
copyright = '2022, Marcus,Martin,Martin,Frank'
author = 'Marcus,Martin,Martin,Frank'

# The full version, including alpha/beta/rc tags
release = '14.03.2022'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension modules names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.napoleon',
              'sphinx.ext.todo',
              'sphinx_git'
              ]
# root doc

master_doc = 'index'
# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True
todo_link_only = True

version = u"test"
# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'
# html_theme = 'classic'
# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Autodoc Options

# Autodoc Class Signature
# FFi: can be "mixed"(default) or "separated"
# FFi: separated looks better imo

autodoc_class_signature = 'mixed'

# Autodoc Default Options

# The supported options are 'members', 'member-order', 'undoc-members', 'private-members',
# 'special-members', 'inherited-members', 'show-inheritance', 'ignore-modules-all', 'imported-members',
# 'exclude-members' and 'class-doc-from'.
# FFi: exclude members doesnt make sense here. should be done in the .rst file
# FFi: member order can be "bysource" "alphabetical"(default) or  "groupwise"
# FFi: No idea how it interacts with the .rst files yet
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'inherited-members': True,
}

# Autodoc MockImports

# This value contains a list of modules to be mocked up. This is useful when some external
# dependencies are not met at build time and break the building process. You may only specify the root package of the
# dependencies themselves and omit the sub-modules:

#autodoc_mock_imports = ["django"] # FFi: Example just there if needed.


# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = True
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = True
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True
