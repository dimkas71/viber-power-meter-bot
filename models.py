from __future__ import annotations
from datetime import datetime, date

from typing import Any

from collections import namedtuple
from dataclasses import dataclass, asdict, field
from dataclasses_json import config, dataclass_json 
from marshmallow import fields


from json import JSONEncoder, dumps

CounterInfo = namedtuple('CounterInfo', 'counter_uuid, counter_factory, owner_name, contract_number')

@dataclass(frozen=True,slots=True)
class User:
    id: str
    name: str


@dataclass_json
@dataclass(frozen=True)
class HistoryCounterValue:
    value: int
    date: date

@dataclass_json
@dataclass(frozen=True, slots=True)
class Counter():
    counter_uuid: str = field(metadata=config(mm_field=fields.String()))
    counter_factory: str = field(metadata=config(mm_field=fields.String()))
    current_value: int = field(metadata=config(mm_field=fields.Integer()))
    owner_name: str = field(metadata=config(mm_field=fields.String()))
    owner_uuid: str = field(metadata=config(mm_field=fields.String()))
    contract_uuid: str = field(metadata=config(mm_field=fields.String()))
    contract_number: str = field(metadata=config(mm_field=fields.String()))

class CounterEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Counter):
            return obj.to_json()
        return JSONEncoder.default(self, obj)            
