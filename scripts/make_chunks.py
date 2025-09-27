import argparse
from pathlib import Path
import json

parser = argparse.ArgumentParser()
parser.add_argument("--input-dir", default="data/docs")
parser.add_argument("--output-dir", default="data/chunks")  # <-- add this
args = parser.parse_args()
