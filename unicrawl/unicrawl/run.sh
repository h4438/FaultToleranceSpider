echo "Input code:"
read code
scrapy runspider spiders/auto.py -o data/$code.jsonl --logfile ./logs/$code.log
