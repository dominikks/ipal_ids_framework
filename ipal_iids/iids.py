#!/usr/bin/env python3
import argparse
import gzip
import json
import logging
import os
import sys
import time

from pathlib import Path
from combiner.utils import get_all_combiners

import ipal_iids.settings as settings

from ids.utils import get_all_iidss


# Wrapper for hiding .gz files
def open_file(filename, mode):
    if filename.endswith(".gz"):
        return gzip.open(filename, mode=mode, compresslevel=settings.compresslevel)
    else:
        return open(filename, mode=mode, buffering=1)


# Initialize logger
def initialize_logger(args):

    if args.log:
        settings.log = getattr(logging, args.log.upper(), None)

        if not isinstance(settings.log, int):
            logging.getLogger("ipal-iids").error("Option '--log' parameter not found")
            exit(1)

    if args.logfile:
        settings.logfile = args.logfile
        logging.basicConfig(
            filename=settings.logfile, level=settings.log, format=settings.logformat
        )
    else:
        logging.basicConfig(level=settings.log, format=settings.logformat)

    settings.logger = logging.getLogger("ipal-iids")


def dump_ids_default_config(name):
    if name not in settings.idss:
        settings.logger.error("IDS {} not found! Use one of:".format(name))
        settings.logger.error(", ".join(settings.idss.keys()))
        exit(1)

    # Create IDSs default config
    config = {
        name: {"_type": name, **get_all_iidss()[name](name=name)._default_settings,}
    }
    config[name]["model-file"] = "./model"

    # Output a pre-filled config file
    print(json.dumps(config, indent=4))
    exit(0)


def prepare_arg_parser(parser):

    # Input and output
    parser.add_argument(
        "--train.ipal",
        dest="train_ipal",
        metavar="FILE",
        help="input file of IPAL messages to train the IDS on ('-' stdin, '*.gz' compressed).",
        required=False,
    )
    parser.add_argument(
        "--train.state",
        dest="train_state",
        metavar="FILE",
        help="input file of IPAL state messages to train the IDS on ('-' stdin, '*.gz' compressed).",
        required=False,
    )
    parser.add_argument(
        "--train-combiner.ipal",
        dest="train_combiner_ipal",
        metavar="FILE",
        help="input file of IPAL messages to train the combiner on ('-' stdin, '*.gz' compressed).",
        required=False,
    )
    parser.add_argument(
        "--train-combiner.state",
        dest="train_combiner_state",
        metavar="FILE",
        help="input file of IPAL state messages to train the combiner on ('-' stdin, '*.gz' compressed).",
        required=False,
    )
    parser.add_argument(
        "--live.ipal",
        dest="live_ipal",
        metavar="FILE",
        help="input file of IPAL messages to perform the live detection on ('-' stdin, '*.gz' compressed).",
        required=False,
    )
    parser.add_argument(
        "--live.state",
        dest="live_state",
        metavar="FILE",
        help="input file of IPAL state messages to perform the live detection on ('-' stdin, '*.gz' compressed).",
        required=False,
    )
    parser.add_argument(
        "--live.combiner",
        dest="live_combiner",
        metavar="FILE",
        help="input file of IDS-processed IPAL messages to apply the combiner on ('-' stdin, '*.gz' compressed).",
        required=False,
    )
    parser.add_argument(
        "--output",
        dest="output",
        metavar="FILE",
        help="output file to write the anotated IDS output to (Default:none, '-' stdout, '*.gz' compress).",
        required=False,
    )
    parser.add_argument(
        "--output.train-combiner",
        dest="output_train_combiner",
        metavar="FILE",
        help="output file to write the annotated IDS output on the combiner train set to (Default:none, '-' stdout, '*.gz' compress).",
    )
    parser.add_argument(
        "--config",
        dest="config",
        metavar="FILE",
        help="load IDS and combiner configuration and parameters from the specified file ('*.gz' compressed).",
        required=False,
    )

    # Further options
    parser.add_argument(
        "--default.config",
        dest="defaultconfig",
        metavar="IDS",
        help="dump the default configuration for the specified IDS to stdout and exit, can be used as a basis for writing IDS config files. Available IIDSs are: {}".format(
            ",".join(settings.idss.keys())
        ),
        required=False,
    )

    parser.add_argument(
        "--retrain",
        dest="retrain",
        help="retrain regardless of a trained model file being present.",
        action="store_true",
        required=False,
    )

    # Logging
    parser.add_argument(
        "--log",
        dest="log",
        metavar="STR",
        help="define logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) (Default: WARNING).",
        required=False,
    )
    parser.add_argument(
        "--logfile",
        dest="logfile",
        metavar="FILE",
        default=False,
        help="file to log to (Default: stderr).",
        required=False,
    )

    # Gzip compress level
    parser.add_argument(
        "--compresslevel",
        dest="compresslevel",
        metavar="INT",
        default=9,
        help="set the gzip compress level. 0 no compress, 1 fast/large, ..., 9 slow/tiny. (Default: 9)",
        required=False,
    )


