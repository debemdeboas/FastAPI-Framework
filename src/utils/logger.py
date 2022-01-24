"""
Logger helper.

Creates logger objects on-demand for separate files with support for
frozen binaries (`exe` files).

Usage:
    from src.utils.logger import get_logger
    logger = get_logger(__name__)

Authors:
    Rafael Almeida de Bem - 19.11.2021
"""

from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from zlib import Z_BEST_COMPRESSION
import logging
import os
import sys
import time
import zipfile

formatter = logging.Formatter(
    '%(asctime)s %(name)s | %(module)s.%(funcName)s@%(lineno)d | %(levelname)s: %(message)s')


class CompressedTimedRotatingFileHandler(TimedRotatingFileHandler):
    """
    Custom log handler that compresses rotated log files.
    """

    def do_compress_rotated_file(self, file: str) -> None:
        """
        Compress a file.

        Args:
            file (str): File path

        Throws:
            BadZipFile: Invalid compressed file
        """
        if not os.path.isfile(file):
            return
        with zipfile.ZipFile(file + '.zip',
                             'w',
                             compression=zipfile.ZIP_DEFLATED,
                             compresslevel=Z_BEST_COMPRESSION) as zf:
            zf.write(file, os.path.basename(file))
            zf.testzip()  # Throws BadZipFile
        os.remove(file)

    def doRollover(self) -> None:
        """
        doRollover remux from `TimedRotatingFileHandler`.

        Adds compression functionality from a rolled-over file.
        """
        if self.stream:
            self.stream.close()
            self.stream = None
        # get the time that this sequence started at and make it a TimeTuple
        currentTime = int(time.time())
        dstNow = time.localtime(currentTime)[-1]
        t = self.rolloverAt - self.interval
        if self.utc:
            timeTuple = time.gmtime(t)
        else:
            timeTuple = time.localtime(t)
            dstThen = timeTuple[-1]
            if dstNow != dstThen:
                if dstNow:
                    addend = 3600
                else:
                    addend = -3600
                timeTuple = time.localtime(t + addend)
        dfn = self.rotation_filename(self.baseFilename[:-4] + '_' +
                                     time.strftime(self.suffix, timeTuple) +
                                     '.log')
        self.rotate(self.baseFilename, dfn)
        self.do_compress_rotated_file(dfn)
        if not self.delay:
            self.stream = self._open()
        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval
        # If DST changes and midnight or weekly rollover, adjust for this.
        if (self.when == 'MIDNIGHT'
                or self.when.startswith('W')) and not self.utc:
            dstAtRollover = time.localtime(newRolloverAt)[-1]
            if dstNow != dstAtRollover:
                if not dstNow:  # DST kicks in before next rollover, so we need to deduct an hour
                    addend = -3600
                else:  # DST bows out before next rollover, so we need to add an hour
                    addend = 3600
                newRolloverAt += addend
        self.rolloverAt = newRolloverAt


def get_logger(logger_name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Create the corresponding logger for the given file.

    Args:
        logger_name (str): Logger name (usually `__name__` or `__file__`)
        level (int, optional): Log level. Defaults to logging.INFO.

    Returns:
        Logger: Fresh logger right out of the factory.
    """
    if getattr(sys, 'frozen', False):
        log_path = os.path.join(os.path.dirname(sys.executable), 'log')
    else:
        log_path = 'log'

    if not os.path.isdir(log_path):
        os.mkdir(log_path)

    log_path = Path(f'{log_path}/{logger_name}.log')
    handler = CompressedTimedRotatingFileHandler(log_path,
                                                 when='W0')
    handler.setFormatter(formatter)

    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger
