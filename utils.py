import io
import os
import sys

import logging
import json
#import re
import sh

from pprint import pprint
from pathlib import Path

import ruamel.yaml
import jsonschema
from jsonschema import Draft202012Validator, validators



# =====================================================================
# Init
# =====================================================================

# Usage of get_logger:
# # In main app:
#   from paasify.common import get_logger
#   log, log_level = get_logger(logger_name="paasify")
# # In other libs:
#   import logging
#   log = logging.getLogger(__name__)

log = logging.getLogger(__name__)


# Setup YAML object
yaml = ruamel.yaml.YAML()
yaml.version = (1, 1)
yaml.default_flow_style = False
#yaml.indent(mapping=3, sequence=2, offset=0)
yaml.allow_duplicate_keys = True
yaml.explicit_start = True


# =====================================================================
# Logging helpers
# =====================================================================

# Source: https://stackoverflow.com/questions/2183233/how-to-add-a-custom-loglevel-to-pythons-logging-facility/35804945#35804945
def addLoggingLevel(levelName, levelNum, methodName=None):
    """
    Comprehensively adds a new logging level to the `logging` module and the
    currently configured logging class.

    `levelName` becomes an attribute of the `logging` module with the value
    `levelNum`. `methodName` becomes a convenience method for both `logging`
    itself and the class returned by `logging.getLoggerClass()` (usually just
    `logging.Logger`). If `methodName` is not specified, `levelName.lower()` is
    used.

    To avoid accidental clobberings of existing attributes, this method will
    raise an `AttributePaasifyError` if the level name is already an attribute of the
    `logging` module or if the method name is already present 

    Example
    -------
    >>> addLoggingLevel('TRACE', logging.DEBUG - 5)
    >>> logging.getLogger(__name__).setLevel("TRACE")
    >>> logging.getLogger(__name__).trace('that worked')
    >>> logging.trace('so did this')
    >>> logging.TRACE
    5

    """
    if not methodName:
        methodName = levelName.lower()

    if hasattr(logging, levelName):
       raise AttributePaasifyError('{} already defined in logging module'.format(levelName))
    if hasattr(logging, methodName):
       raise AttributePaasifyError('{} already defined in logging module'.format(methodName))
    if hasattr(logging.getLoggerClass(), methodName):
       raise AttributePaasifyError('{} already defined in logger class'.format(methodName))

    # This method was inspired by the answers to Stack Overflow post
    # http://stackoverflow.com/q/2183233/2988730, especially
    # http://stackoverflow.com/a/13638084/2988730
    def logForLevel(self, message, *args, **kwargs):

        if self.isEnabledFor(levelNum):
            # Monkey patch for level below 10, dunno why this not work
            lvl = levelNum if levelNum >= 10 else 10
            self._log(lvl, message, args, **kwargs)

    def logToRoot(message, *args, **kwargs):
        logging.log(levelNum, message, *args, **kwargs)

    logging.addLevelName(levelNum, levelName)
    setattr(logging, levelName, levelNum)
    setattr(logging.getLoggerClass(), methodName, logForLevel)
    setattr(logging, methodName, logToRoot)


class MultiLineFormatter(logging.Formatter):
    """Multi-line formatter."""
    def get_header_length(self, record):
        """Get the header length of a given record."""
        return len(super().format(logging.LogRecord(
            name=record.name,
            level=record.levelno,
            pathname=record.pathname,
            lineno=record.lineno,
            msg='', args=(), exc_info=None
        )))

    def format(self, record):
        """Format a record with added indentation."""
        indent = ' ' * self.get_header_length(record)
        head, *trailing = super().format(record).splitlines(True)
        return head + ''.join(indent + line for line in trailing)


