import requests
from api.slack.bot import post_error_message, post_calendar_subscribe_status_message
from flask import current_app
import traceback

if __name__ == '__main__':
    slack_token = "xoxb-3745296232272-4845927270291-uE78X8df2sNz6cC2MSfMsVlH"
    try:
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

        if res.status_code == 200:
            post_calendar_subscribe_status_message(slack_token, "구독중")
        else:
            post_calendar_subscribe_status_message(slack_token, "구독중 아님")

        print("access_token: ", access_token)
        print(re.json())

    except Exception as e:
        post_error_message(
            slack_token, "캘린더 구독 에러",
            str({
                "e": str(e),
                "slack_token": str(slack_token),
                "args": e.args,
                "traceback": traceback.format_exc()
            })
        )