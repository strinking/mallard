#
# __main__.py
#
# mallard - DDG Instant Answers bot for the Programming Server
# Copyright (c) 2017 Ammon Smith et al.
#
# mallard is available free of charge under the terms of the MIT
# License. You are free to redistribute and/or modify it under those
# terms. It is distributed in the hopes that it will be useful, but
# WITHOUT ANY WARRANTY. See the LICENSE file for more details.
#

import argparse
import logging
import sys

from .client import Client
from .config import load_config

LOG_FILE = 'mallard.log'
LOG_FILE_MODE = 'w'
LOG_FORMAT = "[%(levelname)s] %(name)s: %(message)s"
LOG_DATE_FORMAT = "[%d/%m/%Y %H:%M:%S]"

if __name__ == '__main__':
    # Parse arguments
    argparser = argparse.ArgumentParser(description="DuckDuckGo Discord bot")
    argparser.add_argument('-q', '--quiet',
            dest='quiet', action='store_true',
            help="Be quiet: only output errors")
    argparser.add_argument('-d', '--debug', '--verbose',
            dest='debug', action='store_true',
            help="Enable debug logging.")
    argparser.add_argument('-D', '--ddg-logs',
            dest='ddg_logs', action='store_true',
            help="Enable logs for the DuckDuckGo library.")
    argparser.add_argument('-C', '--color', '--colour',
            dest='color',
            help="Override the embed color used by the bot.")
    argparser.add_argument('-T', '--token',
            dest='token',
            help="Override the bot token used to log in.")
    argparser.add_argument('config_file',
            help="Specify a configuration file to use. Keep it secret!")
    args = argparser.parse_args()

    # Set up logging
    log_fmtr = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    log_hndl = logging.FileHandler(filename=LOG_FILE, mode=LOG_FILE_MODE)
    log_hndl.setFormatter(log_fmtr)
    log_level = (logging.DEBUG if args.debug else logging.INFO)

    main_logger = logging.getLogger('mallard', log_level)
    main_logger.addHandler(log_hndl)

    if args.ddg_logs:
        ddg_logger = logging.getLogger('duckduckgo', log_level)
        ddg_logger.addHandler(log_hndl)

    if not args.quiet:
        log_out_hndl = logging.StreamHandler(sys.stdout)
        log_out_hndl.setFormatter(log_fmtr)
        main_logger.addHandler(log_out_hndl)

        if args.ddg_logs:
            ddg_logger.addHandler(log_out_hndl)

    # Get configuration
    config = load_config(args.config_file)

    if args.color is not None:
        config['color'] = args.color

    if args.token is not None:
        config['bot']['token'] = args.token

    # Create and run client
    client = Client()
    client.run(token=config['bot']['token'])
