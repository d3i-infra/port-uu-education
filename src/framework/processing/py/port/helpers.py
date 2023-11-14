from datetime import datetime, timezone
from typing import Any
import warnings
import math
import logging
import re

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

REGEX_ISO8601_FULL = r"^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$"
REGEX_ISO8601_DATE = r"^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])$"


def split_dataframe(df: pd.DataFrame, row_count: int) -> list[pd.DataFrame]:
    """
    Port has trouble putting large tables in memory. 
    Has to be expected. Solution split tables into smaller tables.
    I have tried non-bespoke table soluions they did not perform any better

    I hope you have an idea to make tables faster! Would be nice
    """
    # Calculate the number of splits needed.
    num_splits = int(len(df) / row_count) + (len(df) % row_count > 0)

    # Split the DataFrame into chunks of size row_count.
    df_splits = [df[i*row_count:(i+1)*row_count].reset_index(drop=True) for i in range(num_splits)]

    return df_splits


class CannotConvertEpochTimestamp(Exception):
    """"Raise when epoch timestamp cannot be converted to isoformat"""


def is_timestamp(input_string: str) -> bool:
    """
    Detects if string is a timestamp
    relies on pandas.to_datetime() to detect the time format
    """
    with warnings.catch_warnings():
        warnings.filterwarnings("error")  # temporary behaviour

        try:
            assert isinstance(input_string, str)
            assert input_string != ""
            assert input_string.isdigit() is False

            pd.to_datetime(input_string)

            logger.debug("timestamp FOUND in: '%s'", input_string)
            return True

        except (ValueError, AssertionError) as e:
            logger.debug("Timestamp NOT found in: '%s', %s", input_string, e)
            return False

        except Warning as e:
            logger.warning(
                "WARNING was raised as exception "
                "probably NO timestamp in: "
                "'%s', %s",
                input_string,
                e,
            )
            return False

        except Exception as e:
            logger.error(e)
            return False



def is_isoformat(
    datetime_str: list[str] | list[int], check_minimum: int, date_only: bool = False
) -> bool:
    """
    Check if list like object containing datetime stamps are ISO 8601 strings
    date_only = True, checks if only the date part is ISO 8601
    """

    regex = (
        REGEX_ISO8601_FULL
        if date_only is False
        else REGEX_ISO8601_DATE
    )

    try:
        for i in range(min(len(datetime_str), check_minimum)):
            if isinstance(datetime_str[i], int):
                logger.debug(
                    "Could not detect ISO 8601 timestamp (date_only=%s): %s",
                    date_only,
                    datetime_str[i],
                )
                return False

            if re.fullmatch(regex, datetime_str[i]) is None:  # type: ignore
                logger.debug(
                    "Could not detect ISO 8601 timestamp (date_only=%s): %s",
                    date_only,
                    datetime_str[i],
                )
                return False

    except Exception as e:
        logger.debug(
            "Could not detect ISO 8601 timestamp (date_only=%s): %s, error: %s",
            date_only,
            datetime_str[i],
            e
        )
        return False

    logger.debug("ISO 8601 timestamp detected (date_only=%s)", date_only)
    return True


def is_epoch(datetime_int: list[int] | list[str], check_minimum: int) -> bool:
    """
    Check if list-like object with ints or str that can be interpreted as ints
    epoch time (unit seconds) fall between the start of year 2000 and the year 2040
    """

    year2000 = 946684800
    year2040 = 2208988800

    try:
        for i in range(min(len(datetime_int), check_minimum)):
            check_time = int(datetime_int[i])
            if not year2000 <= check_time <= year2040:
                logger.debug("Could not detect epoch time timestamp: %s", check_time)
                return False

    except Exception as e:
        logger.debug("Could not detect epoch time timestamp, %s", e)
        return False

    logger.debug("Epoch timestamp detected")
    return True


def epoch_to_iso(epoch_timestamp: str | int) -> str:
    """
    Convert epoch timestamp to an ISO 8601 string. Assumes UTC.
    """

    out = str(epoch_timestamp)
    try:
        epoch_timestamp = int(epoch_timestamp)
        out = datetime.fromtimestamp(epoch_timestamp, tz=timezone.utc).isoformat()
        print(f"TIMESTAMP: {out}")
    except (OverflowError, OSError, ValueError, TypeError) as e:
        logger.error("Could not convert epoch time timestamp, %s", e)

    return out


