import re
from argparse import ArgumentParser


def extract_id_from_book_url(url: str):
    book_id = re.search(r"_(\d+)/index\.html$", url).group(1)
    return int(book_id)

def build_cli_parser() -> ArgumentParser:
    parser = ArgumentParser(description="Run the BooksToScrape crawler")
    parser.add_argument(
        "--env",
        choices=["dev", "prod"],
        default="prod",
        help="Enviroment to run the crawler in. If `dev`, only the first page will be crawled"
    )
    parser.add_argument(
        "--restart",
        dest="restart",
        action="store_true",
        help="Drop collections, start afresh and ignore any saved crawler state"
    )
    parser.add_argument(
        "--no-restart",
        dest="restart",
        action="store_false",
        help="Resume from saved crawler state instead of restarting"
    )
    parser.set_defaults(restart=True)
    return parser
