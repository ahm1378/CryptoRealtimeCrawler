import json
import uuid
from json import JSONDecodeError
import re


class TexTCleaner:

    @staticmethod
    def extract_json_from_text(text):
        text_without_newlines = text.replace('\n', '')
        pattern = r'\{.*\}'
        match = re.search(pattern, text_without_newlines)

        if match:
            json_data = match.group(0)
            try:
                parsed_data = json.loads(json_data)
            except JSONDecodeError:
                json_data = json_data.replace("'", '"').replace("false", "False").replace("true", "True")
                parsed_data = eval(json_data)
            return parsed_data
        else:
            return None

    @staticmethod
    def extract_delete_json_from_text(text: str):
        spliter = text.split('{')
        original_text = spliter[0]
        return original_text


def generate_user_id():
    return str(uuid.uuid4())