def get_logger(logger_name=None, create_file=False, verbose=None):
    """Create CmdApp logger"""

    # Take default app name
    logger_name = logger_name or __name__

    # Manage logging level
    if not verbose:
        loglevel = logging.getLogger().getEffectiveLevel()
    else:
        try:
            loglevel = {
                0: logging.ERROR,
                1: logging.WARN,
                2: logging.INFO,
                3: logging.DEBUG,
            }[verbose]
        except KeyPaasifyError:
            loglevel = logging.DEBUG

    # Create logger for prd_ci
    log = logging.getLogger(logger_name)
    log.setLevel(level=loglevel)

    # Formatters
    format1 = "%(levelname)8s: %(message)s"
    format4 = "%(name)-32s%(levelname)8s: %(message)s"
    format2 = "%(asctime)s.%(msecs)03d|%(name)-16s%(levelname)8s: %(message)s"
    format3 = (
       "%(asctime)s.%(msecs)03d"
       + " (%(process)d/%(thread)d) "
       + "%(pathname)s:%(lineno)d:%(funcName)s"
       + ": "
       + "%(levelname)s: %(message)s"
    )
    tformat1 = "%H:%M:%S"
    #tformat2 = "%Y-%m-%d %H:%M:%S"
    #formatter = logging.Formatter(format4, tformat1)
    formatter = MultiLineFormatter(format1, tformat1)
    

    # Create console handler for logger.
    stream = logging.StreamHandler()
    stream.setLevel(level=logging.DEBUG)
    stream.setFormatter(formatter)
    log.addHandler(stream)

    # Create file handler for logger.
    if isinstance(create_file, str):
        handler = logging.FileHandler(create_file)
        handler.setLevel(level=logging.DEBUG)
        handler.setFormatter(formatter)
        log.addHandler(handler)

    #print (f"Fetch logger name: {logger_name} (level={loglevel})")

    # Return objects
    return log, loglevel


# =====================================================================
# Misc functions
# =====================================================================


def serialize(obj, fmt='json'):
    "Serialize anything, output json like compatible (destructive)"
    
    if fmt in ['yaml', 'yml']:
        # Serialize object in json first
        obj = json.dumps(obj, default=lambda o: str(o), indent=2)
        obj = json.loads(obj)

        # Convert json to yaml
        string_stream = io.StringIO()
        yaml.dump(obj, string_stream)
        output_str = string_stream.getvalue()
        string_stream.close()

        # Remove 2 first lines of output
        output_str = output_str.split("\n", 2)[2]
        return output_str
    else:
        obj = json.dumps(obj, default=lambda o: str(o), indent=2)
        return obj


def duplicates(_list):
    ''' Check if given list contains duplicates'''    
    known = set()
    duplicates = set()
    for item in _list:
        if item in known:
            duplicates.add(item)
        else:
            known.add(item)

    if len (duplicates) > 0:
        return list(duplicates)
    return []



def read_file(file):
    "Read file content"
    with open(file) as f:
        return ''.join(f.readlines())


def write_file(file, content):
    "Write content to file"

    file_folder = os.path.dirname(file)
    if not os.path.exists(file_folder):
        os.makedirs(file_folder)

    with open(file, 'w') as f:
        f.write(content)


def flatten(S):
    "Flatten any arrays nested arrays"
    if S == []:
        return S
    if isinstance(S[0], list):
        return flatten(S[0]) + flatten(S[1:])
    return S[:1] + flatten(S[1:])


# =====================================================================
# JSON Schema framework
# =====================================================================

def _extend_with_default(validator_class):
    validate_properties = validator_class.VALIDATORS["properties"]

    def set_defaults(validator, properties, instance, schema):
        for property, subschema in properties.items():
            if "default" in subschema:
                instance.setdefault(property, subschema["default"])

        for error in validate_properties(
            validator, properties, instance, schema,
        ):
            yield error

    return validators.extend(
        validator_class, {"properties" : set_defaults},
    )

DefaultValidatingValidator = _extend_with_default(Draft202012Validator)

def json_validate_defaults(schema, payload):
    "Validate dict against schema and set defaults"
    DefaultValidatingValidator(schema).validate(payload)
    return payload

def json_validate(schema, payload):
    "Validate dict against schema"
    jsonschema.validate(payload, schema)
    return payload

# =====================================================================
# Command Execution framework
# =====================================================================

def _exec(command, cli_args=None, logger=None, **kwargs):
    "Execute any command"

    # Check arguments
    cli_args = cli_args or []
    assert isinstance(cli_args, list), f"_exec require a list, not: {type(cli_args)}"

    # Prepare context
    sh_opts = {
        '_in': sys.stdin,
        '_out': sys.stdout,
    }
    sh_opts = kwargs or sh_opts

    # Bake command
    cmd = sh.Command(command)
    cmd = cmd.bake(*cli_args)

    # Log command
    if logger:
        cmd_line = [cmd.__name__ ] + [ x.decode('utf-8') for x in cmd._partial_baked_args]
        cmd_line = ' '.join(cmd_line)
        logger.exec (cmd_line)     # Support exec level !!!

    # Execute command via sh
    try:
        output = cmd(**sh_opts)
        return output

    except sh.ErrorReturnCode as err:
        #log.error(f"Error while running command: {command} {' '.join(cli_args)}")
        #log.critical (f"Command failed with message:\n{err.stderr.decode('utf-8')}")
        
        #pprint (err.__dict__)
        #raise error.ShellCommandFailed(err)
        #sys.exit(1)
        raise err

