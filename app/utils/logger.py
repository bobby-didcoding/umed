# --------------------------------------------------------------
# Python imports
# --------------------------------------------------------------
import copy
import errno
import logging
import os
import re
import threading
from datetime import datetime
from logging.handlers import RotatingFileHandler
from uuid import uuid4

# --------------------------------------------------------------
# 3rd party imports
# --------------------------------------------------------------
import arrow
from pythonjsonlogger import jsonlogger


"""
https://docs.python.org/3/howto/logging-cookbook.html#context-info
Python's cookbook suggests to use LoggerAdapters to impart contextual information, but this information is attached to 
individual logger. Some disadvantages:
 - we can pass extra parameters only during LoggerAdapter creation, it cuts down the possible list of parameters
 - errors/exceptions from not-our application (django, GBG client and other external apis) will not include extra
   information that was specified in LoggerAdapter
 - if we would like to keep separate applications (authentication, external_apis, frontend_api, payment_api) in logger  
   settings (apps could require different log level), then it will be required to create separate adapters for each 
   logger instance (with the same extra parameters)


As opposite to LoggerAdapter we will use "shared resource" (something similar to "Mapped Diagnostic Context", the concept  
that was taken from Java), it should allow us to add (just once, for all loggers) some contextual information to our  
logging output. For example, we can set unique requestId in middleware (before processing the request) and all loggers  
will output log information that will contain requestId as extra-parameter. Some links:
https://logback.qos.ch/manual/mdc.html
https://gist.github.com/mdaniel/8347533

Use examples:
1) General extra parameters
logger.info("Started schedule processing", extra={'scheduleId': schedule.id})

will produce:
{
  "message": "Started schedule processing",
  "data": {
    "scheduleId": "78e6cce6-7fb7-412c-9401-4b10593e9017"
  },
  "requestId": "cc23f0d2-cc73-435d-ad43-34d787265530",
  "customer": {
    "userId": "c8df3b60-0c90-41b2-80c6-2521d850c392",
    "accountId": "65717684-0101-4800-8dcd-d14d11d6ea11"
  },
  "dateCreated": "2019-09-12T14:28:32.482646",
  "level": "INFO",
  "duration": 292,
  "app": {
    "name": "frontend_api",
    "threadName": "Thread-2"
  }
}

2) "logGlobalDuration" parameter will make sure that we add "duration" property (time from the start of request 
processing) to log record 

logger.info("Response details ...", extra={'logGlobalDuration': True})

"""
logging._shared_extra = threading.local()


class coreLogger(logging.Logger):
    def __init__(self, *args, **kwargs):
        super(coreLogger, self).__init__(*args, **kwargs)
        self.addFilter(SensitiveDataObfuscatorFilter())

    def makeRecord(self, name, level, fn, lno, msg, args, exc_info, func=None, extra=None, sinfo=None):
        if extra is not None:
            # Based on required format we need to make sure that any extra information is placed in "data" section.
            extra = {'data': extra}

        return super(coreLogger, self).makeRecord(name, level, fn, lno, msg, args, exc_info, func, extra, sinfo)


