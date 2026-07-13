#!/bin/bash
# LATW dev branch: these tutorials run on the DEVELOPMENT stack, which is
# installed by LISAanalysistools' install.sh — not by this script.
#
# The main branch of LATW (pip-release tutorials) keeps the conda + pip
# release installer; on dev this file only points you the right way.

cat <<'EOF'
LATW dev branch — the tutorials here require the development stack.

Install it with the LISAanalysistools dev installer (clones and
editable-installs every sibling repo, including this one):

    git clone https://github.com/lisa-analysis-tools/lisa-analysis-tools.git LISAanalysistools
    bash LISAanalysistools/install.sh

For the pip-release tutorials (conda + `pip install lisaanalysistools ...`),
switch to the main branch:

    git checkout main && bash install.sh
EOF
exit 1
