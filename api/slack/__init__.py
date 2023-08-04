from views.slack import get_app_home_not_connected_view, get_app_home_connected_view
from slack_sdk import WebClient
from flask import make_response



def event_app_home_not_connected(slack_token: str, user_id: str):
    """ 슬랙 피시 앱 (홈) - 연결이 안되었을때 화면 """
    client = WebClient(token=slack_token)
    WebClient.views_publish(
        self=client,
        user_id=user_id,
        view=get_app_home_not_connected_view(user_id),
    )
    return make_response("ok", 200)

def event_app_home_connected(slack_token: str, user_id: str):
    """ 슬랙 피시 앱 (홈) - 연결이 되었을때 화면 """
    client = WebClient(token=slack_token)
    WebClient.views_publish(
        self=client,
        user_id=user_id,
        view=get_app_home_connected_view(user_id),
    )
    return make_response("ok", 200)
