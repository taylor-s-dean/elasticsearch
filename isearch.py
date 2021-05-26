#!/usr/bin/env python3

import argparse
import readline
from subprocess import PIPE, run
from sys import exit, stdout

import requests
from jprint import jprint

import signal
import json
from enum import Enum

ES_SEARCH_ENDPOINT = "_search"

_input = input


class LocationType(Enum):
    LOCATION_TYPE_UNSPECIFIED = 0
    LOCATION_TYPE_PLANET = 1  # Planet
    LOCATION_TYPE_COUNTRY = 2  # Country
    LOCATION_TYPE_SUBCOUNTRY = 3  # Part of a Country with its own ISO Country Code
    LOCATION_TYPE_ADM1 = 4  # Administrative Division 1 (e.g. State, Province)
    LOCATION_TYPE_ADM2 = 5  # Administrative Division 2 (e.g. County)
    LOCATION_TYPE_ADM3 = 6  # Administrative Division 3
    LOCATION_TYPE_ADM4 = 7  # Administrative Division 4
    LOCATION_TYPE_ADM5 = 8  # Administrative Division 5
    LOCATION_TYPE_ADMD = 9  # Other Administrative Division
    LOCATION_TYPE_PPL = 10  # Populated Place (e.g. City, Town, Village)
    LOCATION_TYPE_PPLX = 11  # Section of a Populated Place (e.g. Neighborhood)
    LOCATION_TYPE_POST = 12  # Postal Code
    LOCATION_TYPE_LEGACY = 13  # A location from the legacy system
    LOCATION_TYPE_LEGACY_POST = 14  # A US zip code location from the legacy system


def signal_handler(sig, frame):
    tput("clear")
    exit(0)


def input(prompt: str, initial: str = ""):
    readline.set_startup_hook(lambda: readline.insert_text(initial))
    try:
        return _input(prompt)
    finally:
        readline.set_startup_hook(None)


def tput(cmd: str, *args):
    args = [str(x) for x in args]
    output = run(["tput", cmd] + args, stdout=PIPE, check=True).stdout.decode()
    stdout.write(output)


def main(args: argparse.Namespace) -> None:
    tput("clear")
    query_text = ""
    while True:
        tput("sc")
        query_text = input("> ", initial=query_text)

        search_query = {
            "size": args.number_of_results,
            "min_score": 0.0001,
            "query": {
                "function_score": {
                    "score_mode": "avg",
                    "boost_mode": "multiply",
                    "script_score": {
                        "script": {
                            "params": {
                                # m is the minimum combined population.
                                # 99 puts the minimum value at 0.5.
                                "m": 99,
                                # p is the weight applied to the population.
                                "p": 2,
                                # pp is the weight applied to the parent population.
                                "pp": 1,
                            },
                            "source": "1 - 1 / (Math.log10(Math.pow(doc['population'].value + 1, params.p)*Math.pow(doc['parent_population'].value + 1, params.pp) + params.m))",
                        }
                    },
                    "query": {
                        "bool": {
                            "filter": [{"term": {"country_code_iso": args.country}}],
                            "must": [
                                {
                                    "multi_match": {
                                        "query": query_text,
                                        "type": "most_fields",
                                        "fuzziness": "AUTO",
                                        "minimum_should_match": 1,
                                        "fields": [
                                            "name.edge_ngram",
                                            "alternate_names.edge_ngram",
                                            "ancestor_names.edge_ngram",
                                            "alternate_ancestor_names.edge_ngram",
                                        ],
                                    }
                                },
                            ],
                            "should": [
                                {
                                    "multi_match": {
                                        "query": query_text,
                                        "type": "most_fields",
                                        "fields": [
                                            "name.normalized^10",
                                            "full_name.normalized^2",
                                        ],
                                    }
                                },
                            ],
                        },
                    },
                },
            },
        }

        if args.query is not None:
            search_query = args.query
            search_query = search_query.replace("QUERY_TEXT", query_text)
            search_query = search_query.replace("SIZE", str(args.number_of_results))
            search_query = search_query.replace("COUNTRY", args.country)
            search_query = json.loads(search_query)

        tput("clear")

        url = "/".join([args.es_url, args.index, ES_SEARCH_ENDPOINT])
        response = requests.post(url, json=search_query)
        if not response.ok:
            jprint(response.json())
            response.raise_for_status()

        search_results = response.json()
        tput("cup", 1, 0)
        max_len = 0
        for result in search_results["hits"]["hits"]:
            length = len(", ".join(result["_source"]["full_name"]))
            if length > max_len:
                max_len = length
        for result in search_results["hits"]["hits"]:
            length = len(", ".join(result["_source"]["full_name"]))
            print(
                ", ".join(result["_source"]["full_name"])
                + " ".join(["" for _ in range(0, max_len - length + 1)])
                + " (population: {:8d}, parent_population: {:8d}, type: {:>20s}, id: {:>9s}, score: {:g})".format(
                    result["_source"]["population"],
                    result["_source"]["parent_population"],
                    LocationType(result["_source"]["location_type"]).name,
                    result["_id"],
                    result["_score"],
                )
            )
        tput("rc")


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)

    parser = argparse.ArgumentParser(formatter_class=argparse.MetavarTypeHelpFormatter)

    parser.add_argument(
        "country",
        type=str,
        help="ISO country code to filter on",
    )

    parser.add_argument(
        "--index",
        type=str,
        required=False,
        default="test",
        help="Name of ElasticSearch index to use",
    )

    parser.add_argument(
        "--number-of-results",
        type=int,
        required=False,
        default=5,
        help="Number of search results to display",
    )

    parser.add_argument(
        "--es-url",
        type=str,
        required=False,
        default="http://localhost:9200",
        help="URL and port of ElasticSearch",
    )

    parser.add_argument(
        "--query",
        type=str,
        required=False,
        help=(
            "Provide a custom search query with placeholders for QUERY_TEXT, SIZE, "
            "and COUNTRY"
        ),
    )

    main(parser.parse_args())
