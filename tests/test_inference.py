import os
from pathlib import Path

import pytest

from llm_scraper.inference_worker import InferenceWorker

# vllm serve Qwen/Qwen2.5-32B-Instruct-GPTQ-Int4  --tensor-parallel-size 2 --max-model-len 32768


def get_md_files(directory):
    return [file for file in os.listdir(directory) if file.endswith(".md")]


@pytest.fixture
def inference_worker():
    return InferenceWorker()


def test_inference(inference_worker):
    with open("tests/output/inference_output.json", "w", encoding="utf-8") as file:
        response = inference_worker.xml()
        file.write(response)


# def test_inference(inference_worker):
#     with open("tests/output/inference_output.json", "w", encoding="utf-8") as file:
#         for f in get_md_files("tests/output"):
#             md = Path("tests/output", f).read_text()
#             response = inference_worker.extract_ammo_info(md)
#             file.write(response)
#     assert True
