import re
import pandas as pd
import os
from datasets import load_dataset

ABNORMAL = ["Thứ .*, \d{2,}/\d{2,}/\d{4,} - \d+:\d+",
        "\[.* ?\]\(.*\)",
        "Số lần đọc:( \d{1,})?",
    r"\d{1,}:\d{1,} \d{1,}\/\d{1,}\/\d{1,} \d{1,}",
]

def remove_nonascii(txt):
    syms = [" ", "\n", ".", ",","/",":","-"]
    result = ""
    for i in range(0, len(txt),3):
        words = txt[i:i+3]
        words = list(words)
        if len(words) < 3:
            result += "".join([w for w in words if w.isalnum() or w in syms])
            continue
        if words[0].isalnum() and words[2].isalnum() and not words[1].isalnum():
            words[1] = " "
        elif words[0].isalnum() and not words[2].isalnum() and not words[1].isalnum():
            words[1] = " "
            words[2] = ""
        else:
            words = [w if (w.isalnum() or w in syms) else " " for w in words]
        result += "".join(words)
    result = re.sub(r" {2,}"," ",result).strip()
    result = re.sub(r" . ",". ",result).strip()
    result = re.sub(r"^\.","",result).strip()
    return result

def is_url_skipable(url):
    patterns = [r"https://.*/\d*/",r"http://.*/\d*/"]
    for p in patterns:
        result = re.match(p, url) is not None
        if result == True:
            return result
    return False

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
    ps = ABNORMAL
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
    eos = ".\n"
    prev_line = ""
    content = []
    for line in para.split(eos):
        line = remove_abnormal(line)
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

def extract_link(text):
    pattern = "(?P<url>https?://[^\s]+)"
    anc = re.match(r"{pattern}",text)
    print(anc)
    return anc

def clean_split(raw_data):
    content = []
    max_size = 1800
    data_md = raw_data.replace(".\n",".")
    data_md = fix_multi_space(raw_data)
    data_md = remove_abnormal(data_md)
    if len(data_md.split(" ")) <= max_size:
        return [data_md]
    content = window_slide(data_md, eos=".", max_size=max_size, size=20)
    return content

def clean_one_file(path, file, outpath):
    data_path = f"{path}/{file}"
    df = pd.read_json(data_path, lines=True)
    print("Before:", df.shape)
    try:
        df = df[df['content'].str.len() > 20]
    except:
        return
    print("After:",df.shape)
    result = []
    for index, row in df.iterrows():
        if index%1000 == 0:
            print(index)
        skip_url = is_url_skipable(row["url"])
        if skip_url:
            continue
        content = row['content']
        bodies = clean_split(content)
        for idx, body in enumerate(bodies):
            result.append({
                "title":row['title'],
                "body": body.strip(),
                "url": row['url']
            })
    adf = pd.DataFrame(result)
    try:
        adf = adf[adf["body"].str.len() > 0]
        adf = adf[adf["body"].str.len() <= 1900]
    except:
        return
    adf = adf.drop_duplicates(subset=['body'])
    print("Final:",adf.shape)
    adf.to_json(f"{outpath}/{file}", orient='records', lines=True, force_ascii=False)

if __name__ == "__main__":
    path = "./data/thang"
    files = os.listdir(path)
    outpath = "./thangd"
    for f in files:
        clean_one_file(path, f, outpath)
    #clean_file(path,outpath)
