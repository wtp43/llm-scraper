import json
from typing import List

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from pydantic import BaseModel, Field
from scrapegraphai.graphs import DocumentScraperGraph, SmartScraperGraph
from scrapegraphai.utils import prettify_exec_info


class Ammo(BaseModel):
    name: str = Field(description="The name of the ammo")
    original_price: float = Field(description="The price of the ammo")
    manufacturer: str = Field(description="The manufacturer of the ammo")
    rounds: int = Field(description="The description of the dish")
    sale_price: float = Field(description="The discounted price of the ammo")
    bullet_type: str = Field(description="The type of the bullet")
    grain: int = Field(description="The grain of the bullet")
    stock_available: int = Field(description="How much stock the vendor has")
    sku: str = Field(description="SKU or part # of the ammunition")
    calibre: str = Field(description="Calibre of the bullet")


class Quantity(BaseModel):
    rounds: int
    price_per_box: float


class Price(BaseModel):
    name: str = Field(description="The name of the ammo")
    current_price: float = Field(description="The price of the ammo")
    sale_price: float = Field(description="The discounted price of the ammo")
    price: float = Field(description="The price of the product")
    stock_available: int = Field(description="How much stock the vendor has")
    sku: str = Field(description="SKU or part # of the ammunition")
    upc: str = Field(description="UPC of the ammunition")
    item_number: str = Field(description="Item or part # of the bullet")
    quantity_options: list[Quantity]


class Prices(BaseModel):
    Prices: list[Price]


class Ammos(BaseModel):
    ammos: list[Ammo]


class HTMLClient:
    def __init__(self):
        pass

    def playwright_extract(self, url):
        content = None
        with sync_playwright() as p:
            # Channel can be "chrome", "msedge", "chrome-beta", "msedge-beta" or "msedge-dev".
            browser = p.chromium.launch(channel="chrome", headless=False, slow_mo=1000)
            page = browser.new_page()
            page.goto(url)
            content = page.content()
            browser.close()
        return content


class ScraperGraph:
    def __init__(self, source, schema):
        self.graph_config = {
            "llm": {
                # "model": "ollama/codellama:7b-code",
                # "model": "ollama/qwen2.5-coder:7b",#missed sku at 8192 tokens for source[0], best at 2048
                "model": "ollama/qwen2.5:72b-instruct",  #
                # "model": "ollama/qwen2.5-coder:32b",
                # "model": "ollama/qwen2.5-coder:3b", #20s, hallucinates stock
                #    "model": "ollama/codegeex4",# 10s but missed price with 1024, 2048 works good
                "format": "json",
                # "model_tokens":500,
                # "model_tokens":1024,
                # "model_tokens": 1300,
                #    "model_tokens": 2048,
                "model_tokens": 4096,
                #    "model_tokens": 8192,
                # "model_tokens":32768,
                # "model_tokens":131072,
                # "model_tokens":128000,
                # "model_tokens":163840,
                "temperature": 0,
                "base_url": "http://localhost:11434",
            },
            "embeddings": {
                "model": "ollama/nomic-embed-text",
                "temperature": 0,
                "base_url": "http://localhost:11434",
            },
            "verbose": False,
            "headless": False,
            # "loader_kwargs": {
            #     # "requires_js_support": True,
            #     "timeout": 180,  # Increase timeout
            #     "retry_limit": 3,
            #     "slow_mo": 5000,
            # },
        }
        self.scraper_graph = DocumentScraperGraph(
            # self.scraper_graph = SmartScraperGraph(
            # prompt="Extract the name, description of the product, cost, stock, availability and shipping cost from this product page.",
            # prompt="Extract the exact name, the manufacturer or brand, sku,part number, item number, listed price, sale price, rounds per box, stock available for purchase, and any other relevant information about this ammunition being sold.",
            # prompt= "Extract all ammo information about the ammo STV Scorpio 7.62x39",
            # prompt="Extract all price information and SKU or item number about the ammo that appears the most on this product webpage.",
            # prompt="Extract all price information and SKU or item number about the ammo that appears in the url on this product webpage.",
            # prompt="Extract all price information and SKU or item number about the ammo from the main div on this product webpage.",
            prompt="Extract all price information and SKU or item number about the ammo and return it in a json.",
            # prompt="Extract all price information and SKU or item number on this product webpage.",
            # prompt="Extract all price information and SKU or item number about all the ammo from the main div on this product webpage.",
            # prompt="Return all info about ammunition products being sold.",
            # prompt="Extract all price information and SKU or item number about the ammo being sold.",
            # prompt="List all ammo and their product information from the vendor webpage.",
            # prompt="Extract all products and their relevant information from this webpage.",
            # prompt="List me all the items",
            # prompt="Return the data about the products listed, including product id and product name",
            # prompt="List all products and their price",
            # prompt="what is the price of this item in the webpage?",
            source=source,
            config=self.graph_config,
            schema=schema,
        )

    def get_response(self):
        resp = self.scraper_graph.run()
        graph_exec_info = self.scraper_graph.get_execution_info()
        print(prettify_exec_info(graph_exec_info))
        return json.dumps(resp, indent=4)


