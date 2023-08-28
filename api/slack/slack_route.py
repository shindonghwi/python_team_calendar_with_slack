import datetime
import locale
import json
import flask
import requests
from flask import (
    Blueprint, request, make_response, current_app, redirect, session, url_for, jsonify, Markup
)
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from .utils import google_auth
import db
from .bot import post_daily_message, post_job_message, post_error_message, post_calendar_subscribe_status_message
from . import event_app_home_not_connected, event_app_home_connected
import traceback

bp = Blueprint('slack', __name__)

scopes = [
    'openid',
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/drive'
]


@bp.route('/events', methods=['POST'])
def events():
    """ 슬랙 이벤트 수신 """
    try:
        slack_event = json.loads(request.data)
    except json.JSONDecodeError as e:
        post_error_message(current_app.config["slack_token"], "슬랙 이벤트 수신 에러", str(e))

    # 슬랙 도메인 인증을 위한 기능 - challenge return
    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type": "application/json"})

    if "event" in slack_event:
        try:
            event_type = slack_event["event"]["type"]

            print("event_type: ", event_type)

            if event_type == "app_home_opened":
                print(slack_event['event']['user'])
                return event_app_home_not_connected(
                    slack_token=current_app.config["slack_token"],
                    user_id=slack_event['event']['user']
                )
        except Exception as e:
            post_error_message(
                current_app.config["slack_token"], "슬랙 이벤트 수신 에러",
                str({
                    "e": str(e),
                    "args": e.args,
                    "traceback": traceback.format_exc()
                })
            )


@bp.route('/authorize', methods=['GET'])
def authorize():
    """
    슬랙 홈에서 - 구글 캘린더 계정 연동 버튼 클릭시 호출 되는 기능

    사용자 정보는 db/user_info.txt 에 저장한다.

    사용자 정보가 없는 경우
        - credentials.json 파일을 가져와 인증 flow를 만든다.
        - @return @계정 선택 화면으로 redirect 한다.

    사용자 정보가 있는 경우
        - access_token 만료 시간을 확인한다. ( 만료되었으면, access_token을 갱신한다. )
        - @return access_token

    """
    try:
        user_id = request.args.get('user_id')  # query params

        # 사용자 정보가 없는 경우
        if db.check_user_slack_id() is None:
            flow = google_auth.get_flow_from_secret_file()
            flow.redirect_uri = url_for("slack.oauth2callback", _external=True, _scheme="https")
            url, state = flow.authorization_url(access_type="offline", prompt='consent', include_granted_scopes='true')
            flask.session['state'] = state + "&&" + user_id
            return redirect(url)  # 계정 인증 URL로 이동

        # 사용자 정보가 있는 경우
        else:
            user_info = db.get_user_info()
            is_expired = google_auth.check_access_token_expired(access_token=user_info["access_token"])
            if is_expired:  # 액세스 토큰 만료 -> 토큰 갱신
                user_info = google_auth.refresh_access_token(
                    user_info=user_info,
                    client_id=current_app.config["client_id"],
                    client_secret=current_app.config["client_secret"],
                    refresh_token=user_info["refresh_token"]
                )
            res = {
                "status": 200,
                "msg": "토큰 정보가 갱신되었습니다",
                "data": {
                    "access_token": user_info["access_token"]
                }
            }

            renew_subscribe(access_token=user_info["access_token"])

            event_app_home_connected(
                slack_token=current_app.config["slack_token"],
                user_id=user_id
            )  # 슬랙 홈 UI 변경하기

            credentials = google_auth.get_credentials(user_info["access_token"])
            next_sync_token = google_auth.get_calender_next_sync_token(credentials)
            db.update_user_info(user_info=user_info, next_sync_token=next_sync_token)

            return res
    except Exception as e:
        post_error_message(
            current_app.config["slack_token"], "사용자 인증 에러",
            str({
                "e": str(e),
                "args": e.args,
                "traceback": traceback.format_exc()
            })
        )


