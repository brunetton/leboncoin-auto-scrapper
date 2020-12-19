import re
import sys
from pathlib import Path
from typing import List, Optional, Union

from pydantic import AnyHttpUrl, BaseModel, conint, conlist, constr, validator

sys.path.append(str(Path(__file__).parent.absolute()))
from common import ensure_list

nonEmptyString = constr(min_length=1, strict=True)


class StrictModel(BaseModel):
    class Config:
        extra = 'forbid'


class Location(StrictModel):
    gps: nonEmptyString
    radius: conint(gt=10)

    @validator('gps')
    def extract_lon_lat(cls, v):
        match = re.search(r'(\d+(?:\.\d+)?), *(\d+(?:\.\d+)?)', v)
        if not match:
            raise ValueError(f'Unexpected gps coords format: {v!r}')
        return {'lat': float(match.group(1)), 'long': float(match.group(2))}


class Search(StrictModel):
    terms: Union[conlist(nonEmptyString, min_items=1), nonEmptyString]
    price: Optional[conlist(conint(ge=0), min_items=2, max_items=2)]
    location: Optional[Union[Location, conlist(Location, min_items=1)]]
    shippable: Optional[bool]

    @validator('price')
    def check_max_is_higher_than_min(cls, v):
        if not v[1] > v[0]:
            raise ValueError('Max price must be > min price')
        return {'min': v[0], 'max': v[1]}

    # validators
    _normalize_terms = validator('terms', allow_reuse=True)(ensure_list)
    _normalize_terms = validator('location', allow_reuse=True)(ensure_list)


Searches = List[Search]


class Config(BaseModel):
    searches: conlist(Search, min_items=1)
    sms_url: Optional[AnyHttpUrl]

    @validator('sms_url')
    def check_url_contains_brackets(cls, v):
        if not '{}' in v:
            raise ValueError("must contains \"{}\"")
        return v
