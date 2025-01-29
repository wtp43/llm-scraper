import json
from pathlib import Path

import xmltodict
from openai import OpenAI

from llm_scraper.json_schema import Prices

# vllm serve Qwen/Qwen2.5-32B-Instruct-GPTQ-Int4  --tensor-parallel-size 2 --max-model-len 32768


class InferenceWorker:
    def __init__(self, n=1):
        self.workers = n
        self.ammo_price_schema = Prices.model_json_schema()

        self.openai_api_key = "EMPTY"
        self.openai_api_base = "http://192.168.50.145:8000/v1"

        self.client = OpenAI(
            api_key=self.openai_api_key,
            base_url=self.openai_api_base,
        )

        # problems with current prompt:
        # - hallucinating item number
        # - hallucinating stock/quantity with rounds
        # - need better way to distinguish between item number, mpn, sku
        #
        self.ammo_info_prompt = """
            You are an expert data extraction and parsing assistant. 
            Your task is to analyze a provided markdown file containing information about ammunition products and extract specific data fields.
            If a field is not found in the markdown file, assign it the value `None`. 
            Return only the extracted data in JSON format with the following structure:
            { "price": null, "sku": null, "upc": null, "mpn": null, "stock": null, "available_quantities": null}

            Provided markdown:
            """
        self.multi_ammo_info_prompt_md = """
            You are an expert data extraction and parsing assistant. 
            Your task is to analyze a provided markdown file containing information about ammunition products and extract specific data fields.
            If a field is not found in the markdown file, assign it the value `None`. 
            Return only the extracted data in JSON format with the following structure:
            {'prices': [{ "title": null, "manufacturer": null, price": null, "sku": null, "upc": null, "mpn": null, "stock": null, "available_quantities": null}]}

            Provided markdown:
            """
        self.multi_ammo_info_prompt_xml = """
            You are an expert data extraction and parsing assistant. 
            Your task is to analyze a provided json file containing information about multiple ammunition products and extract specific data fields.
            If a field is not found in the JSON file, assign it the value `None`. 
            Return only the extracted data in JSON format with the following structure:
            {'prices': [{ "title": null, "manufacturer": null, price": null, "sku": null, "upc": null, "mpn": null, "stock": null, "available_quantities": null}, ...]}

            Provided JSON:
            """

    def extract_ammo_info(self, text):
        response = self.client.chat.completions.create(
            model="Qwen/Qwen2.5-32B-Instruct-GPTQ-Int4",
            messages=[
                {
                    "role": "system",
                    "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant.",
                },
                {"role": "user", "content": self.ammo_info_prompt + text},
            ],
            temperature=0.7,
            top_p=0.8,
            max_tokens=512,
            extra_body={
                "repetition_penalty": 1.05,
                "guided_json": self.ammo_price_schema,
            },
        )
        # print(response.choices[0].message.content)
        return response.choices[0].message.content

    def xml(self):

        text = Path("data.md").read_text()

        # o = xmltodict.parse(text)
        # text = json.dumps(o, indent=4)  # '{"e": {"a": ["text", "text"]}}'
        # print(text)

        response = self.client.chat.completions.create(
            model="Qwen/Qwen2.5-32B-Instruct-GPTQ-Int4",
            messages=[
                {
                    "role": "system",
                    "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant.",
                },
                {"role": "user", "content": self.multi_ammo_info_prompt_xml + text},
            ],
            temperature=0.7,
            top_p=0.8,
            max_tokens=2012,
            extra_body={
                "repetition_penalty": 1.05,
                "guided_json": self.ammo_price_schema,
            },
        )
        print(response.choices[0].message.content)
        return response.choices[0].message.content

        print(result.text_content)
