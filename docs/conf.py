# from pallets_sphinx_themes import get_version
# from pallets_sphinx_themes import ProjectLink

# Project --------------------------------------------------------------

project = "Click"
copyright = "2014 Pallets"
author = "Pallets"
#release, version = get_version("Click")
release, version = ("dev", "0.3")

# General --------------------------------------------------------------

master_doc = "index"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx_rtd_theme",
#    "sphinxcontrib.log_cabinet",
#    "pallets_sphinx_themes",
#    "sphinx_issues",
#    "sphinx_tabs.tabs",
]
autodoc_typehints = "description"
intersphinx_mapping = {"python": ("https://docs.python.org/3/", None)}
issues_github_path = "pallets/click"

exclude_patterns = [
    "\..*",
    "_*",
]

# HTML -----------------------------------------------------------------

html_theme = "sphinx_rtd_theme"
#html_theme_options = {"index_sidebar_logo": False}
html_context = {
    #"project_links": [
    #    ProjectLink("Donate", "https://palletsprojects.com/donate"),
    #    ProjectLink("PyPI Releases", "https://pypi.org/project/click/"),
    #    ProjectLink("Source Code", "https://github.com/pallets/click/"),
    #    ProjectLink("Issue Tracker", "https://github.com/pallets/click/issues/"),
    #    ProjectLink("Chat", "https://discord.gg/pallets"),
    #]
}
html_sidebars = {
    "index": ["project.html", "localtoc.html", "searchbox.html", "ethicalads.html"],
    "**": ["localtoc.html", "relations.html", "searchbox.html", "ethicalads.html"],
}
singlehtml_sidebars = {"index": ["project.html", "localtoc.html", "ethicalads.html"]}
html_static_path = ["_static"]
html_favicon = "_static/click-icon.png"
html_logo = "_static/click-logo-sidebar.png"
html_title = f"Click Documentation ({version})"
html_show_sourcelink = False

# LaTeX ----------------------------------------------------------------

latex_documents = [(master_doc, f"Click-{version}.tex", html_title, author, "manual")]