@bp.route('/oauth2callback', methods=['GET'])
def oauth2callback():
    try:
        state = flask.session['state'].split("&&")[0]
        user_id = flask.session['state'].split("&&")[1]
        flow = google_auth.get_flow_from_secret_file(state)

        flow.redirect_uri = flask.url_for('slack.oauth2callback', _external=True, _scheme="https")
        authorization_response = flask.request.url
        flow.fetch_token(authorization_response=authorization_response)
        credentials = flow.credentials

        next_sync_token = google_auth.get_calender_next_sync_token(credentials)

        db.set_user_info(
            user_id,
            access_token=credentials.token,
            refresh_token=credentials.refresh_token,
            credentials=google_auth.credentials_to_dict(credentials),
            next_sync_token=next_sync_token
        )

        res = requests.get('https://google-calendar-slack.orotcode.com/slack/authorize?user_id=U03MXBND80Y')
        access_token = res.json()['data']['access_token']
        renew_subscribe(access_token=access_token)

        event_app_home_connected(
            slack_token=current_app.config["slack_token"],
            user_id=user_id
        )  # 슬랙 홈 UI 변경하기

        res = {
            "status": 200,
            "msg": "인증에 성공했습니다. 화면을 닫고 Slack으로 돌아가세요",
        }
        return res
    except Exception as e:
        post_error_message(
            current_app.config["slack_token"], "인증 중 에러",
            str({
                "e": str(e),
                "args": e.args,
                "traceback": traceback.format_exc()
            })
        )

# 구독갱신하기
def renew_subscribe(access_token: str):
    slack_token = "xoxb-3745296232272-4845927270291-uE78X8df2sNz6cC2MSfMsVlH"
    headers = {
        "Authorization": "Bearer {}".format(access_token),
        'Content-Type': 'application/json'
    }
    data = {
        'id': 'U03MXBND80Y',
        'type': 'web_hook',
        'address': 'https://google-calendar-slack.orotcode.com/slack/watch/callback'
    }
    res_subscribe = requests.post(
        'https://www.googleapis.com/calendar/v3/calendars/dev@orotcode.com/events/watch',
        json=data,
        headers=headers
    )

@bp.route('/logout')
def logout():
    try:
        user_id = request.args.get("user_id")

        db.delete_user_info()
        event_app_home_not_connected(
            slack_token=current_app.config["slack_token"],
            user_id=user_id
        )

        res = {
            "status": 200,
            "msg": "로그아웃 성공했습니다. 다시 또 Google Calendar Notification Bot을 찾아주세요",
        }

        return res
    except Exception as e:
        post_error_message(
            current_app.config["slack_token"], "로그아웃 에러",
            str({
                "e": str(e),
                "args": e.args,
                "traceback": traceback.format_exc()
            })
        )


@bp.route("calenders", methods=['GET'])
def get_calender_list():
    try:
        user_id = request.args.get('user_id')
        user_info = db.get_user_info()
        access_token = user_info["access_token"]

        if user_info is not None:
            is_expired = google_auth.check_access_token_expired(access_token=access_token)

            if is_expired:
                user_info = google_auth.refresh_access_token(
                    user_info=user_info,
                    client_id=current_app.config["client_id"],
                    client_secret=current_app.config["client_secret"],
                    refresh_token=user_info.get("refresh_token")
                )

        credentials = google_auth.get_credentials(user_info.get("access_token"))

        try:
            service = build('calendar', 'v3', credentials=credentials)
            today_initial = datetime.datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            ).isoformat() + 'Z'

            events_result = service.events().list(
                calendarId='dev@orotcode.com',
                timeMin=today_initial,
                maxResults=10, singleEvents=True,
                orderBy='startTime').execute()

            events = events_result.get('items', [])
            today_events = []
            for event in events:
                item = parse_item_from_event(event, True)
                today_start_time = event['start'].get('dateTime', event['start'].get('date'))
                today = datetime.datetime.today().date()

                db.add_event_calendar(event["id"], event["status"], event["summary"], event["htmlLink"],
                                      item["meeting_time"])

                if today == datetime.datetime.fromisoformat(today_start_time).date():
                    today_events.append(item)
            post_daily_message(current_app.config["slack_token"], today_events)

            res = {
                "status": 200,
                "msg": "success",
                "data": today_events
            }

            return res

        except HttpError as e:
            post_error_message(
                current_app.config["slack_token"], "캘린더 목록 가져오기 에러",
                str({
                    "e": str(e),
                    "args": e.args,
                    "traceback": traceback.format_exc()
                })
            )
    except Exception as e:
        post_error_message(
            current_app.config["slack_token"], "캘린더 목록 가져오기 에러",
            str({
                "e": str(e),
                "args": e.args,
                "traceback": traceback.format_exc()
            })
        )