def convert_datetime_str(datetime_str: list[str] | list[int]) -> pd.DatetimeIndex | None:
    """
    If timestamps are ISO 8601 return those
    If timestamps are ints (epochtime) return those

    If first ambigous non NaN timestamps is encoutered
    (and can be detected with infer_datetime_format=True and dayfirst-True)
    every timestamp is interpreted as DD/MM/YYYY if possible,
    if resulting in incorrect timestamp, then MM/DD/YYYY is used,
    converting format is silently switched

    If first non-ambigous non NaN timestamps is encoutered
    (and can be detected with infer_datetime_format=True and dayfirst-True)
    every timestamp is interpreted as either DD/MM/YYYY or MM/DD/YYYY depending on the first timestamp
    If the other format is encountered, that would result in an error, format is silently switched

    If timestamp format cannot be detected with infer_datetime_format
    dateutils.parser.parse() is used with dayfirst is true setting
    Interpretering everything as DD/MM/YYYY except if that results in an impossible date,
    then MM/DD/YYYY is used

    YYYY/MM/DD formats not ISO 8601 will be interpreted incorrectly, as YYYY/DD/MM if possible

    Note 1: to_datetime will be rewritten in a future pandas release
    Also to_datetime, guess_datetime_format will be made available in pandas.tools
    The silent format changes will be changed.

    Note 2: This is a very complicated problem to solve, solving this problem myself is too difficult
    for what I might expect to gain in accuracy

    Note 3: if time is converted from epoch utc is used

    Concluding: Although a lot can go wrong, I expect the impact will be minor,
    When american formats are encourted regularly things will go wrong most often
    """
    out = None
    try:
        if is_isoformat(datetime_str, 10):
            out = pd.to_datetime(datetime_str)

        elif is_isoformat(datetime_str, 10, date_only=True):
            out = pd.to_datetime(datetime_str)

        elif is_epoch(datetime_str, 10):
            out = pd.to_datetime(datetime_str, unit="s")

        else:
            out = pd.to_datetime(
                datetime_str, infer_datetime_format=True, dayfirst=True
            )

    except (ValueError, TypeError, OverflowError) as e:
        logger.error("Could not convert timestamps: %s", e)

    finally:
        return out


def dict_denester(
    inp: dict[Any, Any] | list[Any],
    new: dict[Any, Any] | None = None,
    name: str = "",
    run_first: bool = True,
) -> dict[Any, Any]:
    """
    Denest a dict or list, returns a new denested dict
    """

    if run_first:
        new = {}

    if isinstance(inp, dict):
        for k, v in inp.items():
            if isinstance(v, (dict, list)):
                dict_denester(v, new, f"{name}-{str(k)}", run_first=False)
            else:
                newname = f"{name}-{k}"
                new.update({newname[1:]: v})  # type: ignore

    elif isinstance(inp, list):
        for i, item in enumerate(inp):
            dict_denester(item, new, f"{name}-{i}", run_first=False)

    else:
        new.update({name[1:]: inp})  # type: ignore

    return new  # type: ignore



def find_items(d: dict[Any, Any],  key_to_match: str) -> str:
    """
    d is a denested dict
    match all keys in d that contain key_to_match

    return the value beloning to that key that is the least nested
    In case of no match return empty string

    example:
    key_to_match = asd

    asd-asd-asd-asd-asd-asd: 1
    asd-asd: 2
    qwe: 3

    returns 2

    This function is needed because your_posts_1.json contains a wide variety of nestedness per post
    """
    out = ""
    pattern = r"{}".format(f"^.*{key_to_match}.*$")
    depth = math.inf

    try:
        for k, v in d.items():
            if re.match(pattern, k):
                depth_current_match = k.count("-")
                if depth_current_match < depth:
                    depth = depth_current_match
                    out = str(v)
    except Exception as e:
        logger.error("bork bork: %s", e)

    return out



def sort_isotimestamp_empty_timestamp_last(timestamp_series: pd.Series) -> pd.Series:
    """
    Can be used as follows:

    df = df.sort_values(by="Date", key=sort_isotimestamp_empty_timestamp_last)
    """

    def convert_timestamp(timestamp):
        out = np.inf
        try:
            if isinstance(timestamp, str) and len(timestamp) > 0:
                dt = datetime.fromisoformat(timestamp)
                out = -dt.timestamp()
        except Exception as e:
            logger.debug("Cannot convert timestamp: %s", e)

        return out

    return timestamp_series.apply(convert_timestamp)



def fix_latin1_string(input: str) -> str:
    """
    Fixes the string encoding by attempting to encode it using the 'latin1' encoding and then decoding it.

    Args:
        input (str): The input string that needs to be fixed.

    Returns:
        str: The fixed string after encoding and decoding, or the original string if an exception occurs.
    """
    try:
        fixed_string = input.encode("latin1").decode()
        return fixed_string
    except Exception:
        return input
