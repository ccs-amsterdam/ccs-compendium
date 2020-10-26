#!/usr/bin/env python3
#CREATES: data/intermediate/sample.txt
#TITLE: Example module without input


import sys

from compendium.compendium import Compendium

fn = Compendium().folders.DATA_INTERMEDIATE/"sample.txt"
fn.open("w").write("This is example text")
