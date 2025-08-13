# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys
sys.path.insert(0, os.path.abspath('../'))  # 如果你的模块位于上一级目录
project = 'ASEngine-Client'
copyright = '2025, OpelaCake'
author = 'OpelaCake'
release = '0.0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.githubpages',  # 生成 .nojekyll 和 sitemap
    'sphinx.ext.autodoc'
]


templates_path = ['_templates']
exclude_patterns = []
html_theme = 'sphinx_rtd_theme'
html_theme_options = {
        "dark_css_variables": {
        "color-background": "#2E2E2E",  # 背景颜色
        "color-text": "#EAEAEA",         # 文字颜色
        "color-link": "#007ACC",         # 链接颜色
        "color-link-hover": "#005F8A",   # 链接悬停时颜色
        # 可以根据需要修改其他 CSS 变量
    }
}



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
