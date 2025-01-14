import os
from google.cloud import resourcemanager_v3, billing_v1, run_v2, tasks_v2

cloud_run_service_id = os.environ["CLOUDRUN_SERVICE_ID"]
master_service_account_email = os.environ["SERVICE_ACCOUNT_EMAIL"]

def create_sandbox_project(project_id, folder_id):

    client = resourcemanager_v3.ProjectsClient()

    project_request = resourcemanager_v3.CreateProjectRequest(
        project=resourcemanager_v3.Project(
            project_id=project_id,
            parent=folder_id,
            display_name=project_id
        )
    )

    operation = client.create_project(request=project_request)
    response = operation.result()

    # Handle the response
    return response


def update_project_billing_info(project_id):

    billing_account_id = os.environ["BILLING_ACCOUNT_ID"]
    client = billing_v1.CloudBillingClient()

    # Initialize request argument(s)
    request = billing_v1.UpdateProjectBillingInfoRequest(
        name=f"projects/{project_id}",
        project_billing_info=billing_v1.ProjectBillingInfo(
            billing_account_name=f"billingAccounts/{billing_account_id}"
        )
    )

    # Make the request
    response = client.update_project_billing_info(request=request)
    return response


def delete_sandbox_project(project_id):
    # Create a client
    client = resourcemanager_v3.ProjectsClient()

    # Initialize request argument(s)
    request = resourcemanager_v3.DeleteProjectRequest(
        name=f"projects/{project_id}"
    )

    # Make the request
    operation = client.delete_project(request=request)
    response = operation.result()

    # Handle the response
    return response

def generate_project_id(user_email, current_timestamp):
    extract_prefix = user_email.split("@")[0].replace(".", "-")
    return f"{extract_prefix}-{current_timestamp}"


def get_active_projects_count(user_email_prefix, folder_id):
    client = resourcemanager_v3.ProjectsClient()

    # Initialize request argument(s)
    request = resourcemanager_v3.ListProjectsRequest(
        parent=folder_id,
    )

    # Make the request
    page_result = client.list_projects(request=request)

    project_list = [response.project_id for response in page_result]

    count = 0
    for project in project_list:
        if user_email_prefix in project:
            count += 1
    return count


def get_cloud_run_service_url(cloud_run_service_id):
    client = run_v2.ServicesClient()

    request = run_v2.GetServiceRequest(
        name=cloud_run_service_id
    )

    response = client.get_service(request=request)
    return response.uri


def get_cloud_task_expiry_time(task_id):
    # Create a client
    client = tasks_v2.CloudTasksClient()

    # Initialize request argument(s)
    request = tasks_v2.GetTaskRequest(
        name=task_id
    )

    # Make the request
    response = client.get_task(request=request)

    # Handle the response
    return int(response.schedule_time.timestamp())


def delete_cloud_task(task_id):
    # Create a client
    client = tasks_v2.CloudTasksClient()

    # Initialize request argument(s)
    request = tasks_v2.DeleteTaskRequest(
        name=task_id,
    )

    # Make the request
    response = client.delete_task(request=request)

    return response


def list_cloud_tasks(project_id):
    # Create a client
    client = tasks_v2.CloudTasksClient()
    cloud_tasks_queue_id = os.environ["CLOUD_TASKS_DELETION_QUEUE_ID"]

    # Initialize request argument(s)
    request = tasks_v2.ListTasksRequest(
        parent=cloud_tasks_queue_id
    )

    # Make the request
    page_result = client.list_tasks(request=request)

    # Handle the response
    for response in page_result:
        if project_id in response.name:
            return response.name
    


def create_deletion_task(project_id, task_name, expiry_timestamp):
    client = tasks_v2.CloudTasksClient()

    cloud_run_service_url = get_cloud_run_service_url(cloud_run_service_id)

    cloud_tasks_queue_id = os.environ["CLOUD_TASKS_DELETION_QUEUE_ID"]

    task_object = tasks_v2.Task(
        name=f"{cloud_tasks_queue_id}/tasks/{task_name}",
        http_request=tasks_v2.HttpRequest(
            url=f"{cloud_run_service_url}/delete_sandbox",
            body=f'{{"project_id":"{project_id}"}}'.encode('utf-8'),
            headers=[("Content-Type", "application/json")],
            oidc_token=tasks_v2.OidcToken(
                service_account_email=master_service_account_email
            )
        ),
        schedule_time=expiry_timestamp
    )

    # Initialize request argument(s)
    request = tasks_v2.CreateTaskRequest(
        parent=cloud_tasks_queue_id,
        task=task_object
    )

    # Make the request
    response = client.create_task(request=request)

    # Handle the response
    return response

def get_cloud_run_service_url(cloud_run_service_id):
    client = run_v2.ServicesClient()

    request = run_v2.GetServiceRequest(
        name=cloud_run_service_id
    )

    response = client.get_service(request=request)
    return response.uri