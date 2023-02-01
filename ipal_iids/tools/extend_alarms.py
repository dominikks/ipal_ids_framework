#!/usr/bin/env python3
import argparse
import gzip
import json
import logging
import sys

import ipal_iids.settings as settings


def open_file(filename, mode="r"):
    if filename is None:
        return None
    elif filename.endswith(".gz"):
        return gzip.open(filename, mode=mode, compresslevel=settings.compresslevel)
    elif filename == "-":
        return sys.stdin
    else:
        return open(filename, mode=mode, buffering=1)


# Initialize logger
def initialize_logger(args):
    if args.log:
        settings.log = getattr(logging, args.log.upper(), None)

        if not isinstance(settings.log, int):
            logging.getLogger("ipal-extend-alarms").error(
                "Option '--log' parameter not found"
            )
            exit(1)

    if args.logfile:
        settings.logfile = args.logfile
        logging.basicConfig(
            filename=settings.logfile, level=settings.log, format=settings.logformat
        )
    else:
        logging.basicConfig(level=settings.log, format=settings.logformat)

    settings.logger = logging.getLogger("ipal-extend-alarms")


def prepare_arg_parser(parser):

    parser.add_argument(
        "files",
        metavar="FILE",
        help="files to extend alarms ('*.gz' compressed).",
        nargs="+",
    )

    # Logging
    parser.add_argument(
        "--log",
        dest="log",
        metavar="STR",
        help="define logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Default is WARNING.",
        required=False,
    )
    parser.add_argument(
        "--logfile",
        dest="logfile",
        metavar="FILE",
        default=False,
        help="File to log to. Default is stderr.",
        required=False,
    )


def extend_alarms(file):

    ipal = []

    # Load file into memory
    with open_file(file, mode="r") as f:
        for line in f.readlines():
            ipal.append(json.loads(line))

    # Extend alarms
    for i in range(len(ipal)):
        if "adjust" not in ipal[i]:
            continue

        if type(ipal[i]["adjust"]) is dict:
            # We should adjust alerts and metrics
            for ids_name, adjust in ipal[i]["adjust"].items():
                for offset, alert, metric in adjust:
                    assert offset <= 0

                    if i + offset < 0:
                        settings.logger.error(
                            f"Offset is {offset + i}! Defaulting to dataset start."
                        )
                        offset = -i

                    ipal[i + offset]["alerts"][ids_name] = alert
                    ipal[i + offset]["metrics"][ids_name] = metric

        else:
            # Adjust alert
            for offset, alert, metric in ipal[i]["adjust"]:
                assert offset <= 0

                if i + offset < 0:  # Log warning!
                    settings.logger.error(
                        f"Offset is {offset + i}! Defaulting to dataset start."
                    )
                    offset = -i

                ipal[i + offset]["ids"] = alert

        del ipal[i]["adjust"]

    # Write file to disc
    with open_file(file, "wt") as f:
        for out in ipal:
            f.write(json.dumps(out) + "\n")


def main():
    parser = argparse.ArgumentParser()
    prepare_arg_parser(parser)

    args = parser.parse_args()
    initialize_logger(args)

    N = 0
    for file in args.files:
        N += 1
        settings.logger.info(
            "Extending Alarms ({}/{}) {}".format(N, len(args.files), file)
        )

        extend_alarms(file)


if __name__ == "__main__":
    main()