# Returns IDS according to the provided config
def parse_ids_arguments():
    all_idss = get_all_iidss()
    all_combiners = get_all_combiners()

    idss = []
    combiners = []

    # IDS defined by config file
    for name, config in settings.idss.items():
        if config["_type"] in all_idss:
            idss.append(all_idss[config["_type"]](name=name))
        elif config["_type"] in all_combiners:
            combiners.append(all_combiners[config["_type"]](name=name))
        else:
            settings.logger.error(
                f"Invalid config: unknown IDS/Combiner type: {config['_type']}"
            )
            exit(1)

    return idss, combiners


def load_settings(args):  # noqa: C901

    if args.defaultconfig:
        dump_ids_default_config(args.defaultconfig)

    # Gzip compress level
    if args.compresslevel:
        try:
            settings.compresslevel = int(args.compresslevel)
        except ValueError:
            settings.logger.error(
                "Option '--compresslevel' must be an integer from 0-9"
            )
            exit(1)

        if settings.compresslevel < 0 or 9 < settings.compresslevel:
            settings.logger.error(
                "Option '--compresslevel' must be an integer from 0-9"
            )
            exit(1)

    # Catch incompatible combinations
    if not args.config:
        settings.logger.error("no IDS configuration provided, exiting")
        exit(1)

    # This is a limitation required for the combiner to work properly
    if args.train_combiner_ipal and args.train_combiner_state:
        settings.logger.error("cannot take two datasets as combiner training input")
        exit(1)

    # Parse training input
    if args.train_ipal:
        settings.train_ipal = args.train_ipal
    if args.train_state:
        settings.train_state = args.train_state
    if args.train_combiner_ipal:
        settings.train_combiner_ipal = args.train_combiner_ipal
    if args.train_combiner_state:
        settings.train_combiner_state = args.train_combiner_state

    # Parse live ipal input
    if args.live_ipal:
        settings.live_ipal = args.live_ipal
    if settings.live_ipal:
        if settings.live_ipal != "stdout" and settings.live_ipal != "-":
            settings.live_ipalfd = open_file(settings.live_ipal, "r")
        else:
            settings.live_ipalfd = sys.stdin

    # Parse live state input
    if args.live_state:
        settings.live_state = args.live_state
    if settings.live_state:
        if settings.live_state != "stdin" and settings.live_state != "-":
            settings.live_statefd = open_file(settings.live_state, "r")
        else:
            settings.live_statefd = sys.stdin

    # Parser combiner input
    if args.live_combiner:
        settings.live_combiner = args.live_combiner
        if settings.live_combiner != "stdin" and settings.live_combiner != "-":
            settings.live_combinerfd = open_file(settings.live_combiner, "r")
        else:
            settings.live_combinerfd = sys.stdin

    # Parse retrain
    if args.retrain:
        settings.retrain = True
        settings.logger.info("Retraining models")

    # Parse output
    if args.output:
        settings.output = args.output
    if settings.output:
        if settings.output != "stdout" and settings.output != "-":
            # clear the file we are about to write to
            open_file(settings.output, "wt").close()
            settings.outputfd = open_file(settings.output, "wt")
        else:
            settings.outputfd = sys.stdout

    if args.output_train_combiner:
        settings.output_traincombiner = args.output_train_combiner
    if settings.output_traincombiner:
        if (
            settings.output_traincombiner != "stdout"
            and settings.output_traincombiner != "-"
        ):
            # clear the file we are about to write to
            open_file(settings.output_traincombiner, "wt").close()
            settings.output_traincombinerfd = open_file(
                settings.output_traincombiner, "wt"
            )
        else:
            settings.output_traincombinerfd = sys.stdout

    # Parse config
    settings.config = args.config

    config_file = Path(settings.config).resolve()
    if config_file.is_file():
        with open_file(settings.config, "r") as f:
            try:
                settings.idss = json.load(f)
            except json.decoder.JSONDecodeError as e:
                settings.logger.error("Error parsing config file")
                settings.logger.error(e)
                exit(1)
    else:
        settings.logger.error("Could not find config file at {}".format(config_file))
        exit(1)


