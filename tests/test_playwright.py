import os
import re
from asyncio import sleep

import pytest
from playwright.async_api import Browser, Page, async_playwright, expect

from llm_scraper.shipping_estimator import ShippingEstimator, UserInformation

os.environ["PWDEBUG"] = "0"

urls = [
    "https://www.gotenda.com/product/consignment-blue-line-870-12-ga-28-pump-action-shotgun-51-excellent/",
    "https://www.gotenda.com/product/stv-scorpio-7-62x39-fmc-ammo-can-of-300/",
    "https://canadafirstammo.ca/cci-blazer-brass-38-spl-125-grain-fmj/",
    "https://northernelitefirearms.ca/product/243-winchester-80-grain-super-x-20rds/",
    "https://canadafirstammo.ca/federal-american-eagle-handgun-380-auto/",
    "https://theammosource.com/remington-32-20-winchester-100-grain-lead-50-rounds/",
    "https://www.bullseyenorth.com/shop/cci-speer-gold-dot-223-remington-62-grain-soft-point-box-of-20-33361/",  # broken
    "https://blackbasin.com/hornady-80237-american-gunner-hollow-point-55-grain-223-remington/",  # broken: has multiple quantities and prices
    "https://www.rdsc.ca/firearms-ammunition/ammunition/aguila-ammo-22lr-20-grain-colibri-420-fps-50-rounds.html",  # simple
    "https://www.cheaperthandirt.com/armscor-usa-.22-lr-ammunition-500-rounds-hp-36-grains/fc-amm-0551-5132.html",  # able to get bulk quantity pricing
    "https://g4cgunstore.com/product/challenger-12ga-2-3-4-tactical-slug-175-pack-magnum/",
    "https://ammo.com/rifle/223-rem-ammo",  # this website doesn't have individual pages for ammo
    "https://www.midwayusa.com/product/2090655809?pid=721427",
    "https://www.rangeviewsports.ca/product/norinco-308-win-rifle-ammo-147gr-fmj-steel-case-500rds/",
    "https://www.targetsportsusa.com/cci-blazer-40-sw-ammo-165-grain-full-metal-jacket-aluminum-3589-p-702.aspx",
]


@pytest.fixture(scope="function")
def user_usa():
    return UserInformation(
        "John",
        "Doe",
        "10111 Niagara Fls Blvd",
        "Niagara Falls",
        "NY",
        "14304",
    )


@pytest.fixture(scope="function")
def user_ca():
    return UserInformation(
        "John",
        "Doe",
        "243 Carlton Road",
        "Unionville",
        "Ontario",
        "L3R 3M3",
    )


@pytest.fixture(scope="session")
async def browser():
    async with async_playwright() as playwright:
        chromium = playwright.chromium

        browser = await chromium.launch(headless=False)
        yield browser


@pytest.mark.asyncio(loop_scope="session")
class TestShippingEstimator:
    async def assert_shipping_provider(self, page: Page) -> AssertionError:
        locator = page.locator("body")
        return await expect(locator).to_contain_text(
            re.compile(r"\b(fedex|ups)", re.IGNORECASE)
        )

    async def test_quote_on_cart_page_usa(
        self,
        browser: Browser,
        user_usa: UserInformation,
    ):
        # shipping estimate element is on the shopping cart page before checkout
        url = "https://www.bulkammo.com/200-rounds-of-6-5-creedmoor-ammo-by-hornady-in-field-box-140gr-bthp"

        page = await browser.new_page()
        shipping_estimator = ShippingEstimator(page)
        await shipping_estimator.run(url, user_usa)

        await self.assert_shipping_provider(page)
        await page.close()

    async def test_quote_on_checkout_page_ca(
        self,
        browser: Browser,
        user_ca: UserInformation,
    ):
        # uses click_option_state
        url = "https://www.gotenda.com/product/cci-noise-blanks-22-short-box-of-100/"
        page = await browser.new_page()
        shipping_estimator = ShippingEstimator(page)
        await shipping_estimator.run(url, user_ca)

        await self.assert_shipping_provider(page)
        await page.close()

    async def test_checkout_page_ca(
        self,
        browser: Browser,
        user_ca: UserInformation,
    ):
        # uses select_option_state
        url = "https://canadafirstammo.ca/federal-american-eagle-handgun-380-auto/"

        page = await browser.new_page()
        shipping_estimator = ShippingEstimator(page)
        await shipping_estimator.run(url, user_ca)

        await self.assert_shipping_provider(page)
        await page.close()
