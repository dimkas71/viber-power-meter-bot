from cgitb import text
import logging
import db

import dotenv

import handlers
from models import Counter
import service
import keyboards

import re
import json

from typing import List
from os import environ

from flask import Flask, Response, request
from statemachine import State, StateMachine
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages import VideoMessage
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.messages.url_message import URLMessage
from viberbot.api.viber_requests import (ViberConversationStartedRequest,
                                         ViberFailedRequest,
                                         ViberMessageRequest,
                                         ViberSubscribedRequest,
                                         ViberUnsubscribedRequest)


from keyboards import (AB_ADD_POWER_METER_CMD, AB_ADD_POWER_METER_BY_CONTRACT_CMD, AB_ADD_POWER_METER_VALUE_CMD, AB_HELP_CMD, AB_MAIN_MENU_CMD, AB_DELETE_POWER_METER_CMD, create_keyboard_on_counter, main_menu_keyboard,
                       to_main_menu_keyboard)

dotenv.load_dotenv()

app = Flask(__name__)
viber = Api(BotConfiguration(
    name='powermeterkalinkabot',
    avatar='http://site.com/avatar.jpg',
    auth_token=environ.get('TOKEN')
))

class MenuWorkflowMachine(StateMachine):
    main_menu = State('main_menu', initial=True)
    add_power_meter = State('add_power_meter')
    delete_power_meter =State('delete_power_meter')
    add_power_meter_value = State('add_power_meter_value')
    add_power_meter_by_contract = State('add_power_meter_by_contract')
    help = State('help')

    from_main = main_menu.to(add_power_meter) | main_menu.to(delete_power_meter) | main_menu.to(add_power_meter_value) \
        | main_menu.to(help) | main_menu.to(add_power_meter_by_contract)
    to_help = main_menu.to(help) | help.to.itself() 
    to_add_power_meter = main_menu.to(add_power_meter) | add_power_meter.to.itself()
    to_add_power_meter_value = main_menu.to(add_power_meter_value) | add_power_meter_value.to.itself()

    to_delete_power_meter = main_menu.to(delete_power_meter) | delete_power_meter.to.itself()
    
    to_add_power_meter_by_contract = main_menu.to(add_power_meter_by_contract) | add_power_meter_by_contract.to.itself()  
    to_main = help.to(main_menu) | main_menu.to.itself() | add_power_meter.to(main_menu) \
         | add_power_meter_by_contract.to(main_menu) | delete_power_meter.to(main_menu) | add_power_meter_value.to(main_menu)

WORKFLOW = MenuWorkflowMachine(start_value='main_menu')

#region
def on_add_power_meter_cmd(viber_request: ViberMessageRequest):
    viber.send_messages(
        viber_request.sender.id
        ,
        [
            TextMessage(text="""
                Введіть номер лічильника:
                Номер лічильника повинен задаватись у форматі
                ХХХХХ, де Х \- це цифра\. *Не менш ніж 7 символів*
            """, keyboard=to_main_menu_keyboard)            
        ]
    )
def on_delete_power_meter_cmd(viber_request: ViberMessageRequest):
    counters = db.counter_info_by_user(viber_request.sender.id)
    viber.send_messages(
        viber_request.sender.id,
        [
            TextMessage(text="Виберіть лічильник:",keyboard=create_keyboard_on_counter(counters))
        ]
    ) 

def on_add_power_meter_value_cmd(viber_request: ViberMessageRequest):
    counters = db.counter_info_by_user(viber_request.sender.id)
    viber.send_messages(
        viber_request.sender.id,
        [
            TextMessage(text="Виберіть лічильник:",keyboard=create_keyboard_on_counter(counters))
        ]
    ) 


def on_add_power_meter_by_contract_cmd(viber_request: ViberMessageRequest):
    viber.send_messages(
        viber_request.sender.id,
        [
            TextMessage(text="""
            Введіть номер торгового об'єкту:
            Наприклад: *123 А* або *34 =*...
            """, keyboard=to_main_menu_keyboard)
        ]
    )

def on_help_cmd(viber_request: ViberMessageRequest):
    viber.send_messages(viber_request.sender.id,
        [
            TextMessage(text="""
                Розділ *допомога* знаходиться у розробці
            """
            , keyboard=to_main_menu_keyboard)
        ]
    )

