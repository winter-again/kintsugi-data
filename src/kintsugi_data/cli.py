import argparse
import shutil
import urllib.request
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


@dataclass
class CommandArgs:
    func: Callable[..., None] = lambda: None

    url: str = ""
    output: Path | None = None

    year: int = 2024
    geo: str = "county"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="kintsugi-data", description="kintsugi-data CLI for common tasks"
    )
    subparsers = parser.add_subparsers(dest="cmd")

    parser_ftp = subparsers.add_parser(
        "ftp", help="Download a file from the Census Bureau's FTP site"
    )
    parser_ftp.add_argument("url", type=str, help="FTP site URL")
    parser_ftp.add_argument(
        "-o", "--output", type=Path, help="Desired location of the downloaded file"
    )
    parser_ftp.set_defaults(func=get_ftp_file)

    parser_geo = subparsers.add_parser(
        "geo",
        help="Download shapefile data for a given year and geography from Census Bureau's FTP site",
    )
    parser_geo.add_argument(
        "year", type=int, default=2024, help="Year of shapefile data"
    )
    parser_geo.add_argument(
        "geo",
        type=str,
        default="county",
        help="Geography of shapefile data: 'county' or 'state' ",
    )
    parser_geo.add_argument(
        "-o", "--output", type=Path, help="Desired location of the downloaded file"
    )
    parser_geo.set_defaults(func=get_shapefile)

    c = CommandArgs()
    args = parser.parse_args(argv, c)
    args.func(args)

    return 0


def get_ftp_file(args: CommandArgs) -> None:
    if args.output is None:
        file_name = args.url.split("/")[-1]
        output = Path.cwd() / file_name
    else:
        output = args.output

    try:
        with urllib.request.urlopen(args.url) as r, open(output, "wb") as f:  # pyright: ignore [reportAny]
            shutil.copyfileobj(r, f)  # pyright: ignore [reportAny]
    except urllib.request.HTTPError as err:
        print(f"Error fetching data: {err}")
        raise SystemExit(1)


def get_shapefile(args: CommandArgs) -> None:
    if args.output is None:
        file_name = args.url.split("/")[-1]
        output = Path.cwd() / file_name
    else:
        output = args.output

    url = f"ftp://ftp2.census.gov/geo/tiger/GENZ{args.year}/shp/cb_{args.year}_us_{args.geo}_5m.zip"
    try:
        with urllib.request.urlopen(url) as r, open(output, "wb") as f:  # pyright: ignore [reportAny]
            shutil.copyfileobj(r, f)  # pyright: ignore [reportAny]
    except urllib.request.HTTPError as err:
        print(f"Error fetching data: {err}")
        raise SystemExit(1)


if __name__ == "__main__":
    raise SystemExit(main())
