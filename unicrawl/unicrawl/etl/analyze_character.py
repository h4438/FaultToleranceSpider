import pandas as pd
import os

def analyze_words(text):
    words = text.split(" ")

if __name__ == "__main__":
    folder = "./data/tri"
    jsonl_files = os.listdir(folder)
    files = [f for f in jsonl_files if ".jsonl" in f]
    print(files)

