from slack_sdk import WebClient

slack_calendar_channel = "#-일정-"
slack_calendar_error_channel = "#구독-에러"


def post_daily_message(
        token,
        items,
        channel: str = slack_calendar_channel
):
    """ 슬랙채널에 하루 일정 알림 게시하기 """

    client = WebClient(token=token)
    header_payload = []
    attachments = []

    if len(items) == 0:
        header_payload.append(make_header_payload("오늘은 일정이 없어요"))
    else:
        header_payload.append(make_header_payload("오늘은 총 {}개의 일정이 있어요".format(len(items))))
        for item in items:
            summary = item.get("summary")
            link = item.get("link")
            location = item.get("location")
            meeting_time = item.get("meeting_time")

            block_messages = make_content_payload(summary, link, meeting_time, location)
            attachments.append({
                'color': '#5D3731',
                'blocks': [block_messages]
            })

    client.chat_postMessage(
        channel=channel,
        text="하루 일정 알림",
        blocks=header_payload,
        attachments=attachments
    )


def post_calendar_subscribe_status_message(
        token,
        status,
        channel: str = slack_calendar_channel
):
    """ 슬랙채널에 캘린더 구독상태 게시하기 """

    client = WebClient(token=token)
    header_payload = []
    attachments = []

    header_payload.append(
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": '{}'.format("구글 캘린더 구독 상태 알림")
            }
        }
    )
    attachments.append({
        'color': '#5D3731',
        'blocks': [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": '*상태:{}*'.format(status)
                }
            }
        ]
    })

    client.chat_postMessage(
        channel=channel,
        text="구글 캘린더 구독 상태 알림",
        blocks=header_payload,
        attachments=attachments
    )


def post_job_message(
        token,
        text,
        items,
        channel: str = slack_calendar_channel
):
    """
        슬랙채널에 아래 내용 게시하기
         1. 일정 등록 알림
         2. 일정 취소 알림
         3. 일정 변경 알림
     """

    client = WebClient(token=token)
    header_payload = []
    attachments = []

    if len(items) != 0:
        header_payload.append(make_header_payload(text))
        for item in items:
            print(item)
            summary = item.get("summary", "")
            link = item.get("link", "")
            location = item.get("location", "")
            meeting_time = item.get("meeting_time", "")

            attachments.append({
                'color': '#5D3731',
                'blocks': [make_content_payload_with_li(summary, link, meeting_time, location)]
            })

        client.chat_postMessage(
            channel=channel,
            text=text,
            blocks=header_payload,
            attachments=attachments
        )


def post_error_message(
        token,
        text,
        error_msg,
        channel: str = slack_calendar_error_channel
):
    """
        슬랙채널에 아래 내용 게시하기
         1. 에러 내용
     """

    client = WebClient(token=token)
    header_payload = []
    attachments = []

    header_payload.append(make_header_payload(text))

    attachments.append({
        'color': '#5D3731',
        'blocks': [make_error_content_payload(error_msg)]
    })

    client.chat_postMessage(
        channel=channel,
        text=text,
        blocks=header_payload,
        attachments=attachments
    )


def make_header_payload(header_title):
    return {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": '{}'.format(header_title)
        }
    }


def make_content_payload(summary_title, link, meet_time, location):
    if location is None:
        return {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": '*<{}|{}>*\n{}'.format(link, summary_title, meet_time)
            }
        }
    else:
        return {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": '*<{}|{}>*\n{}\n{}'.format(link, summary_title, meet_time, location)
            }
        }


def make_content_payload_with_li(summary_title, link, meet_time, location):
    if location is None:
        return {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": '*<{}|{}>*\n{}'.format(link, summary_title, meet_time)
            }
        }
    else:
        return {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": '<{}|{}>\n{}\n{}'.format(link, summary_title, meet_time, location)
            }
        }


def make_error_content_payload(error_msg):
    return {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": '{}'.format(error_msg)
        }
    }
