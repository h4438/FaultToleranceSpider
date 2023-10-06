import pandas as pd
import re
from bs4 import BeautifulSoup as BS
from markdownify import markdownify as md
from markdownify import ATX, UNDERSCORE
import os
import htmlmin

EOS = "."
MAX_WINDOW_SIZE = 1800

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

def clean_html(raw_html):
    data,_ = remove_tag(raw_html, "<img", ">")
    data,_ = remove_tag(data, "<script", "</script>")
    data,_ = remove_tag(data, "<a", "</a>")
    html = htmlmin.minify(
            data,
            remove_comments=True,
            remove_empty_space=True,
    )
    return html

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

def to_md(data):
    data_md = md(
            data,
            heading_style=ATX,
            strong_em_symbol=UNDERSCORE,
    )
    return data_md

def fix_multi_space(data):
    if len(data) == 0:
        return data
    tmp = re.sub(r"\n{3,}",".\n\n", data)
    content = re.sub(r"\s{3,}", ".\n", tmp)
    if content[0] == ".":
        return content[1:]
    return content

def remove_abnormal(line):
    result = line
    ps = [r"\d{1,}:\d{1,} \d{1,}\/\d{1,}\/\d{1,} \d{1,}"]
    for p in ps:
        matches = re.search(p, result)
        if matches is None:
            continue
        result = re.sub(p," ",result)
    return result

def get_last_sentence(para, size):
    words = para.split(" ")[-size:]
    return " ".join(words)

def window_slide(para, eos=".", max_size=1800, size=20):
    eos = "."
    prev_line = ""
    content = []
    for line in para.split(eos):
        line = remove_abnormal(line)+"."
        cand_line = (prev_line+"\n"+line).strip()
        cand_length = len(cand_line)
        if cand_length == max_size:
            content.append(cand_line)
            prev_line = get_last_sentence(cand_line,size).strip()

        elif cand_length > max_size:
            content.append(prev_line)
            prev_line = get_last_sentence(cand_line,size).strip()
            prev_line = f"{prev_line}\n{line}"

        else:
            prev_line = cand_line 
    if len(prev_line) != 0:
        content.append(prev_line)
    return content 

def clean_split(raw_html):
    content = []
    max_size = 1800
    html = clean_html(raw_html)
    data_md = to_md(html)
    data_md = fix_multi_space(data_md)
    if len(data_md) <= max_size:
        return [data_md]
    content = window_slide(data_md, eos=".", max_size=max_size, size=20)
    return content

def clean_one_file(path,file, outpath):
    data_path = f"{path}/{file}"
    html_tables = []
    df = pd.read_json(data_path, lines=True)
    print("Before:", df.shape)
    df = df[df['body'].str.len() > 0]
    print("After:",df.shape)
    result = []
    for index, row in df.iterrows():
        if index%1000 == 0:
            print(index)
        html_body = "".join(row["body"]).strip()
        html_body, tables = extract_table_tag(html_body)
        # body
        bodies = clean_split(html_body)
        html_title = "".join(row["title"]).strip()
        title = to_md(html_title)
        for idx, body in enumerate(bodies):
            result.append({
                "title": title.strip(),
                "body": body.strip(),
                "group_id": index,
                "part": idx,
                "total": len(bodies),
                "url": row["url"].strip(),
                "university": row["university"],
                "code": row["code"]
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
    adf.to_json(f"{outpath}/{file}", orient='records', lines=True, force_ascii=False)
    tdf = pd.DataFrame(html_tables)
    tdf.to_json(f"./table/table_{file}", orient="records", lines=True, force_ascii=False)

if __name__ == "__main__":
    path = "./data/hieu"
    outpath = "./hieud"
    files = os.listdir(path)
    for f in files:
        print(f)
        if ".jsonl" not in f:
            continue
        clean_one_file(path, f, outpath)
