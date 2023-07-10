#!/bin/bash


# Generate autodoc
rm -rf apidoc/*
sphinx-apidoc -f -o apidoc ../cafram/
rm apidoc/modules.rst

# Build doc
echo "Build Documentation ..."
rm -rf _build/html
sphinx-build -v  . _build/html

