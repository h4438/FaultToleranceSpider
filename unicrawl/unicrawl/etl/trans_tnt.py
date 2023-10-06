from datasets import load_dataset
import os

if __name__ == "__main__":

    os.environ["HUGGINGFACE_TOKEN"] = "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"
    ds = "nlplabtdtu/tnt-edu-crawl"
    dataset = load_dataset(ds)
    breakpoint()

