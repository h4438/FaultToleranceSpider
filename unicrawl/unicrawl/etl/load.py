import pandas as pd
import re

def strip_emoji(text):
    RE_EMOJI = re.compile(u'([\U00002600-\U000027BF])|([\U0001f300-\U0001f64F])|([\U0001f680-\U0001f6FF])')
    return RE_EMOJI.sub(r'', text)

def remove_emojis(data):
    emoj = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002500-\U00002BEF"  # chinese char
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642" 
        u"\u2600-\u2B55"
        u"\u200d"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f"  # dingbats
        u"\u3030"
                      "]+", re.UNICODE)
    return re.sub(emoj, '', data)

def remove_weirds(text):
    words = [w for w in text.split(" ") if w.isalnum()]
    return " ".join(words)

def remove_nonascii(txt):
    syms = [" ", "\n", ".", ","]
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

def main(folder, filename):
    max_lim = 1900
    min_lim = 1000
    df = pd.read_json(f"{folder}/{filename}",lines=True)
    print("Before",df.shape)
    for i in range(4):    
        df = df.drop_duplicates(subset=["body"])
        print("After",df.shape)
    df['body'] = df['body'].apply(lambda e: remove_nonascii(e))
    lens = df['body'].apply(lambda e: len(e))
    adf = df[df["body"].str.len() <= max_lim]
    adf = adf[adf["body"].str.len() > 0]
    print(f"Long paras > {max_lim}:", df.shape[0]-adf.shape[0])
    print("Avg:",sum(lens)/len(lens))
    print(f"Have:",adf.shape)
    adf.to_json(f"{folder}/train.jsonl", lines=True, orient='records', force_ascii=False)

if __name__ == "__main__":
    main("./hieud","ready.jsonl")
