import sys
sys.path.append("../../")
from unicrawl.etl import load 
import pandas as pd
import os
import re

FOLDER = "/home/h4438/Desktop/app/FaultToleranceSpider/unicrawl/unicrawl/test/samples"

def test_nonascii():
    df = pd.read_json(f"{FOLDER}/nonascii.jsonl", lines=True)
    for idx, row in df.iterrows():
        text = load.remove_nonascii(row['txt'])
        assert(text == row['res'])

