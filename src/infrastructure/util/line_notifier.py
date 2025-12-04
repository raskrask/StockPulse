import requests
from infrastructure.config.settings import settings

class LineNotifier:
    def send(self, message: str) -> None:
        for to in settings.LINE_USER_IDS:
            url = 'https://api.line.me/v2/bot/message/push'

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {settings.LINE_ACCESS_TOKEN}',
            }

            body = {
                'to': to,
                'messages': [
                    {
                        'type': 'text',
                        'text': message,
                    },
                ],
            }

            try:
                res = requests.post(url, json=body, headers=headers)
                res.raise_for_status()
                print('LINE送信成功', res.json())
            except requests.exceptions.RequestException as error:
                print('LINE送信失敗', error)
                if error.response is not None:
                    print('>> details:', error.response.json())        

