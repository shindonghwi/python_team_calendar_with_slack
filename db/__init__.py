from oauth2client.client import AccessTokenCredentials
import json
import os
import db


def check_user_slack_id():
    with open('{}/user_info.txt'.format(os.path.dirname(os.path.realpath(__file__))), 'r') as file:
        user_info = file.read()
        if len(user_info) == 0:
            return None
        else:
            return True


def set_user_info(
        user_id: str,
        access_token: str = None,
        refresh_token: str = None,
        credentials: AccessTokenCredentials = None,
        next_sync_token: str = None,
):
    user_info_dict = {
        "user_id": user_id,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "credentials": credentials,
        "next_sync_token": next_sync_token,
    }

    json_object = json.dumps(user_info_dict, ensure_ascii=False, indent=4)
    with open('{}/user_info.txt'.format(os.path.dirname(os.path.realpath(__file__))), 'w') as file:
        file.write(json_object)


def get_user_info():
    with open('{}/user_info.txt'.format(os.path.dirname(os.path.realpath(__file__))), 'r') as file:
        try:
            user_info_json = json.load(file)
            if user_info_json["user_id"] is None:
                return None
            else:
                return user_info_json
        except:
            return None


def update_user_info(
        user_info: dict,
        access_token: str = None,
        next_sync_token: str = None,
):
    next_token = user_info["next_sync_token"]
    new_access_token = user_info["access_token"]

    if access_token is not None:
        new_access_token = access_token

    if next_sync_token is not None:
        next_token = next_sync_token

    db.set_user_info(
        user_id=user_info["user_id"],
        access_token=new_access_token,
        refresh_token=user_info["refresh_token"],
        credentials=user_info["credentials"],
        next_sync_token=next_token,
    )

    return db.get_user_info()


def delete_user_info():
    # print("delete_user_info")
    with open('{}/user_info.txt'.format(os.path.dirname(os.path.realpath(__file__))), 'w') as file:
        file.close()


def get_calendar_events():
    with open('{}/calendar_events.txt'.format(os.path.dirname(os.path.realpath(__file__))), 'r') as file:
        return file.readlines()

def add_event_calendar(id: str, status: str, summary: str, link: str, meeting_time: str):
    # print("add_event_calendar")
    if not is_exist_event_id(id):
        file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'calendar_events.txt')
        event_info = {
            "id": id,
            "status": status,
            "summary": summary,
            "link": link,
            "meeting_time": meeting_time,
        }
        json_object = json.dumps(event_info, ensure_ascii=False)

        with open(file_path, 'a') as file:
            file.write("{}\n".format(json_object))


def delete_event_calendar(id: str):
    # print("delete_event_calendar")
    event_list = get_calendar_events()

    updated_objects = []
    removed_objects = []
    for event in event_list:
        json_event_info = json.loads(event)
        if json_event_info["id"] != id:
            updated_objects.append(json_event_info)
        else:
            removed_objects.append(json_event_info)
    with open('{}/calendar_events.txt'.format(os.path.dirname(os.path.realpath(__file__))), 'w') as file:
        for obj in updated_objects:
            file.write(json.dumps(obj) + "\n")

    return removed_objects

def update_event_calendar(id: str, status: str, summary: str):
    # print("update_event_calendar")

    updated_data = {
        "id": id,
        "status": status,
        "summary": summary,
    }

    with open('{}/calendar_events.txt'.format(os.path.dirname(os.path.realpath(__file__))), 'r+') as file:
        lines = file.readlines()
        file.seek(0)

        updated_objects = []
        for line in lines:
            json_object = json.loads(line)
            if json_object.get("id") == id:
                json_object.update(updated_data)
            updated_objects.append(json_object)

        file.truncate()
        for obj in updated_objects:
            file.write(json.dumps(obj) + "\n")


def is_exist_event_id(id: str):
    # print("is_exist_id")
    event_list = get_calendar_events()

    if len(event_list) == 0:
        # print("len event_list 0")
        return False
    else:
        for event in event_list:
            json_event_info = json.loads(event)

            # print("{} - {}".format(id, json_event_info["id"]))

            if id == json_event_info["id"]:
                return True
    # print("not found")
    return False
