# -*- coding: utf-8 -*-

"""Models."""

__all__ = ['Model']

import abc
from types import FunctionType

from motor import motor_tornado

from .validators import (
    TypeValidator, RegexValidator, LenValidator, InValidator, OrValidator,
)

if 'MONGO_DB_SERVER' not in globals():
    MONGO_DB_SERVER = 'mongodb://localhost:27017/'


class Model(object):
    """An abstract db model."""
    __metaclass__ = abc.ABCMeta
    _db_con = motor_tornado.MotorClient(MONGO_DB_SERVER)

    fields = {}
    db_collection_name = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        for name, field in self.fields.items():
            if not hasattr(self, name):
                if 'default' in field:
                    setattr(self, name, Model._get_default(field))
                else:
                    raise TypeError(
                        '__init__() missing the required argument: %r' % name
                    )

    def __getitem__(self, key):
        """Return value for key if it is used like m['key']."""
        # only for the lulz
        return getattr(self, key)

    @classmethod
    def objects(cls):
        """Return the manager for this model."""
        return Model._db_con[cls.db_collection_name]

    def to_json(self, id_as_str=False):
        """
        Return a JSON serializable dict containing all data to be stored in db.

        id_as_str: hack, because mongodb needs a ObjectId but this is not JSON
                    serializable. -> For mongodb: False, for JSON: True
        """
        json_data = {
            name: getattr(self, name) for (name, field) in self.fields.items()
        }
        if hasattr(self, '_id'):
            json_data['_id'] = str(self['_id']) if id_as_str else self['_id']
        return json_data

    def save(self):
        """
        Save the object to database. Don't forget to save the ObjectId.

        Return: The ObjectId of this object in db.
                You might want to save it in this object like:
        >>> m._id = m.save()
        """
        return self.objects().insert(self.to_json())

    @classmethod
    def validate(cls, **kwargs):
        """Validate the kwargs and return cleaned data or raise a HTTPError."""
        data = {}
        for key, value in kwargs.items():
            if cls.fields[key].get('multiple'):
                values = value
                for validator in cls.fields[key].get('list_validators', []):
                    values = validator.validate(values)
            else:
                values = [value]

            for value in values:
                for validator in cls.fields[key]['validators']:
                    value = validator.validate(value)

            if cls.fields[key].get('multiple'):
                data[key] = values
            else:
                data[key] = values[0]
        return data

    @classmethod
    def create_from_request(cls, request_handler,
                            include_id=False, mapping=None, strip=True):
        """
        Create a object of this model out of an request.

        include_id: If this should edit an existing object,
                    accept the _id from the request
        mapping: dict: keys: model field name, value: request field name
        strip: strip values

        >>> my_obj = MyModel.create_from_request(self)
        >>> result = my_obj.save()
        """
        data = {}
        if not mapping:
            mapping = {}
        if include_id:
            data['_id'] = request_handler.get_argument('_id', strip=strip)
        for name, field in cls.fields.items():
            req_name = mapping.get(name, name)
            if field.get('multiple'):
                value = request_handler.get_arguments(
                    name=req_name, strip=strip
                )
            elif 'default' in field:
                value = request_handler.get_argument(
                    name=req_name, strip=strip,
                    default=Model._get_default(field),
                )
            else:
                value = request_handler.get_argument(
                    name=req_name, strip=strip
                )
            data[name] = value
        cleaned_data = cls.validate(**data)
        return cls(**cleaned_data)

    @staticmethod
    def _get_default(field):
        """Helper method to return the default value of a field."""
        if isinstance(field['default'], FunctionType):
            return field['default']()
        else:
            return field['default']
