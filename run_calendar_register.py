import requests

""" 
캘린더 고유 번호를 등록하는 기능 ( 일주일 마다 만료됨. )
crontab - 매일 12에서 갱신하도록 설정.
"""

res = requests.get('https://google-calendar-slack.orotcode.com/slack/authorize?user_id=U03MXBND80Y')
print(res)
access_token = res.json()['data']['access_token']

headers = {
    "Authorization": "Bearer {}".format(access_token),
    'Content-Type': 'application/json'
}
data = {
    'id': 'U03MXBND80Y',
    'type': 'web_hook',
    'address': 'https://google-calendar-slack.orotcode.com/slack/watch/callback'
}
re = requests.post(
    'https://www.googleapis.com/calendar/v3/calendars/dev@orotcode.com/events/watch',
    json=data,
    headers=headers
)

print("access_token: ", access_token)
print(re.json())
