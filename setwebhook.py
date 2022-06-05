#sethook
from os import environ
import requests
import json
import dotenv

dotenv.load_dotenv()

auth_token = environ.get('TOKEN') # тут ваш токен полученный в начале #п.2
hook = 'https://chatapi.viber.com/pa/set_webhook'
headers = {'X-Viber-Auth-Token': auth_token}


sen = dict(url=environ.get('WEB_HOOK_ADDRESS'),
           event_types = ['subscribed', 'unsubscribed', 'conversation_started', 'message', 'seen', 'delivered', 'failed'])
# sen - это body запроса для отправки к backend серверов viber
#seen, delivered - можно убрать, но иногда маркетологи хотят знать,
#сколько и кто именно  принял и почитал ваших сообщений,  можете оставить)
if __name__ == '__main__':
    r = requests.post(hook, json.dumps(sen), headers=headers)
    # r - это пост запрос составленный по требованиям viber 
    print(r.json())
    #   в ответном print мы должны увидеть "status_message":"ok" - и это значит,
    #  что вебхук установлен