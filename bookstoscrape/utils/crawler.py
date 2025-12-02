import re
import time


def extract_id_from_book_url(url: str):
    book_id = re.search(r"_(\d+)/index\.html$", url).group(1)
    return int(book_id)

def get_milliseconds_since_epoch():
    return int(time.time() * 1000)
