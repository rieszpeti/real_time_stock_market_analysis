import json
import logging
import requests
import time


class KafkaSinkCreator:
    def __init__(self, base_url: str):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.base_url = base_url

    def create_sink(self, config: dict, max_retries: int = 5, backoff_factor: float = 2.0) -> None:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        json_data = json.dumps(config)

        for attempt in range(max_retries):
            try:
                response = requests.post(self.base_url, headers=headers, data=json_data)

                if response.status_code == 200 or response.status_code == 201:
                    self.logger.info("Successfully created sink")
                    return  # Exit after a successful request
                else:
                    self.logger.error("Failed to create sink, Status Code: %d", response.status_code)
                    raise Exception(f"Failed with status code: {response.status_code}")

            except requests.RequestException as e:
                self.logger.error(f"Request failed on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    sleep_time = backoff_factor ** attempt
                    self.logger.info(f"Retrying in {sleep_time} seconds...")
                    time.sleep(sleep_time)  # Exponential backoff
                else:
                    self.logger.error("Max retries reached. Could not create sink.")