def clean_html(url):
    client = HTMLClient()
    html_doc = client.playwright_extract(url)
    soup = BeautifulSoup(html_doc, "html.parser")
    for data in soup(
        [
            "script",
            "a",
            "iframe",
            "input",
            "link",
            "button",
            "footer",
            "style",
            "head",
            "img",
            "svg",
            "symbol",
            "path",
            "nav",
        ]
    ):
        # for data in soup(['script', 'a','iframe', 'input', 'link', 'button', 'form', 'ins', 'textarea', 'footer', 'head', 'style', 'img', 'svg']):
        # for data in soup(['script', 'a', 'iframe', 'input', 'link', 'form', 'ins', 'footer', 'symbol', 'img']):
        # Remove tags
        data.decompose()

    soup.smooth()
    content = str(soup.prettify())
    filename = url.rstrip("/").split("/")[-1] + ".html"
    print(filename, len(content))
    with open(filename, "w") as file:
        file.write(content)
    return content


def main():
    sources = [
        # "https://www.gotenda.com/product/stv-scorpio-7-62x39-fmc-ammo-can-of-300/",
        # "https://canadafirstammo.ca/cci-blazer-brass-38-spl-125-grain-fmj/",
        # "https://northernelitefirearms.ca/product/243-winchester-80-grain-super-x-20rds/",
        # "https://canadafirstammo.ca/federal-american-eagle-handgun-380-auto/",
        # "https://theammosource.com/remington-32-20-winchester-100-grain-lead-50-rounds/",
        # "https://www.bullseyenorth.com/shop/cci-speer-gold-dot-223-remington-62-grain-soft-point-box-of-20-33361/",# broken# broken
        # "https://blackbasin.com/hornady-80237-american-gunner-hollow-point-55-grain-223-remington/",#broken: has multiple quantities and prices
        # "https://www.rdsc.ca/firearms-ammunition/ammunition/aguila-ammo-22lr-20-grain-colibri-420-fps-50-rounds.html",# simple
        # "https://www.cheaperthandirt.com/armscor-usa-.22-lr-ammunition-500-rounds-hp-36-grains/fc-amm-0551-5132.html",#able to get bulk quantity pricing
        # "https://g4cgunstore.com/product/challenger-12ga-2-3-4-tactical-slug-175-pack-magnum/",
        # "https://ammo.com/rifle/223-rem-ammo", #this website doesn't have individual pages for ammo
        "https://www.midwayusa.com/product/2090655809?pid=721427",
        "https://www.rangeviewsports.ca/product/norinco-308-win-rifle-ammo-147gr-fmj-steel-case-500rds/",
        "https://www.targetsportsusa.com/cci-blazer-40-sw-ammo-165-grain-full-metal-jacket-aluminum-3589-p-702.aspx",
    ]

    from pathlib import Path

    # content = Path('markdown.md').read_text()
    scraper_graph = ScraperGraph("markdown.md", Price)
    print(scraper_graph.get_response())
    return

    for url in sources:
        content = clean_html(url)
        # content = url
        # continue
        scraper_graph = ScraperGraph(content, Price)
        print(scraper_graph.get_response())
        print(url)


if __name__ == "__main__":
    main()
# proxmox vm must have host flag in cpu
# https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#installation
# sudo docker run -d --gpus=all -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
# sudo docker exec -it ollama ollama pull nomic-embed-text
# sudo docker exec -it ollama ollama run qwen2.5-coder:7b
# sudo docker start ollama
# sudo docker start open-webui
