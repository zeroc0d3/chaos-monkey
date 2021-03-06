# Copyright 2015 Canonical Ltd.
# Licensed under the AGPLv3, see LICENCE file for details.
from __future__ import print_function

import errno
import logging
from logging.handlers import RotatingFileHandler
import os
from shutil import rmtree
from subprocess import (
    CalledProcessError,
    check_output,
)
from tempfile import mkdtemp

from contextlib import contextmanager
from yaml import dump


def ensure_dir(path):
    """Ensure a directory exists. If it doesn't exist, it will be created."""
    try:
        os.mkdir(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def run_shell_command(cmd, quiet_mode=False):
    """Run a shell command.

    :param quiet_mode: When False, generate a CalledProcessError
       exception on error.
    """
    shell_cmd = cmd.split(' ') if type(cmd) is str else cmd
    output = None
    try:
        output = check_output(shell_cmd)
    except CalledProcessError:
        logging.error("Command generated error: %s " % cmd)
        if not quiet_mode:
            raise
    return output


def setup_logging(log_path, log_count, log_level=logging.INFO, name=None,
                  add_stream=True, disable_formatter=False):
    """Install log handlers to output to file and stream."""
    formatter = None if disable_formatter else logging.Formatter(
        '%(asctime)s %(levelname)s %(message)s', '%Y-%m-%d %H:%M:%S')
    logger = logging.getLogger(name)
    logger.propagate = 0
    rf_handler = RotatingFileHandler(
        log_path, maxBytes=1024 * 1024 * 512, backupCount=log_count)
    rf_handler.setFormatter(formatter)
    logger.addHandler(rf_handler)
    if add_stream:
        s_handler = logging.StreamHandler()
        s_handler.setFormatter(formatter)
        logger.addHandler(s_handler)
    logger.setLevel(log_level)


def split_arg_string(arg_string):
    """Split string using comma as delimiter."""
    if not arg_string:
        return []
    return arg_string.split(',') if ',' in arg_string else [arg_string]


@contextmanager
def temp_dir():
    """Create a temporary directory."""
    dirname = mkdtemp()
    try:
        yield dirname
    finally:
        rmtree(dirname)


class NotFound(Exception):
    """Requested resource not found"""
    error_code = 404


class BadRequest(Exception):
    """Incorrectly formatted  request"""
    error_code = 400


class StructuredMessage:
    """Create YAML structured message."""
    def __init__(self, *args):
        self.args = args

    def __str__(self):
        # -1 to remove the newline
        return dump([list(self.args)])[:-1]
