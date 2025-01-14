from pydantic import BaseModel, EmailStr, Field, field_validator
import os
import json
from typing import List

# Constants
AUTHORIZED_DOMAINS = ["gmail.com"]
TEAM_FOLDERS = {
    "Team-3": "folders/550157719134",
    "Team-4": "folders/1005335406543",
    "Team-Data": "folders/118001772766",
    "Team-DevOps": "folders/330608683756"
}


class SandboxCreate(BaseModel):
    user_email: EmailStr = Field(
        ...,
        description=f"Email address of the user requesting the sandbox. User must belong to {AUTHORIZED_DOMAINS}"
    )
    team_name: str = Field(
        ...,
        description=f"Name of the team to which the sandbox belongs. Team name must be one in {TEAM_FOLDERS.keys()}"
    )
    requested_duration_hours: int = Field(
        2,
        description="Requested duration of the sandbox in hours."
    )
    request_description: str = Field(
        default="POC On ",
        description="Description for sandbox requirement."
    )
    cloud_provider: str = Field(
        ...,
        description="Cloud Provider to be used for the sandbox.",
        choices=["GCP", "AWS", "AZURE"]
    )
    additional_users: List[str] = Field(
        default=[],
        description="Optional list of additional users to grant access to the sandbox environment."
    )

    @field_validator('user_email')
    @classmethod
    def validate_user_email_domain(cls, validated_email: str) -> str:
        user_email_domain = validated_email.split("@")[1]
        if user_email_domain not in AUTHORIZED_DOMAINS:
            raise ValueError(f"User {validated_email} doesn't belong to authorized domains {AUTHORIZED_DOMAINS}")
        return validated_email

    @field_validator('team_name')
    @classmethod
    def validate_team_name(cls, validated_team_name: str) -> str:
        if validated_team_name not in TEAM_FOLDERS.keys():
            raise ValueError(f"Team name {validated_team_name} is invalid. Required value must be one in {TEAM_FOLDERS.keys()}")
        return validated_team_name


class SandboxDelete(BaseModel):
    project_id: str = Field(
        ...,
        description="ID of the project to be deleted."
    )


class SandboxExtend(BaseModel):
    project_id: str = Field(
        ...,
        description="ID of the project to be extended."
    )
    extend_by_hours: int = Field(
        4,
        description="Number of hours by which to extend the sandbox."
    )