@bp.route('/watch/callback', methods=['POST'])
def google_calendar_watch():
    try:
        user_id = flask.request.headers.get("X-Goog-Channel-Id")
        user_info = db.get_user_info()

        # access_token 만료 체크
        is_expired = google_auth.check_access_token_expired(access_token=user_info["access_token"])
        if is_expired:
            user_info = google_auth.refresh_access_token(
                user_info=user_info,
                client_id=current_app.config["client_id"],
                client_secret=current_app.config["client_secret"],
                refresh_token=user_info["refresh_token"]
            )

        # access_token = user_info.get("access_token")
        next_sync_token = user_info["next_sync_token"]

        service = build('calendar', 'v3', credentials=google_auth.get_credentials(user_info.get("access_token")))
        current_events = service.events().list(calendarId='dev@orotcode.com',
                                               # showDeleted=False,
                                               # maxResults=2500,
                                               # singleEvents=False
                                               syncToken=next_sync_token,
                                               ).execute()

        # print("ASdaksdjhaskjd : ", current_events)

        try:
            db.update_user_info(user_info=user_info, next_sync_token=current_events['nextSyncToken'])
        except:
            pass

        # print("cc: ", current_events)

        events = current_events.get('items', [])

        cancel_items = []
        update_items = []
        create_items = []

        print("event len: ", len(events))

        for event in events:
            event_id = event.get("id", None)
            event_status = event.get("status", None)
            event_summary = event.get("summary", None)
            event_link = event.get("htmlLink", None)

            if event_id is not None:
                item = parse_item_from_event(event, False)

                # 이벤트가 등록되어 있지 않은 경우
                # print("kk - ", event_status)
                if not db.is_exist_event_id(event_id):
                    if event_status == 'confirmed':  # 등록
                        # print("등록 {}".format(event_summary))
                        parse_data = parse_item_from_event(event, False)
                        meeting_time = parse_data['meeting_time']
                        db.add_event_calendar(event_id, event_status, event_summary, event_link, meeting_time)
                        create_items.append(item)
                else:
                    if event_status == 'cancelled':  # 취소
                        print("취소 {}".format(event_summary))
                        removed_list = db.delete_event_calendar(event_id)

                        for remove_item in removed_list:
                            cancel_items.append(remove_item)
                    elif event_status == 'confirmed':  # 업데이트
                        # print("업데이트 {}".format(event_summary))
                        db.update_event_calendar(event_id, event_status, event_summary)
                        update_items.append(item)

        print("event 등록:{}개".format(len(create_items)))
        print("event 취소:{}개".format(len(cancel_items)))
        print("event 변경:{}개".format(len(update_items)))

        post_job_message(current_app.config["slack_token"], "일정 등록 알림", create_items)
        post_job_message(current_app.config["slack_token"], "일정 취소 알림", cancel_items)
        post_job_message(current_app.config["slack_token"], "일정 변경 알림", update_items)

    except Exception as e:
        post_error_message(
            current_app.config["slack_token"], "캘린더 Event Watch Error",
            str({
                "e": str(e),
                "args": e.args,
                "traceback": traceback.format_exc()
            })
        )
    return 'success', 204


def parse_item_from_event(event, is_daily_mode):

    print(event)

    item = {
        "summary": event.get("summary", None),
        "location": event.get("location", None),
        "meeting_time": None,
        "link": event.get("htmlLink", None),
    }

    if event.get("status") == "cancelled":
       print("취소 상태에서는 정보가 없음.")
    else:
        start = event.get("start", None)
        if start and start.get("date"):
            start = event.get("start", None).get("date")
            end = event.get("end", None).get("date")
            item["meeting_time"] = "종일 {}".format(start)

        # 하루 일정 시간 체크
        elif start and start.get("dateTime"):
            start_datetime = event.get("start", None).get("dateTime")
            end_datetime = event.get("end", None).get("dateTime")
            start_date = str(start_datetime).split("T")[0]
            end_date = str(end_datetime).split("T")[0]
            start = str(event.get("start", None).get("dateTime")).split("T")[1].split("+")[0]
            end = event.get("end", None).get("dateTime").split("T")[1].split("+")[0]

            start_time = start.split(":")
            end_time = end.split(":")

            date_format = "%Y-%m-%dT%H:%M:%S%z"
            start_date_obj = datetime.datetime.strptime(start_datetime, date_format)
            end_date_obj = datetime.datetime.strptime(end_datetime, date_format)

            korean_locale = locale.setlocale(locale.LC_TIME, 'ko_KR.utf8')
            start_yoil = start_date_obj.strftime("%a").strip()
            end_yoil = end_date_obj.strftime("%a").strip()

            if is_daily_mode:
                item["meeting_time"] = "{}시 {}분".format(start_time[0], start_time[1])
                item["meeting_time"] += " ~ {}시 {}분".format(end_time[0], end_time[1])
            else:
                item["meeting_time"] = "{}({}) {}시 {}분".format(start_date, start_yoil, start_time[0], start_time[1])

                if start_date == end_date:
                    item["meeting_time"] += " ~ {}시 {}분".format(end_time[0], end_time[1])
                else:
                    item["meeting_time"] += " ~ {}({}) {}시 {}분".format(end_date, end_yoil, end_time[0], end_time[1])

    return item