class BetterRotatingFileHandler(RotatingFileHandler):
    def _open(self):
        self._ensure_dir(os.path.dirname(self.baseFilename))
        return logging.handlers.RotatingFileHandler._open(self)

    def _ensure_dir(self, path):
        # type: (AnyStr) -> None
        """os.path.makedirs without EEXIST."""
        try:
            os.makedirs(path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise


class coreJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(coreJsonFormatter, self).add_fields(log_record, record, message_dict)

        # Map all shared_extra params to root level
        # @NOTE: we cannot map shared_extra in coreLogger, because not all loggers are coreLogger,
        # so there is a risk to lost this information in log record
        shared_extra = logging.get_shared_extra()
        if len(shared_extra) > 0:
            current_data = {'data': copy.deepcopy(log_record.get('data', {}))}
            shared_extra = copy.deepcopy(shared_extra)
            shared_extra = {**shared_extra, **current_data}
            log_record.update(shared_extra)

        if not log_record.get('dateCreated'):
            now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')
            log_record['dateCreated'] = now

        if log_record.get('level'):
            log_record['level'] = log_record['level'].upper()
        else:
            log_record['level'] = record.levelname

        if log_record.get('startProcessingTimer'):
            if not log_record.get('duration') and log_record.get('data', {}).get('logGlobalDuration'):
                log_record['duration'] = log_record['startProcessingTimer'].duration()
                del(log_record['data']['logGlobalDuration'])

            del(log_record['startProcessingTimer'])

        log_record['app'] = {
            'name': 'core',
            "threadName": record.threadName
        }

        self._move_unexpected_params_to_data(log_record)

    # We move some unexpected parameters (like request, status_code, exc_info, stack_info) to "data" section
    def _move_unexpected_params_to_data(self, log_record):
        top_level_attributes = ['dateCreated', 'level', 'duration', 'message', 'requestId', 'customer', 'app', 'data']
        for key, _ in log_record.copy().items():
            if key not in top_level_attributes:
                if not log_record.get('data'):
                    log_record['data'] = {}

                log_record['data'][key] = log_record.get(key)
                del(log_record[key])


class SensitiveDataObfuscatorFilter(logging.Filter):
    _placeholder = '***'
    _patterns = {
        # IBANs, for example:
        # "iban":"DE05202208445090025780", \"iban\":\"DE05202208445090025780\", "feeIban": "DE05202208445090025780"
        # "DE05202208445090025780" => "DE0***780"
        re.compile(r'(\\?\"\w*iban\\?\":\s?\\?\".{3})(.*?)(\w{3}\\?\")', re.IGNORECASE):
            f'\g<1>{_placeholder}\g<3>',
        re.compile(r'(\\?\"ibanGeneralPart\\?\":\s?\\?\")(.*?)(\w{3}\\?\")', re.IGNORECASE):
            f'\g<1>{_placeholder}\g<3>',

        # Funding sources details, for example:
        # "bic":"SXPADAH", \"bic\":\"SXPADAH\", "accountNumber": "3244334"
        # "SXPADAH" => "SX***"
        re.compile(r'(\\?\"(?:bic|accountNumber|sortCode|expYear|lastDigits)\\?\":\s?\\?\"\w{2})(.*?)(\\?\")', re.IGNORECASE):
            f'\g<1>{_placeholder}\g<3>',

        # Personal information, for example:
        # "email": "dev_verified@mailinator.com", "fullName": "Christopher Hurst", "driver_licence_postcode": "B18888"
        # "dev_verified@mailinator.com" => "***"
        re.compile(r'(\\?\"(?:\w*email|\w*name|password|phone_number|address\w*|city|locality|postcode|birth_date|driver_licence\w*|\w*token)\\?\":\s?\\?\")(.*?)(\\?\")', re.IGNORECASE):
            f'\g<1>{_placeholder}\g<3>'
    }

    def filter(self, record):
        if hasattr(record, 'args'):
            record.args = self.obfuscate(record.args)
        if hasattr(record, 'data'):
            record.data = self.obfuscate(record.data)

        return True

    def obfuscate(self, data):
        if isinstance(data, str):
            for pattern, replace in self._patterns.items():
                data = pattern.sub(replace, data)
        elif isinstance(data, dict):
            for k in data.keys():
                data[k] = self.obfuscate(data[k])

        return data


class RequestIdGenerator:
    @staticmethod
    def get() -> str:
        return str(uuid4())


class Timer:
    def __init__(self):
        self._start = arrow.utcnow()

    def __str__(self):
        return self._start

    def duration(self):
        return int((arrow.utcnow() - self._start).microseconds / 1000)


def set_shared_extra(attributes: dict):
    for key, value in attributes.items():
        setattr(logging._shared_extra, key, value)


logging.set_shared_extra = set_shared_extra
del set_shared_extra


def init_shared_extra(request_id=None):
    logging.set_shared_extra({
        'requestId': request_id if request_id else RequestIdGenerator.get(),
        'startProcessingTimer': Timer()
    })


logging.init_shared_extra = init_shared_extra
del init_shared_extra


def get_shared_extra() -> dict:
    results = {}
    for x in dir(logging._shared_extra):
        if x.startswith('__'):
            continue
        results[x] = getattr(logging._shared_extra, x)

    return results


logging.get_shared_extra = get_shared_extra
del get_shared_extra


def get_shared_extra_param(key: str):
    return logging.get_shared_extra().get(key, None)


logging.get_shared_extra_param = get_shared_extra_param
del get_shared_extra_param

