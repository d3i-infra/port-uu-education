"""
Contains classes to deal with input validation of DDPs
"""
from dataclasses import dataclass, field
from enum import Enum

import logging

logger = logging.getLogger(__name__)


class Language(Enum):
    """ Languages Enum """
    EN = 1
    NL = 2


class DDPFiletype(Enum):
    """ Filetype Enum """
    JSON = 1
    HTML = 2
    CSV = 3
    TXT = 4


@dataclass
class DDPCategory:
    """
    Characteristics that characterize a DDP
    """
    id: str | None = None
    ddp_filetype: DDPFiletype | None = None
    language: Language | None = None
    known_files: list[str] | None = None


@dataclass
class StatusCode:
    """
    Can be used to set a DDP status
    """
    id: int
    description: str
    message: str


@dataclass
class ValidateInput:
    """
    Class containing the results of input validation

    A validation class to store the result of the validation

    status_codes: a list of all StatusCode's that are possible for a specific platform
    ddp_categories: a list of all DDPCategory's that are possible for a specific platform
    status_code: the status code of a submission after validation
    ddp_category: the inferred DDP category after validation
    """

    status_codes: list[StatusCode]
    ddp_categories: list[DDPCategory]
    status_code: StatusCode = StatusCode(-1, description="DDP not validated", message="")
    ddp_category: DDPCategory = DDPCategory()

    ddp_categories_lookup: dict[str, DDPCategory] = field(init=False)
    status_codes_lookup: dict[int, StatusCode] = field(init=False)

    def set_status_code(self, id: int) -> None:
        """
        Set the status code according to a StatusCode id
        """
        self.status_code = self.status_codes_lookup[id]

    def set_ddp_category(self, id: str) -> None:
        """
        Set the ddp_category code according to a DDPCategory id
        """
        self.ddp_category = self.ddp_categories_lookup[id]

    def infer_ddp_category(self, file_list_input: list[str]) -> bool:
        """
        Compares a list of filenames to a list of known filenames.

        From that comparison infer the DDP Category
        Note: at least 5% percent of known files should match
        """
        prop_category = {}
        for identifier, category in self.ddp_categories_lookup.items():
            n_files_found = [
                1 if f in category.known_files else 0 for f in file_list_input
            ]
            prop_category[identifier] = sum(n_files_found) / len(category.known_files) * 100
            logger.debug("propertion of ddp categories: %s", prop_category)

        if max(prop_category.values()) >= 5:
            highest = max(prop_category, key=prop_category.get)  # type: ignore
            self.ddp_category = self.ddp_categories_lookup[highest]
            logger.info("Detected DDP category: %s", self.ddp_category.id)
            return True

        logger.info("Not a valid input; not enough files matched when performing input validation")
        return False

    def __post_init__(self) -> None:
        for status_code, ddp_category in zip(self.status_codes, self.ddp_categories):
            assert isinstance(status_code, StatusCode), "Input is not of class StatusCode"
            assert isinstance(ddp_category, DDPCategory), "Input is not of class DDPCategory"

        self.ddp_categories_lookup = {
            category.id: category for category in self.ddp_categories
        }
        self.status_codes_lookup = {
            status_code.id: status_code for status_code in self.status_codes
        }
