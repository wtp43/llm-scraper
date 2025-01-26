import pytest

from llm_scraper.scraper_client import ScraperClient


@pytest.fixture
def urls():
    urls = [
        # "https://www.gotenda.com/product/stv-scorpio-7-62x39-fmc-ammo-can-of-300/",
        "https://canadafirstammo.ca/cci-blazer-brass-38-spl-125-grain-fmj/",
        "https://northernelitefirearms.ca/product/243-winchester-80-grain-super-x-20rds/",
        "https://canadafirstammo.ca/federal-american-eagle-handgun-380-auto/",
        "https://theammosource.com/remington-32-20-winchester-100-grain-lead-50-rounds/",
        # "https://www.bullseyenorth.com/shop/cci-speer-gold-dot-223-remington-62-grain-soft-point-box-of-20-33361/",  # broken
        # "https://blackbasin.com/hornady-80237-american-gunner-hollow-point-55-grain-223-remington/",  # broken: has multiple quantities and prices
        # "https://www.rdsc.ca/firearms-ammunition/ammunition/aguila-ammo-22lr-20-grain-colibri-420-fps-50-rounds.html",  # simple
        # "https://www.cheaperthandirt.com/armscor-usa-.22-lr-ammunition-500-rounds-hp-36-grains/fc-amm-0551-5132.html",  # able to get bulk quantity pricing
        # "https://g4cgunstore.com/product/challenger-12ga-2-3-4-tactical-slug-175-pack-magnum/",
        # "https://ammo.com/rifle/223-rem-ammo", #this website doesn't have individual pages for ammo
        # "https://www.midwayusa.com/product/2090655809?pid=721427",
        # "https://www.rangeviewsports.ca/product/norinco-308-win-rifle-ammo-147gr-fmj-steel-case-500rds/",
        # "https://www.targetsportsusa.com/cci-blazer-40-sw-ammo-165-grain-full-metal-jacket-aluminum-3589-p-702.aspx",
    ]
    return urls


@pytest.fixture()
def scraper_client():
    """Returns default scraper client"""
    return ScraperClient()


def write_to_file(path: str, content: str) -> None:
    with open(path, "w") as file:
        file.write(content)


def test_scraper(scraper_client, urls):
    htmls = scraper_client.run(urls=urls, slow_mo=0)
    assert len(htmls) == len(urls)
    markdown_docs = scraper_client.batch_convert_html_to_markdown(htmls)
    for i in range(len(urls)):
        base_path = "tests/output/" + urls[i].rstrip("/").split("/")[-1]
        write_to_file(base_path + ".html", htmls[i])
        write_to_file(base_path + ".md", markdown_docs[i])
