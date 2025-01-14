import os
from fastapi import FastAPI, HTTPException
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_bolt.app import App
from slack_handlers import register_handlers
from datetime import timedelta, datetime, UTC
from base_models import SandboxCreate
from providers.gcp import *
from google.protobuf.timestamp_pb2 import Timestamp

# Set enviornment vars
BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
APP_TOKEN = os.environ["SLACK_APP_TOKEN"]
SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]

team_folders = {
    "Team-3": "folders/550157719134",
    "Team-4": "folders/1005335406543",
    "Team-Data": "folders/118001772766",
    "Team-DevOps": "folders/330608683756"
}

max_allowed_projects_per_user = 1

# Load Slack Bolt
app = App(token=BOT_TOKEN, signing_secret=SIGNING_SECRET)

# Load FastAPI
api = FastAPI()

# Load Slack bolt handlers
SocketModeHandler(app, APP_TOKEN).connect()

register_handlers(app)

# Load FastAPI endpoints
@api.get("/")
async def root():
    return {"OK"}



@api.post("/create_gcp_sandbox/")
def create_gcp_sandbox(user_data: SandboxCreate):
    """
    Creates a google cloud sandbox project based on the provided user data.
    """
    # return (user_data)
    user_email = user_data.user_email
    team_name = user_data.team_name
    requested_duration_hours = int(user_data.requested_duration_hours)
    request_description = user_data.request_description
    folder_id = team_folders[team_name]

    user_email_prefix = user_email.split("@")[0].replace(".", "-")

    # Check active sandboxes
    active_projects_count = get_active_projects_count(user_email_prefix, folder_id)
    if active_projects_count >= max_allowed_projects_per_user:
        raise HTTPException(status_code=400, detail=f"ERROR 400: User {user_email} has reached maximum number of allowed active sandbox projects.")

    request_time = datetime.now(UTC)
    request_time_str = request_time.strftime("%Y-%m-%d-%H-%M-%S")

    delta = timedelta(hours=requested_duration_hours)
    expiry_timestamp = Timestamp()
    expiry_timestamp.FromDatetime(request_time + delta)

    project_id = generate_project_id(user_email, request_time_str)

    print(f"Handling sandbox project creation event for {user_email}...")
    create_project_response = create_sandbox_project(project_id, folder_id)
    print(f"Successfuly created project {project_id}.")

    print(f"Linking project {project_id} to billing account...")
    updated_project_billing_response = update_project_billing_info(project_id)
    print(f"Successfuly linked project {project_id} to billing account.")

    print(f"Creating deletion task for Project {project_id} on Google Cloud Tasks queue...")
    create_deletion_task_response = create_deletion_task(project_id, project_id, expiry_timestamp)
    print(f"Successfully created deletion task for Project {project_id} on Google Cloud Tasks queue.")

    return {
        "detail": "Sandbox project provisioned succesfully",
        "user_email": user_email,
        "team_name": team_name,
        "project_id": project_id,
        "folder_id": folder_id,
        "request_description": request_description,
        "billing_enabled": updated_project_billing_response.billing_enabled,
        "project_url": f"https://console.cloud.google.com/welcome?project={project_id}",
        "created_at": create_project_response.create_time.strftime("%Y-%d-%m %H:%M:%S UTC"),
        "expires_at": create_deletion_task_response.schedule_time.strftime("%Y-%d-%m %H:%M:%S UTC")
    }