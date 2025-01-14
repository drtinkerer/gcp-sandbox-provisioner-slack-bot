from slack_ui import BlockTemplates
ui_blocks = BlockTemplates()

def register_handlers(app):    
    @app.message("hello")
    def message_hello(message, say):
        say(f"Hey there <@{message['user']}>!")

    @app.event("app_home_opened")
    def publish_home_tab(client, event, logger):
        try:
            client.views_publish(
                user_id=event["user"],
                view=ui_blocks.app_home
            )
        except Exception as e:
            logger.error(f"Error publishing home tab: {e}")

    @app.action("button_click")
    def open_sandbox_request_form(ack, body, client):
        ack()
        client.views_open(
            trigger_id=body["trigger_id"],
            view=ui_blocks.sandbox_request_form
        )

# Handle a view_submission request
    @app.view("sandbox_request_form")
    def handle_submission(ack, body, client, view, logger):
        ack()
        user_id = body["user"]["id"]
        user_email = client.users_info(user=user_id)["user"]["profile"]["email"]
        cloud_provider = body["view"]["state"]["values"]["cloud_provider"]['static_select-action']["selected_option"]["value"]

        # print(user_email)
        submission_data = {
            "cloud_provider": cloud_provider,
            "user_email": user_email,
            "requested_duration_hours": body["view"]["state"]["values"]["requested_duration_hours"]['static_select-action']["selected_option"]["value"] or "2",
            "team_name": body["view"]["state"]["values"]["team_name"]['static_select-action']["selected_option"]["value"],
            "additional_users": body["view"]["state"]["values"]["additional_users"]['multi_users_select-action']["selected_users"],
            "request_description": body["view"]["state"]["values"]["request_description"]['plain_text_input-action']["value"]
        }
        print(submission_data)

        import requests

        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }

        # json_data = {
        #     "user_email": user_email,
        #     "cloud_provider": cloud_provider,
        #     "team_name": body["view"]["state"]["values"]["team_name"]['static_select-action']["selected_option"]["value"],
        #     "requested_duration_hours": int(body["view"]["state"]["values"]["requested_duration_hours"]['static_select-action']["selected_option"]["value"]),
        #     "request_description": body["view"]["state"]["values"]["request_description"]['plain_text_input-action']["value"],
        #     "additional_users": body["view"]["state"]["values"]["additional_users"]['multi_users_select-action']["selected_users"]
        # }

        response = requests.post('http://localhost:4000/create_gcp_sandbox/', headers=headers, json=submission_data)
        print(response.json())
        print(response.status_code)
        # Message the user with acknowledgement
        try:
            if response.status_code == 200:
                client.chat_postMessage(channel=user_id, text=f"Request recieved for <@{user_id}>. Sandbox will be ready shortly.")
            else:
                client.chat_postMessage(channel=user_id, text=f"Request failed for <@{user_id}>. Please try again.")
        except Exception as e:
            logger.exception(f"Failed to post a message {e}")