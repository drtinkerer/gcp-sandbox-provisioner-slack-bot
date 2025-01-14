import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import json
from pprint import pprint

# Open and read the JSON file
with open('ui-blocks/blocks.json', 'r') as file:
    data = json.load(file)

with open('ui-blocks/modal.json', 'r') as file:
    modal = json.load(file)

with open('ui-blocks/app_home.json', 'r') as file:
    app_home = json.load(file)

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN").strip()
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN").strip()

# Initializes your app with your bot token and socket mode handler
app = App(token=SLACK_BOT_TOKEN)
# pprint(app.client.admin_teams_list(token = SLACK_BOT_TOKEN))
# pprint(dir(app.client.users_info))
# print(app.client.users_identity())
# New functionality
@app.event("app_home_opened")
def update_home_tab(client, event, logger):
    try:
        # views.publish is the method that your app uses to push a view to the Home tab
        client.views_publish(
            # the user that opened your app's app home
            user_id=event["user"],
            # the view object that appears in the app home
            view=app_home
        )

    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")


@app.action("button_click")
def open_modal(ack, body, client):
    # Acknowledge the command request
    ack()
    # Call views_open with the built-in client
    client.views_open(
        # Pass a valid trigger_id within 3 seconds of receiving it
        trigger_id=body["trigger_id"],
        # View payload
        view = modal
    )

# @app.action("button_click")
# def action_button_click(body, ack, say):
#     # Acknowledge the action
#     print(body)
#     ack()
#     say(f"<@{body['user']['id']}> clicked the button")


@app.view("")
def handle_view_submission_events(ack, body, logger):
    # pprint(body["view"]["state"]["values"])
    submission_data = {
        "cloud_provider": body["view"]["state"]["values"]["cloud_provider"]['static_select-action']["selected_option"]["text"]["text"],
        "requested_time_duration": body["view"]["state"]["values"]["requested_time_duration"]['static_select-action']["selected_option"]["text"]["text"] or "222 hours",
        "additional_users": body["view"]["state"]["values"]["additional_users"]['multi_users_select-action']["selected_users"],
        "reason_for_request": body["view"]["state"]["values"]["reason_for_request"]['plain_text_input-action']["value"]
    }
    print(submission_data)
    ack()
    logger.info(body)

# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, SLACK_APP_TOKEN).start()
