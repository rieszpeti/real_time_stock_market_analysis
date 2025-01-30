import json
import logging
import requests


class KafkaSinkCreator:
    def __init__(self, base_url: str):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.base_url = base_url

    def create_sink(self, config: dict) -> None:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        json_data = json.dumps(config)
        response = requests.post(self.base_url, headers=headers, data=json_data)

        if response.status_code == 201:
            self.logger.info("Successfully created sink")
        else:
            self.logger.error("Failed to create sink, Status Code: %d", response.status_code)
