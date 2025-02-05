# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

# default behavior
html_with_pdf:
	make html
	make latexpdf
	cp ${SOURCEDIR}/_static/download_pdf.png $(BUILDDIR)/html/_static/
	export PDF_FILENAME=$(shell cat source/conf.py | sed -n "s/.*'\(.*\)\.tex'.*/\1/p"); \
	cp $(BUILDDIR)/latex/$${PDF_FILENAME}.pdf $(BUILDDIR)/html/_static/; \
	sed -i 's/INCLUSION_ZONE_FOR_PDF_DOWNLOAD/\<span\>Télécharger\ le\ PDF :\<a href="_static\/'$${PDF_FILENAME}'.pdf" target="_blank"\> \<img src="_static\/download_pdf.png"\/\> \<\/a\>/g' $(BUILDDIR)/html/index.html

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: html_with_pdf help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
