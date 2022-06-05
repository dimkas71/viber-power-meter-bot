from urllib import response
import requests
import logging
import json

from os  import environ

from typing import List
from models import Counter, HistoryCounterValue

def search_by_uuid(uuid: str) -> Counter | None:
    response = requests.get(f"{environ.get('API_BASE_URL')}/list", auth=(environ.get('API_USER'), environ.get('API_PASSWORD')))
    
    if response.status_code == 200:
        counters: List[Counter] = Counter.schema().loads(response.content, many=True)
        filtered_list: List[Counter] = list(filter(lambda counter: counter.counter_uuid == uuid, counters))
        return filtered_list[0] if filtered_list else None

    return None    

def search_by_number(number: str) -> List[Counter]:
    params = {"number":number}
    
    response = requests.get(f"{environ.get('API_BASE_URL')}/search",
                             params=params,
                             auth=(environ.get('API_USER'), environ.get('API_PASSWORD')))

    if response.status_code == 200:
        return Counter.schema().loads(response.content, many=True)
    else:
        return []  

def search_by_contract(contract: str) -> List[Counter]:
    response = requests.get(f"{environ.get('API_BASE_URL')}/list", auth=(environ.get('API_USER'), environ.get('API_PASSWORD')))

    if response.status_code == 200:
        counters: List[Counter] = Counter.schema().loads(response.content, many=True)
        return list(filter(lambda ci: ci.contract_number.startswith(contract), counters))
    else:
        return []    

def last_counter_value(counter_uuid: str) -> int | None:
    params = {'uuid': counter_uuid}
    response = requests.get(f"{environ.get('API_BASE_URL')}/history", params=params, auth=(environ.get('API_USER'), environ.get('API_PASSWORD')))
    if response.status_code == 200:
        values: List[HistoryCounterValue] = HistoryCounterValue.schema().loads(response.content, many=True)
        if values:
            return values[::-1][0].value    
    return None  

def add_counter_value(counter_uuid: str, new_value: int) -> bool:
    data = {'uuid': counter_uuid, 'value': new_value}
    response = requests.post(f"{environ.get('API_BASE_URL')}/add",
                    auth=(environ.get('API_USER'),environ.get('API_PASSWORD')),
                    data=json.dumps(data))

    if response.status_code != 200:
        return False
    return True                           