def on_add_power_meter_factory_cmd(viber_request: ViberMessageRequest, number: str):
    ci: List[Counter] = service.search_by_number(number)
    
    try:
        viber.send_messages(viber_request.sender.id,
                                    [
                                        TextMessage(text="Виберіть лічильник:", keyboard=keyboards.create_keyboard_on_counter(ci))
                                    ]
        )
    except Exception as e:
        viber.send_messages(viber_request.sender.id,
                                    [
                                        TextMessage(text="Кількість вибраних лічильників перевищує ліміт, спробуйте уточнити пошук", keyboard=keyboards.to_main_menu_keyboard)
                                    ]
        )
def on_add_power_meter_factory_choosen_cmd(viber_request: ViberMessageRequest, counter_uuid: str):
    counter: Counter = service.search_by_uuid(counter_uuid)
    if counter:
        updated_counter = db.update_or_if_not_create_counter(counter, viber_request.sender.id)
        if updated_counter:
            viber.send_messages(viber_request.sender.id,
                [
                    TextMessage(text=f"Ваш лічильник було додано в базу данних", keyboard=to_main_menu_keyboard)
                ]   
            )
        else:
            viber.send_messages(viber_request.sender.id,
            [
                TextMessage(text=f"Виникли помилки про додаванні лічильника, спробуйте ще раз..", keyboard=to_main_menu_keyboard)
            ]    
        )        
    else:
        viber.send_messages(viber_request.sender.id,
            [
                TextMessage(text=f"Виникли помилки про додаванні лічильника, спробуйте ще раз..", keyboard=to_main_menu_keyboard)
            ]    
        )    

def on_add_power_meter_value_factory_choosen_cmd(viber_request: ViberMessageRequest, counter_uuid: str):
    value = service.last_counter_value(counter_uuid=counter_uuid) or 0
    viber.send_messages(
        viber_request.sender.id,
        [
                TextMessage(text=f"""
                    Поточне значення показника = *{value}*
                    Введіть значення показника:
                """, keyboard=to_main_menu_keyboard,tracking_data=counter_uuid)
        ]
    )
def on_add_power_meter_value_add_cmd(viber_request: ViberMessageRequest, new_value: str, counter_uuid: str):
    result = service.add_counter_value(counter_uuid, new_value)
    if result: 
        viber.send_messages(
            viber_request.sender.id,
            [
                TextMessage(text="Показники лічильника додано успішно",keyboard=to_main_menu_keyboard)
            ]
        )
    else:
        viber.send_messages(
            viber_request.sender.id,
            [
                TextMessage(text="Не вдалось записати показники, попробуйте ще раз.",keyboard=to_main_menu_keyboard)
            ]
        )    
def on_delete_power_meter_factory_choosen_cmd(viber_request: ViberMessageRequest, counter_uuid: str):
    success: bool = db.delete_counter(viber_request.sender.id, counter_uuid)  
    if success:
        viber.send_messages(
            viber_request.sender.id,
            [
                TextMessage(text="Лічильник успішно вилучено...", keyboard=to_main_menu_keyboard)
            ]
        )      
    else:
            viber.send_messages(
            viber_request.sender.id,
            [
                TextMessage(text="""
                    Виникли помилки при вилученні лічильника.
                    Спробуйте ще раз."""
                , keyboard=to_main_menu_keyboard)
            ]
        )      

def on_add_power_meter_by_contract_number_cmd(viber_request: ViberMessageRequest, contract: str):
    ci: List[Counter] = service.search_by_contract(contract)
    
    try:
        viber.send_messages(viber_request.sender.id,
                                    [
                                        TextMessage(text="Виберіть лічильник:", keyboard=keyboards.create_keyboard_on_counter(ci))
                                    ]
        )
    except Exception as e:
        viber.send_messages(viber_request.sender.id,
                                    [
                                        TextMessage(text="Кількість вибраних лічильників перевищує ліміт, спробуйте уточнити пошук", keyboard=keyboards.to_main_menu_keyboard)
                                    ]
        )

def on_main_menu_cmd(viber_request: ViberMessageRequest):
    default_message_handler(viber_request)  


def default_message_handler(viber_request: ViberMessageRequest):
     viber.send_messages(viber_request.sender.id, [
                TextMessage(text="Виберіть дію:", keyboard=main_menu_keyboard)
            ])

#endregion

