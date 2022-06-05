import pytest
import db as db
import dotenv
from models import User, Counter


dotenv.load_dotenv()

@pytest.fixture()
def factory() -> str:
    return "4207097"

@pytest.fixture()
def user() -> User:
    return User(id="Cm5I1SQF3EJoa7AaNiH1dA==", name="Dmytro Tryfanenko")

@pytest.fixture()
def counter() -> Counter:
    import json
    repr = """
        {
            "counter_uuid": "f9317d1d-7faf-11e4-84f2-0007e98a1230",
            "counter_factory": "4207097",
            "current_value": "6180",
            "owner_name": "Богдан Денис Вікторович",
            "owner_uuid": "f6cfbe8b-3c56-44d5-b554-2b35f8b39187",
            "contract_uuid": "4f25b14e-820a-11e4-a4ba-000c2905aeea",
            "contract_number": "1000 = 32/1тс"
        }
     """
    return Counter.from_json(repr) 

def test_user(user:User) -> None:
    assert user.name == "Dmytro Tryfanenko" 


def test_fake_counter(counter: Counter) -> None:
    assert counter.current_value == '6180'


def test_save_counter(user: User, counter: Counter) -> None:
    res: Counter | None = db.update_or_if_not_create_counter(counter, user.id)
    assert res
