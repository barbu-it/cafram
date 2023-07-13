"""
colargulog - Python3 Logging with Colored Arguments and new string formatting style

Written by david.ohana@ibm.com
License: Apache-2.0
"""

# TODO: Fix Mypy
# mypy: ignore-errors

import logging
import logging.handlers
import re
import sys

logger_sfmt = {
    "default": None,
    # "colors": "%(levelname)8s: %(message)s",
    "basic": "%(levelname)8s: %(message)s",
    "struct": "%(name)-40s%(levelname)8s: %(message)s",
    "time": "%(asctime)s.%(msecs)03d|%(name)-16s%(levelname)8s: %(message)s",
    "precise": (
        "%(asctime)s.%(msecs)03d"
        + " (%(process)d/%(thread)d) "
        + "%(pathname)s:%(lineno)d:%(funcName)s"
        + ": "
        + "%(levelname)s: %(message)s"
    ),
}
logger_tfmt = {
    "default": None,
    "basic": "%H:%M:%S",
    "precise": "%Y-%m-%d %H:%M:%S",
}


def app_logger(name=None, logger=None, level=None, sfmt=None, tfmt=None, colors=None):
    "Logging basicConfig alternative with logger choice"

    name = name or None
    # level = level or logging.WARNING
    # sfmt = sfmt or '%(name)s - %(levelname)s - %(message)s'

    # Get formats
    # print ("FORMAT ", sfmt, name)
    sfmt = sfmt  # or 'default'
    # print ("FORMAT ", sfmt)
    sfmt = logger_sfmt.get(sfmt, sfmt)
    # print ("FORMAT ", sfmt, colors)
    tfmt = tfmt  # or 'default'
    tfmt = logger_tfmt.get(tfmt, tfmt)

    # Get logger or root if None
    logger = logger or logging.getLogger(name)
    if level:
        logger.setLevel(level)

    # Determine next action
    _colors = colors if isinstance(colors, bool) else sys.stdout.isatty()
    if not (sfmt or tfmt or _colors):
        logger.propagate = True
        return logger

    if _colors:

        # Colorization only happens on level name, so we add ensure levelname is present
        # especially if user set colors=True
        if colors is True:
            if not sfmt:
                sfmt = "%(levelname)7s: %(message)s"
            if sfmt and not "levelname" in sfmt:
                sfmt = "%(levelname)7s: " + sfmt

        formatter = ColorizedArgsFormatter(fmt=sfmt, datefmt=tfmt)
    else:
        formatter = logging.Formatter(fmt=sfmt, datefmt=tfmt)

    # Cleanup existing handlers
    if logger.handlers:
        for handler in logger.handlers:
            logger.removeHandler(handler)
    hand = logging.StreamHandler()

    # create a stream handler and set the formatter
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    # add the handler to the logger
    logger.addHandler(handler)

    # logger.propagate = False

    return logger


class ColorCodes:
    "Holds color codes"

    grey = "\x1b[38;21m"
    green = "\x1b[1;32m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    blue = "\x1b[1;34m"
    light_blue = "\x1b[1;36m"
    purple = "\x1b[1;35m"
    reset = "\x1b[0m"


class ColorizedArgsFormatter(logging.Formatter):
    "ColorizedArgsFormatter"

    arg_colors = [ColorCodes.purple, ColorCodes.light_blue]
    level_fields = ["levelname", "levelno"]
    level_to_color = {
        logging.DEBUG: ColorCodes.grey,
        logging.INFO: ColorCodes.green,
        logging.WARNING: ColorCodes.yellow,
        logging.ERROR: ColorCodes.red,
        logging.CRITICAL: ColorCodes.bold_red,
    }

    # Actual signature:
    # def __init__(self, fmt=None, datefmt=None, style='%', validate=True, *,defaults=None):
    def __init__(self, fmt: str = None, **kwargs):
        super().__init__()
        self.level_to_formatter = {}

        fmt = fmt or self._fmt

        def add_color_format(level: int):
            color = ColorizedArgsFormatter.level_to_color[level]
            _format = fmt
            for fld in ColorizedArgsFormatter.level_fields:
                search = "(%\\(" + fld + "\\).*?s)"
                _format = re.sub(search, f"{color}\\1{ColorCodes.reset}", _format)
            formatter = logging.Formatter(fmt=_format, **kwargs)
            self.level_to_formatter[level] = formatter

        add_color_format(logging.DEBUG)
        add_color_format(logging.INFO)
        add_color_format(logging.WARNING)
        add_color_format(logging.ERROR)
        add_color_format(logging.CRITICAL)

    @staticmethod
    def rewrite_record(record: logging.LogRecord):
        "Rewrite record"
        if not BraceFormatStyleFormatter.is_brace_format_style(record):
            return

        msg = record.msg
        msg = msg.replace("{", "_{{")
        msg = msg.replace("}", "_}}")
        placeholder_count = 0
        # add ANSI escape code for next alternating color before each formatting parameter
        # and reset color after it.
        while True:
            if "_{{" not in msg:
                break
            color_index = placeholder_count % len(ColorizedArgsFormatter.arg_colors)
            color = ColorizedArgsFormatter.arg_colors[color_index]
            msg = msg.replace("_{{", color + "{", 1)
            msg = msg.replace("_}}", "}" + ColorCodes.reset, 1)
            placeholder_count += 1

        record.msg = msg.format(*record.args)
        record.args = []

    def format(self, record):
        "Format record"
        orig_msg = record.msg
        orig_args = record.args
        formatter = self.level_to_formatter.get(record.levelno)
        self.rewrite_record(record)
        formatted = formatter.format(record)

        # restore log record to original state for other handlers
        record.msg = orig_msg
        record.args = orig_args
        return formatted


class BraceFormatStyleFormatter(logging.Formatter):
    "BraceFormatStyleFormatter"

    def __init__(self, fmt: str):
        super().__init__()
        self.formatter = logging.Formatter(fmt)

    @staticmethod
    def is_brace_format_style(record: logging.LogRecord):
        "Check if style is brace format"

        if len(record.args) == 0:
            return False

        msg = record.msg
        if "%" in msg:
            return False

        count_of_start_param = msg.count("{")
        count_of_end_param = msg.count("}")

        if count_of_start_param != count_of_end_param:
            return False

        if count_of_start_param != len(record.args):
            return False

        return True

    @staticmethod
    def rewrite_record(record: logging.LogRecord):
        "Rewrite record"

        if not BraceFormatStyleFormatter.is_brace_format_style(record):
            return

        record.msg = record.msg.format(*record.args)
        record.args = []

    def format(self, record):
        "Format record"

        orig_msg = record.msg
        orig_args = record.args
        self.rewrite_record(record)
        formatted = self.formatter.format(record)

        # restore log record to original state for other handlers
        record.msg = orig_msg
        record.args = orig_args
        return formatted
