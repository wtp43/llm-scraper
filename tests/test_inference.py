from pathlib import Path

import pytest

from llm_scraper.inference_worker import InferenceWorker

# vllm serve Qwen/Qwen2.5-32B-Instruct-GPTQ-Int4  --tensor-parallel-size 2 --max-model-len 32768


@pytest.fixture
def inference_worker():
    return InferenceWorker()


def test_inference(inference_worker):
    md = Path("tests/output/243-winchester-80-grain-super-x-20rds.md").read_text()
    response = inference_worker.extract_ammo_info(md)
    print(response)
    md = Path("tests/output/cci-blazer-brass-38-spl-125-grain-fmj.md").read_text()
    response = inference_worker.extract_ammo_info(md)
    print(response)

    assert True