def train_idss(idss):
    # Try to load an existing model from file
    loaded_from_file = []
    for ids in idss:
        if settings.retrain:
            continue

        try:
            if ids.load_trained_model():
                loaded_from_file.append(ids)
                settings.logger.info(
                    "IDS {} loaded a saved model successfully.".format(ids._name)
                )
        except NotImplementedError:
            settings.logger.info(
                "Loading model from file not implemented for {}.".format(ids._name)
            )

    # Check if all datasets necessary for the selected IDSs are provided
    for ids in idss:
        if ids in loaded_from_file:
            continue
        if ids.requires("train.ipal") and settings.train_ipal:
            continue
        if ids.requires("train.state") and settings.train_state:
            continue

        settings.logger.error(
            "Required arguement: {} for IDS {}".format(ids._requires, ids._name)
        )
        exit(1)

    # Give the various IDSs the dataset they need in their learning phase
    for ids in idss:
        if ids in loaded_from_file:
            continue

        start = time.time()
        settings.logger.info("Training of {} started at {}".format(ids._name, start))

        ids.train(ipal=settings.train_ipal, state=settings.train_state)

        end = time.time()
        settings.logger.info(
            "Training of {} ended at {} ({}s)".format(ids._name, end, end - start)
        )

        # Try to save the trained model
        try:
            if ids.save_trained_model():
                settings.logger.info(
                    "Saved trained model of {} to file.".format(ids._name)
                )
        except NotImplementedError:
            settings.logger.info(
                "Saving model to file not implemented for {}.".format(ids._name)
            )


def train_combiners(idss, combiners):
    trainable_combiners = [
        combiner for combiner in combiners if combiner._needs_training
    ]

    # Attempt to load combiners from disk
    loaded_from_file = []
    if not settings.retrain:
        for combiner in trainable_combiners:
            if combiner.load_trained_model():
                settings.logger.info(
                    "Combiner {} loaded a saved model successfully.".format(
                        combiner._name
                    )
                )
                loaded_from_file.append(combiner)

    # If all combiners were loaded from disk, we can abort
    if (
        len(loaded_from_file) == len(trainable_combiners)
        and not settings.output_traincombiner
    ):
        return

    # Load the dataset and compute alerts from all IDSs
    msgs = []

    if not (settings.train_combiner_ipal or settings.train_combiner_state):
        settings.logger.error("Required arguement: combiner training set")
        exit(1)

    settings.logger.info("Loading dataset for combiner training.")

    with open_file(
        settings.train_combiner_ipal or settings.train_combiner_state, "rt"
    ) as f:
        ipal_mode = bool(settings.train_combiner_ipal)

        for msg in f:
            msg = json.loads(msg)

            if "alerts" not in msg:
                msg["alerts"] = {}
            if "metrics" not in msg:
                msg["metrics"] = {}

            for ids in idss:
                if (
                    ids.requires("live.ipal" if ipal_mode else "live.state")
                    and ids._name not in msg["alerts"]
                ):
                    alert, metric = (
                        ids.new_ipal_msg(msg) if ipal_mode else ids.new_state_msg(msg)
                    )
                    msg["alerts"][ids._name] = alert
                    msg["metrics"][ids._name] = metric

            msgs.append(msg)

    # Save dataset to disk
    if settings.output_traincombiner:
        is_first = True

        for msg in msgs:
            if is_first:
                msg["_iids-config"] = settings.iids_settings_to_dict()
                is_first = False

            settings.output_traincombinerfd.write(json.dumps(msg) + "\n")
            settings.output_traincombinerfd.flush()

    # Run combiner training with our loaded messages
    for combiner in trainable_combiners:
        if combiner in loaded_from_file:
            continue

        start = time.time()
        settings.logger.info(
            "Training of combiner {} started at {}".format(combiner._name, start)
        )

        combiner.train(msgs=msgs)

        end = time.time()
        settings.logger.info(
            "Training of combiner {} ended at {} ({}s)".format(
                combiner._name, end, end - start
            )
        )

        if combiner.save_trained_model():
            settings.logger.info(
                "Saved trained model of combiner {} to file.".format(combiner._name)
            )

    settings.logger.info("Combiner training finished.")


