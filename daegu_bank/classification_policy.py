import re
from typing import List

from daegu_bank.mydata_row import MyDataRow


class ClassificationPolicy:
    _name = '<unnamed ClassificationPolicy>'
    _note_filter = []
    _note_regex = []

    _regex_list = None

    @classmethod
    def regex_list(cls):
        if cls._regex_list is None:
            cls._regex_list = [re.compile(regex) for regex in cls._note_regex]
        return cls._regex_list

    @classmethod
    def pass_filter(cls, row: MyDataRow) -> bool:
        for password in cls._note_filter:
            if row.note == password:
                return True
        for regex in cls.regex_list():
            if regex.match(row.note):
                return True
        return False

    @classmethod
    def name(cls) -> str:
        return cls._name


class IncomePolicy(ClassificationPolicy):
    @classmethod
    def name(cls) -> str:
        return 'I' + cls._name


class LossPolicy(ClassificationPolicy):
    @classmethod
    def name(cls) -> str:
        return 'L' + cls._name


class ClassificationModel:
    default_properties = {'__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__',
                          '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__',
                          '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__',
                          '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', 'get_policies',
                          'default_properties'}

    @classmethod
    def get_policies(cls) -> List[ClassificationPolicy]:
        return [getattr(cls, attr) for attr in set(dir(cls)).difference(cls.default_properties)]