@app.route('/', methods=['POST'])
def incoming():
    logging.debug("received request. post data: {0}".format(request.get_data()))
    # every viber message is signed, you can verify the signature using this method
    if not viber.verify_signature(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
        return Response(status=403)

    # this library supplies a simple way to receive a request object
    viber_request = viber.parse_request(request.get_data())
    #print(f"Raw request {viber_request}")
    if isinstance(viber_request, ViberMessageRequest):
        message = viber_request.message



        if isinstance(message, TextMessage) and message.text == AB_ADD_POWER_METER_CMD:
        
            WORKFLOW.run('to_add_power_meter')
            on_add_power_meter_cmd(viber_request)

        elif isinstance(message, TextMessage) and message.text == AB_ADD_POWER_METER_VALUE_CMD:
            
            WORKFLOW.run('to_add_power_meter_value')
            on_add_power_meter_value_cmd(viber_request)    

        elif isinstance(message, TextMessage) and message.text == AB_ADD_POWER_METER_BY_CONTRACT_CMD:
            WORKFLOW.run('to_add_power_meter_by_contract')
            on_add_power_meter_by_contract_cmd(viber_request)    
        
        elif isinstance(message, TextMessage) and message.text == AB_DELETE_POWER_METER_CMD:
            WORKFLOW.run('to_delete_power_meter')
            on_delete_power_meter_cmd(viber_request)

        elif isinstance(message, TextMessage) and message.text == AB_HELP_CMD:

            WORKFLOW.run('to_help') 
            on_help_cmd(viber_request)   

        elif isinstance(message, TextMessage) and message.text == AB_MAIN_MENU_CMD:
            WORKFLOW.run('to_main')
            on_main_menu_cmd(viber_request)
        elif isinstance(message, TextMessage) and \
                        WORKFLOW.current_state == WORKFLOW.add_power_meter and \
                            re.search(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', message.text):
            counter_uuid = message.text
            on_add_power_meter_factory_choosen_cmd(viber_request, counter_uuid)
        elif isinstance(message, TextMessage) and \
                        WORKFLOW.current_state == WORKFLOW.add_power_meter_by_contract and \
                            re.search(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', message.text):
            counter_uuid = message.text
            on_add_power_meter_factory_choosen_cmd(viber_request, counter_uuid)
        elif isinstance(message, TextMessage) and \
                        WORKFLOW.current_state == WORKFLOW.add_power_meter_value and \
                            re.search(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', message.text):
            counter_uuid = message.text
            on_add_power_meter_value_factory_choosen_cmd(viber_request, counter_uuid)      
        elif isinstance(message, TextMessage) and \
                        WORKFLOW.current_state == WORKFLOW.delete_power_meter and \
                            re.search(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', message.text):
            counter_uuid = message.text
            on_delete_power_meter_factory_choosen_cmd(viber_request, counter_uuid)                         
        elif isinstance(message, TextMessage) and \
                        WORKFLOW.current_state == WORKFLOW.add_power_meter and \
                            re.search(r'\d{7,}', message.text):
            on_add_power_meter_factory_cmd(viber_request, message.text)
        elif isinstance(message, TextMessage) and \
                    WORKFLOW.current_state == WORKFLOW.add_power_meter_by_contract and \
                        re.search(r'\d{1,}', message.text):
            on_add_power_meter_by_contract_number_cmd(viber_request, message.text)
        elif isinstance(message, TextMessage) and \
            WORKFLOW.current_state == WORKFLOW.add_power_meter_value and \
                re.search(r'\d{1,}', message.text):
            on_add_power_meter_value_add_cmd(viber_request, message.text, message.tracking_data)                    
        else:
            if WORKFLOW.current_state == WORKFLOW.help:
                #Don't show anything. Just silent
                pass    
            else:
                default_message_handler(viber_request)
    
    elif isinstance(viber_request, ViberSubscribedRequest):
        handlers.on_user_subscribed(viber_request.user.id, viber_request.user.name)
        viber.send_messages(viber_request.user.id, [
            TextMessage(text='Thank you for subscribing')
        ])    
    elif isinstance(viber_request, ViberConversationStartedRequest):
        handlers.on_conversation_started(viber_request.user.id, viber_request.user.name)
    elif isinstance(viber_request, ViberUnsubscribedRequest):
        handlers.on_user_unsubscribed(viber_request.user_id)
          
    elif isinstance(viber_request, ViberFailedRequest):
        logging.warn("client failed receiving message. failure: {0}".format(viber_request))

    return Response(status=200)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    context = ('server.crt', 'server.key')
    app.run(host='127.0.0.1', port=4443, debug=True, ssl_context=context)
