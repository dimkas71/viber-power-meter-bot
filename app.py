import logging
import re
from os import environ
from typing import List

import dotenv
from flask import Flask, Response, request
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.viber_requests import (ViberConversationStartedRequest,
                                         ViberFailedRequest,
                                         ViberMessageRequest,
                                         ViberSubscribedRequest,
                                         ViberUnsubscribedRequest)

import handlers
import service
from keyboards import (start_keyboard)
from models import Counter
from text_messages import COUNTER_NUMBER_AND_VALUE_MESSAGE
from utils import parse

dotenv.load_dotenv()

app = Flask(__name__)
viber = Api(BotConfiguration(
    name='powermeterkalinkabot',
    avatar='http://site.com/avatar.jpg',
    auth_token=environ.get('TOKEN')
))


# region
def default_message_handler(viber_request: ViberMessageRequest):
    viber.send_messages(viber_request.sender.id, [
        TextMessage(
            text=COUNTER_NUMBER_AND_VALUE_MESSAGE,
            keyboard=start_keyboard)
    ])


# endregion

def on_add_value(viber_request: ViberMessageRequest, message: str):
    respond_message = ""
    try:
        counter_factory, value = parse(message)
        loaded_counters: List[Counter] = service.search_by_number(counter_factory)
        counters = list(filter(lambda counter: counter.counter_factory == counter_factory, loaded_counters))

        if not counters:
            respond_message = f"""*ПОМИЛКА*
            Лічильник з номером {counter_factory} не знайдено. Дані по лічильнику не додано
            """
            raise ValueError(f"Counter {counter_factory} not found")
        if counters[0].current_value > value:
            respond_message = f"""
            *ПОМИЛКА* Поточні показники лічильника *{counters[0].current_value}* > *{value}* більші за введені Дані по лічильнику не додано. Повторіть спробу.
            """.strip()
            raise ValueError(f"Bad counter value: {value}")
        respond_message = f"""
        *ПОКАЗНИКИ ЛІЧИЛЬНИКА ДОДАНО УСПІШНО*
        """
        if not service.add_counter_value(counters[0].counter_uuid, value):
            respond_message = f"""
                *ВНУТРІШНЯ ПОМИЛКА СЕРВЕРА* Дані по лічильнику {counter_factory} не додано. Поточне значення показника *{counters[0].current_value}*.Повторіть спробу 
            """
            raise ValueError(f"Internal error at adding counter's value")



    except ValueError as er:
        print(er)
    finally:
        viber.send_messages(
            viber_request.sender.id,
            [
                TextMessage(
                    text=respond_message,
                    keyboard=start_keyboard
                )
            ]
        )

@app.route('/', methods=['POST'])
def incoming():
    logging.debug("received request. post data: {0}".format(request.get_data()))
    # every viber message is signed, you can verify the signature using this method
    if not viber.verify_signature(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
        return Response(status=403)

    # this library supplies a simple way to receive a request object
    viber_request = viber.parse_request(request.get_data())
    if isinstance(viber_request, ViberMessageRequest):
        message = viber_request.message
        logging.info(message)
        if re.search(":", message.text):
            on_add_value(viber_request, message.text)
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
    logging.basicConfig(level=logging.INFO)
    context = ('server.crt', 'server.key')
    app.run(host='127.0.0.1', port=4443, debug=True, ssl_context=context)
