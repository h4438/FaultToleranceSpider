import sys
sys.path.append("../../")
from unicrawl import split_extract as extract
import pandas as pd
import os

FOLDER = "/home/h4438/Desktop/app/FaultToleranceSpider/unicrawl/unicrawl/test/samples"

def read_html(file):
    with open(f"{FOLDER}/{file}", "r") as f:
        html = f.readlines()
        html = ''.join(html)
    return html

def test_remove_script():
    files = ["sa.html"]
    tags = [1]
    for file, tag in zip(files, tags):
        html = read_html(file)
        html, removes = extract.remove_tag(html, "<script", "</script>")
        tag_list = extract.list_tags(html)
        assert("script" not in tag_list)
        assert(tag == removes)

def test_remove_img():
    files = ["ab.html", "ac.html", "ad.html", "c.html"]
    imgs = [1, 3, 3, 1]
    for file, img in zip(files, imgs):
        html = read_html(file)
        html, removes = extract.remove_tag(html, "<img", ">")
        tag_list = extract.list_tags(html)
        assert("img" not in tag_list)
        assert(img == removes)

def test_remove_table():
    files = ["table.html"]
    imgs = [1]
    for file, num in zip(files,imgs):
        html = read_html(file)
        content, tables = extract.extract_table_tag(html)
        tag_list = extract.list_tags(content)
        assert("table" not in tag_list)
        assert(len(tables) == num)
        for t in tables:
            assert(t[0] == "<" and t[-1] == ">")

def test_fix_multi_breaks():
    cases = ["Hello\n\n\nWorld", "a\n\nb", "a   b",
            "a\n\n\nb\n\n\nd", "hello\n\n\nbye\n\n\nworld\n\n\ndone."
    ]
    units = ["Hello.\n\nWorld", "a\n\nb","a.\nb", "a.\n\nb.\n\nd",
            "hello.\n\nbye.\n\nworld.\n\ndone."]
    for unit, case in zip(units, cases):
        result = extract.fix_multi_space(case)
        assert(result == unit)

def test_clean_html():
    dirpath = "./test/samples"
    files = [f for f in os.listdir("./test/samples/") if ".html" in f]
    for a in files:
        with open(f"{dirpath}/{a}") as f:
            content = "\n".join(f.readlines())
        mini = extract.clean_html(content).strip()
        lines = mini.split("\n")
        assert(len(lines) == 1)

def test_remove_abnormal():
    df = pd.read_csv(f"{FOLDER}/abnormal.csv")
    for idx, row in df.iterrows():
        result = extract.remove_abnormal(row["not"]).strip()
        assert(result == row['fix'])

def test_get_last_sentence():
    cases = ["This is a cat.He is fun", "This is a cat.He is fun."]
    units = ["He is fun", "He is fun"]
    for unit, case in zip(units, cases):
        result = extract.get_last_sentence(case)
        assert(result == unit)

def test_is_url_relevant():
    df = pd.read_csv(f"{FOLDER}/urls.csv")
    for idx, row in df.iterrows():
        result = extract.is_url_skipable(row["url"])
        assert(result == row["skip"])
