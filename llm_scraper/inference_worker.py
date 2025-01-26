from openai import OpenAI

from llm_scraper.json_schema import Price


class InferenceWorker:
    def __init__(self, n=1):
        self.workers = n
        self.ammo_price_schema = Price.model_json_schema()

        self.openai_api_key = "EMPTY"
        self.openai_api_base = "http://192.168.50.145:8000/v1"

        self.client = OpenAI(
            api_key=self.openai_api_key,
            base_url=self.openai_api_base,
        )

        self.ammo_info_prompt = """
            You are an expert data extraction and parsing assistant. 
            Your task is to analyze a provided markdown file containing information 
            about ammunition products and extract specific data fields.
            If a field is not found in the markdown file, assign it the value `None`. 
            Return only the extracted data in JSON format with the following structure:
            { "price": null, "sku": null, "upc": null, "mpn": null, "stock": null, "available_quantities": null}

            Provided markdown:
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
        print(response.choices[0].message.content)
