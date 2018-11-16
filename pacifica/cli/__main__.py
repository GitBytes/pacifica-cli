#!/usr/bin/python
# -*- coding: utf-8 -*-
"""The CLI module contains all the logic needed to run a CLI."""
import sys
import argparse
from os import getenv
from pacifica.uploader.metadata import metadata_decode
from .methods import upload, configure
from .utils import system_config_path


def mangle_config_argument(argv):
    """Get the config argument out of argv and return stripped version."""
    config_arg = '--config'
    len_arg = len(config_arg)
    starts_argv = [arg[:len_arg] for arg in argv]
    if config_arg in starts_argv:
        if config_arg in argv:
            config_file = argv[argv.index(config_arg) + 1]
            del argv[argv.index(config_arg) + 1]
            del argv[argv.index(config_arg)]
        else:
            config_file = argv[starts_argv.index(config_arg)][len_arg + 1:]
            del argv[starts_argv.index(config_arg)]
        return (config_file, argv)
    return (None, argv)


def main():
    """Main method to deal with command line argument parsing."""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='sub-command help')
    upload_parser = subparsers.add_parser(
        'upload', help='upload help', description='perform upload')
    config_parser = subparsers.add_parser(
        'configure', help='configure help', description='setup configuration')

    default_config = getenv(
        'UPLOADER_CONFIG', system_config_path('uploader.json'))
    config_file, argv = mangle_config_argument(sys.argv)
    if not config_file:
        config_file = default_config
    config_data = metadata_decode(open(config_file).read())
    for config_part in config_data:
        if not config_part.value:
            upload_parser.add_argument(
                '--{}-regex'.format(config_part.metaID), required=False,
                dest='{}_regex'.format(config_part.metaID),
                help='{} regular expression match.'.format(
                    config_part.displayTitle)
            )
            upload_parser.add_argument(
                '--{}'.format(config_part.metaID), '-{}'.format(
                    config_part.metaID[0]),
                help=config_part.displayTitle, required=False
            )
    parser.add_argument(
        '--verbose', dest='verbose', default='info',
        help='Enable verbose logging.', required=False
    )
    upload_parser.add_argument(
        '--follow-links', default=False, action='store_true', dest='followlinks',
        help='Follow links to directories when bundling.', required=False
    )
    upload_parser.add_argument(
        '--nowait', default=True, action='store_false', dest='wait',
        help='Wait for the upload is accepted.', required=False
    )
    upload_parser.add_argument(
        '--local-retry', dest='localretry',
        help='Retry and upload from an existing bundle.', required=False
    )
    upload_parser.add_argument(
        '--local-save', dest='localsave', metavar='FILE',
        help='Save the upload bundle to FILE.', required=False
    )
    upload_parser.add_argument(
        '--tar-in-tar', default=False, action='store_true', dest='tarintar',
        help='Create a tar before we upload.', required=False
    )
    upload_parser.add_argument(
        '--dry-run', default=False, action='store_true', dest='dry_run',
        help='Don\'t upload, stop after query engine.', required=False
    )
    upload_parser.add_argument(
        '--do-not-upload', default=False, action='store_true', dest='do_not_upload',
        help='Don\'t upload, works well with local save option.', required=False
    )
    upload_parser.add_argument(
        '--interactive', default=False, action='store_true', dest='interactive',
        help='Interact with the query engine.', required=False
    )
    upload_parser.add_argument(
        'files', metavar='FILES', nargs='*', help='files you want to upload.'
    )
    upload_parser.set_defaults(func=upload)
    config_parser.set_defaults(func=configure)

    args = parser.parse_args(argv[1:])
    args.func(args, config_data)


if __name__ == '__main__':
    main()