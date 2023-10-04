import pandas as pd
import re
from bs4 import BeautifulSoup as BS
from markdownify import markdownify as md
from markdownify import ATX, UNDERSCORE
import os

MAX_WINDOW_SIZE = 1000

def list_tags(html):
    soup = BS(html, "html.parser")
    tags = [tag.name for tag in soup.find_all()]
    return tags

def detect_tag(html, head, tail):
    try:
        start_idx = html.index(head)
        end_idx = html.index(tail,start_idx) + len(tail)
        return [start_idx, end_idx]
    except:
        return None

def remove_tag(html, head, tail):
    removes = 0
    result = html
    clear = False
    while(not clear):
        idx = detect_tag(result, head, tail)
        if idx is None:
            break
        result = result[0:idx[0]] + result[idx[1]:]
        removes += 1
    return result, removes

def extract_table_tag(html):
    tables = []
    result = html
    clear = False
    while not clear:
        idx = detect_tag(result, "<table", "</table>")
        if idx is None:
            break
        tables.append(result[idx[0]: idx[1]])
        result = result[0:idx[0]] + result[idx[1]:]
    return result, tables

def is_url_skipable(url):
    patterns = [r"https://.*/\d*/",r"http://.*/\d*/"]
    for p in patterns:
        result = re.match(p, url) is not None
        if result == True:
            return result
    return False

def fix_multi_breaks(data):
    content = re.sub(r"\n{3,}","\n\n", data)
    return content

def to_md(data):
    data_md = md(
            data,
            heading_style=ATX,
            strong_em_symbol=UNDERSCORE,
    )
    return data_md

def clean(raw_html):
    content = []
    data,_ = remove_tag(raw_html, "<img", ">")
    data,_ = remove_tag(data, "<script", "</script>")
    data,_ = remove_tag(data, "<a", "</a>")
    data = data.replace("\n","").strip()
    data_md = to_md(data)
    content = fix_multi_breaks(data_md)
    return content 

def clean_one_file(file):
    data_path = f"./data/{file}"
    html_tables = []
    df = pd.read_json(data_path, lines=True)
    print("Before:", df.shape)
    df = df[df['body'].str.len() > 0]
    print("After:",df.shape)
    result = []
    for idx, row in df.iterrows():
        if idx%1000 == 0:
            print(idx)
        html_body = "".join(row["body"]).strip()
        html_body, tables = extract_table_tag(html_body)
        #html_tags = list_tags(html_body)
        # body
        body = clean(html_body)
        html_title = "".join(row["title"]).strip()
        title = to_md(html_title)
        result.append({
            "title": title,
            "body": body,
            "url": row["url"],
            "university": row["university"],
            "code": row["code"],
            "hasTable": False 
        })
        # table
        if len(tables) == 0:
            continue
        for t in tables:
            html_tables.append({
                "table":t,
                "code": row["code"],
                "university": row["university"],
                "title": title
            })

    adf = pd.DataFrame(result)
    adf = adf[adf["body"].str.len() > 0]
    adf = adf.drop_duplicates(subset=['body'])
    print("Final:",adf.shape)
    adf.to_json(f"./ok/{file}", orient='records', lines=True, force_ascii=False)
    tdf = pd.DataFrame(html_tables)
    tdf.to_json(f"./table/table_{file}", orient="records", lines=True, force_ascii=False)

if __name__ == "__main__":
    files = os.listdir("./data")
    for f in files:
        print(f)
        clean_one_file(f)
