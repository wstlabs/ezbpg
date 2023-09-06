#!/bin/sh -ue
#
# A simple smoketest which should verify that the package is basically working.
# Much faster than running the equivalent logic over pytest.
#
python3 -m ezbpg --infile=tests/data/simple.csv $@
