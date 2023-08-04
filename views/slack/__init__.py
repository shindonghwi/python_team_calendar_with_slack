""" 슬랙 피시 앱 (홈) - UI """
def get_app_home_not_connected_view(user_id: str):
    return {
        "type": "home",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "구글 캘린더를 연동하여 알림을 받을 수 있는 앱입니다"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*주요 기능* \n\n 1. 하루의 일정을 지정된 시간에 보고합니다.\n2. 캘린더에 일정이 등록,삭제되면 보고합니다"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "구글 캘린더 계정 연동"
                        },
                        "style": "primary",
                        "url": "https://google-calendar-slack.orotcode.com/slack/authorize?user_id={}".format(user_id)
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "오롯코드 홈페이지"
                        },
                        "url": "https://www.orotcode.com"
                    }
                ]
            }
        ]
    }

def get_app_home_connected_view(user_id: str):
    return {
        "type": "home",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "구글 캘린더를 연동하여 알림을 받을 수 있는 앱입니다"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*주요 기능* \n\n 1. 하루의 일정을 지정된 시간에 보고합니다.\n2. 캘린더에 일정이 등록,삭제되면 보고합니다"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "로그아웃"
                        },
                        "style": "primary",
                        "url": "https://google-calendar-slack.orotcode.com/slack/logout?user_id={}".format(user_id)
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "오롯코드 홈페이지"
                        },
                        "url": "https://www.orotcode.com"
                    }
                ]
            }
        ]
    }