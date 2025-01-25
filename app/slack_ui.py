import json
from typing import Dict, Any
from config import Config


class BlockTemplates:
    def __init__(self):
        self.base_path = "app/slack_ui_blocks"
        self.config = Config()

        # Load static blocks into memory
        self.app_home = self._load_block("app_home.json")
        self.sandbox_request_form = self._load_block(
            "sandbox_request_form.json")
        self.sandbox_request_form_ack = self._load_block(
            "sandbox_request_form_ack.json")
        self._update_sandbox_request_form()

    def _load_block(self, filename: str) -> Dict[str, Any]:
        """
        Load a JSON file from the base path.
        Args:
            filename (str): JSON file to load
        Returns:
            Dict[str, Any]: Parsed JSON content
        """
        with open(f"{self.base_path}/{filename}", "r") as file:
            return json.load(file)

    def _update_sandbox_request_form(self):
        """
        Update the sandbox request form dynamically with team options.
        """
        team_name_options = [
            {
                "text": {"type": "plain_text", "text": team, "emoji": True},
                "value": team,
            }
            for team in self.config.AUTHORIZED_TEAM_FOLDERS
        ]

        # Modify sandbox_request_form blocks
        for block in self.sandbox_request_form["blocks"]:
            if block.get("block_id") == "team_name":
                block["element"]["options"] = team_name_options

    def _acknowledge_sandbox_request(self, user_id):
        self.sandbox_request_form_ack["blocks"][0]["text"]["text"] = f"Thanks for your submission, <@{user_id}>!\n Your sandbox will be provisioned shortly."
        
        return self.sandbox_request_form_ack