def live_idss(idss, combiners):
    # Keep track of the last state and message information. Then we are capable of delivering them in the right order.
    msg_sources = {
        "ipal": {"msg": None, "is_first": True, "fd": settings.live_ipalfd},
        "state": {"msg": None, "is_first": True, "fd": settings.live_statefd},
        "combiner": {"msg": None, "is_first": True, "fd": settings.live_combinerfd},
    }

    while True:
        # load new msgs for all types
        for msg_source in msg_sources.values():
            if msg_source["msg"] is None and msg_source["fd"]:
                line = msg_source["fd"].readline()
                if line:
                    msg_source["msg"] = json.loads(line)

        # filter out sources that do not have a message
        available_sources = {
            k: v for k, v in msg_sources.items() if v["msg"] is not None
        }

        # Determine next msg based on timestamp: ipal, state or combiner
        source, source_entry = min(
            available_sources.items(),
            key=lambda item: item[1]["msg"]["timestamp"],
            default=(None, None),
        )
        if source is None:  # handled all messages
            break

        msg = source_entry["msg"]

        if not "alerts" in msg:
            msg["alerts"] = {}
        if not "metrics" in msg:
            msg["metrics"] = {}

        msg["combiner_alerts"] = {}
        msg["combiner_metrics"] = {}

        for ids in idss:
            if source == "ipal" and ids.requires("live.ipal"):
                alert, metric = ids.new_ipal_msg(msg)
            elif source == "state" and ids.requires("live.state"):
                alert, metric = ids.new_state_msg(msg)
            else:  # combiner msgs do not need an ids invocation
                continue

            msg["alerts"][ids._name] = alert
            msg["metrics"][ids._name] = metric

        for combiner in combiners:
            alert, metric = combiner.combine(msg)

            msg["combiner_alerts"][combiner._name] = alert
            msg["combiner_metrics"][combiner._name] = metric

        # Take the output of the first combiner as global output
        msg["ids"] = msg["combiner_alerts"][combiners[0]._name]

        if settings.output:

            if source_entry["is_first"]:
                msg["_iids-config"] = settings.iids_settings_to_dict()
                source_entry["is_first"] = False

            settings.outputfd.write(json.dumps(msg) + "\n")
            settings.outputfd.flush()

        source_entry["msg"] = None


def main():
    # Argument parser and settings
    parser = argparse.ArgumentParser()
    prepare_arg_parser(parser)
    args = parser.parse_args()
    initialize_logger(args)
    load_settings(args)
    idss, combiners = parse_ids_arguments()

    if not combiners:
        # Make sure there is at least one combiner
        settings.idss["DefaultOrCombiner"] = {"_type": "OrCombiner"}
        combiners.append(get_all_combiners()["Or"](name="DefaultOrCombiner"))

    try:
        # Train IDSs
        settings.logger.info("Start IDS training...")
        train_idss(idss)

        # Train combiner
        settings.logger.info("Start combiner training...")
        train_combiners(idss, combiners)

        # Live IDS
        settings.logger.info("Start IDS live...")
        live_idss(idss, combiners)
    except BrokenPipeError:
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())

    # Finalize and close
    if settings.output and settings.outputfd != sys.stdout:
        settings.outputfd.close()
    if settings.output_traincombiner and settings.output_traincombinerfd != sys.stdout:
        settings.output_traincombinerfd.close()
    if settings.live_ipal:
        settings.live_ipalfd.close()
    if settings.live_state:
        settings.live_statefd.close()


if __name__ == "__main__":
    main()
