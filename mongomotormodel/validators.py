# -*- coding: utf-8 -*-

"""Validators."""

__all__ = ['TypeValidator', 'RegexValidator', 'LenValidator', 'InValidator']

import re
import abc
from tornado.web import HTTPError


class Validator(object):
    """A validator."""

    def __init__(self, message=None):
        self.msg = message
        self.default_msg = ''


    @abc.abstractmethod
    def validate(self, data):
        """Run the validator and raise a HTTPError."""
        pass


class TypeValidator(Validator):
    """Convert data to type."""

    def __init__(self, dest_type, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dest_type = dest_type
        self.default_message = '{data} should be of {dest_type}'

    def validate(self, data):
        try:
            data = self.dest_type(data)
        except ValueError:
            raise HTTPError(
                400,
                (self.msg if self.msg else self.default_msg).format(
                    data=data, dest_type=self.dest_type.__name__,
                )
            )
        return data


class RegexValidator(Validator):
    """Validate data against a regexp."""

    def __init__(self, regexp, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.regex = re.compile(regexp)
        self.default_msg = '{data} contains illegal characters.'

    def validate(self, data):
        if not self.regex.match(data):
            raise HTTPError(
                400,
                (self.msg if self.msg else self.default_msg).format(
                    data=data, regexp=self.regex.pattern,
                )
            )
        return data


class LenValidator(Validator):
    """Validate the length of data."""
    def __init__(self, min_len=0, max_len=float('inf'), *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.min_len = min_len
        self.max_len = max_len
        self.default_msg = '{data} is too short or too long'

    def validate(self, data):
        if not self.min_len <= len(data) <= self.max_len:
            raise HTTPError(
                400,
                (self.msg if self.msg else self.default_msg).format(
                    data=data, min_len=self.min_len, max_len=self.max_len,
                )
            )
        return data


class InValidator(Validator):
    """Validate that data is an element of an iterable."""
    def __init__(self, iterable, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.iterable = iterable
        self.iterable_str = ', '.join((str(e) for e in iterable))
        self.default_msg = '{data} should be one of {iterable}'

    def validate(self, data):
        if data not in self.iterable:
            raise HTTPError(
                400,
                (self.msg if self.msg else self.default_msg).format(
                    data=data, iterable=self.iterable_str,
                )
            )
        return data


class OrValidator(Validator):
    """It's okay if only one of the validators validates."""
    def __init__(self, list_of_validators, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.list_of_validators = list_of_validators
        self.default_msg = 'None of the validators accepted the data'

    def validate(self, data):
        for validator in self.list_of_validators:
            try:
                validator.validate(data)
            except HTTPError:
                continue
            else:
                return data

        raise HTTPError(
            400,
            (self.msg if self.msg else self.default_msg).format(data=data)
        )
