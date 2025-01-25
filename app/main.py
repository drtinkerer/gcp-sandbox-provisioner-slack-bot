import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_ui import BlockTemplates
from config import Config

config = Config()
# Load UI blocks
ui_blocks = BlockTemplates()

# Initialize the Slack app with bot token
app = App(token=config.SLACK_BOT_TOKEN)

@app.message("hello")
def message_hello(message, say):
    say(f"Hey there <@{message['user']}>!")

@app.event("app_home_opened")
def publish_home_tab(client, event, logger):
    try:
        # Publish dynamic home tab
        client.views_publish(
            user_id=event["user"],
            view=ui_blocks.app_home
        )
    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")

@app.action("button_click")
def open_sandbox_request_form(ack, body, client):
    ack()
    # Dynamically updated form
    client.views_open(
        trigger_id=body["trigger_id"],
        view=ui_blocks.sandbox_request_form
    )


@app.view("sandbox_request_form_submit")
def handle_submission(ack, body, client, logger):
    ack()
    user_id = body["user"]["id"]

    try:
        user_info = client.users_info(user=user_id)
        user_email = user_info["user"]["profile"].get("email", "No email found")

        cloud_provider = body["view"]["state"]["values"]["cloud_provider"]['static_select-action']["selected_option"].get("value", "Not selected")
        requested_duration_hours = body["view"]["state"]["values"]["requested_duration_hours"]['static_select-action']["selected_option"].get("value", "2")
        team_name = body["view"]["state"]["values"]["team_name"]['static_select-action']["selected_option"].get("value", "Not specified")
        additional_users = body["view"]["state"]["values"]["additional_users"]['multi_users_select-action']["selected_users"]
        request_description = body["view"]["state"]["values"]["request_description"]['plain_text_input-action'].get("value", "No description")

        submission_data = {
            "cloud_provider": cloud_provider,
            "user_email": user_email,
            "requested_duration_hours": requested_duration_hours,
            "team_name": team_name,
            "additional_users": additional_users,
            "request_description": request_description
        }

        print(submission_data)
        # print(client.users_info(user=additional_users[0]))

        # Open a new ephemeral modal/dialog to notify the user
        client.views_open(
            trigger_id=body["trigger_id"],
            view=ui_blocks._acknowledge_sandbox_request(user_id)
        )

    except Exception as e:
        logger.error(f"Error handling submission: {e}")

# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, config.SLACK_APP_TOKEN).start()

