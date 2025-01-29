import re
from asyncio import sleep

from playwright.async_api import Locator, Page, expect


class UserInformation:
    def __init__(self, first_name, last_name, address, city, state, zip_code):
        self.first_name = first_name
        self.last_name = last_name
        self.address = address
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.phone = "555-555-5555"
        self.email = "2LQa9@gmail.com"
        self.firearms_license = "123456789"
        self.dob = "2000-01-01"


# Take a screenshot and save it to a file
# page.screenshot(path="snapshot.png")
class ShippingEstimator:
    def __init__(self, page: Page):
        self.page = page

    async def add_to_cart(self, quantity: int = 3) -> None:

        if quantity > 1:
            # quantity can be a spinbutton

            spin_button = await self.page.get_by_role(
                "spinbutton",
                name=re.compile(r"\b(qty|quantity)", re.IGNORECASE),
            ).all()
            if spin_button:
                await spin_button[0].fill(str(quantity))

            textbox = await self.page.get_by_role(
                "textbox", name=re.compile(r"\b(qty|quantity)", re.IGNORECASE)
            ).all()
            if textbox:
                await textbox[0].fill(str(quantity))

            locator = await (
                self.page.locator("div")
                .filter(has_not_text=re.compile(r"\brelated products", re.IGNORECASE))
                .filter(has_text=re.compile(r"\b(qty|quantity)", re.IGNORECASE))
                .get_by_role(
                    "button", name=re.compile(r"\b(cart|add to cart)", re.IGNORECASE)
                )
                .all()
            )
            if locator:
                await locator[0].click()
        # await self.page.get_by_role(
        #     "button", name=re.compile(r"\b(cart|add to cart)", re.IGNORECASE)
        # ).click()

    async def handler(self, locator: Locator):
        await locator.click()

    async def age_verification_handler(self, locator: Locator) -> None:
        await locator.click()

    async def email_login_handler(self, locator: Locator) -> None:
        pass

    async def assert_shipping_quote(self) -> bool:
        await sleep(1)
        e = await self.page.get_by_role(
            "textbox", name=re.compile(r"\b(postal|zip)", re.IGNORECASE)
        ).all()
        if e:
            return True
        else:
            return False

    async def checkout(self) -> None:
        # could be iframe
        # await page.get_by_role("button").get_by_text("checkout").click()
        # await page.get_by_text("View Cart").click()

        # some shipping estimators happen before the payment page: check bulkammo.com
        # TODO: it might be easier to check for the existence of a shipping estimate instead
        if re.match(r"\b(checkout|cart)", self.page.url):
            return

        await self.page.get_by_role("link").get_by_text("checkout").first.click()

    async def fill_email_label(self, user: UserInformation) -> None:
        # there are some weird sites with an email label instead of textbox
        email_label = await self.page.get_by_label("email").all()
        if email_label:
            await email_label[0].fill(user.email)

        # Email should be filled first. Other form fields might not show if
        # no email is given
        await sleep(2)
        for locator in await self.page.get_by_role(
            "textbox", name=re.compile(r"\b(email)", re.IGNORECASE)
        ).all():
            await locator.fill(user.email)

        # there might exist a continue button
        # 'continue shopping' should be avoided however

        continue_button = await self.page.get_by_role(
            "button",
            name=re.compile(r"\b(continue|next)\b(?!\s+shopping)", re.IGNORECASE),
        ).all()

        if continue_button:
            await continue_button[0].click()

    async def fill_shipping_address(self, user: UserInformation) -> None:
        # There can be multiple elements with the same name corresponding to
        # a billing and shipping address. we should fill all locators
        # All fields are case insensitive, unless exact is set to true

        await sleep(2)
        # First Name
        for locator in await self.page.get_by_role("textbox", name="first name").all():
            await locator.fill(user.first_name)

        # Last Name
        for locator in await self.page.get_by_role("textbox", name="last name").all():
            await locator.fill(user.last_name)

        # Phone number
        for locator in await self.page.get_by_role(
            "textbox", name=re.compile(r"\b(phone|mobile)", re.IGNORECASE)
        ).all():
            await locator.fill(user.phone)

        # Street address
        for locator in await self.page.get_by_role(
            "textbox",
            name=re.compile(r"\b(?!\s+shopping)\b(address)", re.IGNORECASE),
        ).all():
            await locator.fill(user.address)

        # City/State
        for locator in await self.page.get_by_role(
            "textbox", name=re.compile(r"\b(town|city)", re.IGNORECASE)
        ).all():
            await locator.fill(user.city)

        # Zip code
        for locator in await self.page.get_by_role(
            "textbox", name=re.compile(r"\b(postal|zip)", re.IGNORECASE)
        ).all():  # use _or to fill also postal
            await locator.fill(user.zip_code)

        # firearms license
        for locator in await self.page.get_by_role(
            "textbox", name=re.compile(r"\b(firearms|license)", re.IGNORECASE)
        ).all():  # use _or to fill also postal
            await locator.fill(user.firearms_license)

            # date of birth
            # TODO: some websites disable textbox and only allow datepicker...
            for locator in await self.page.get_by_role(
                "textbox",
                name=re.compile(r"\b(age|date of birth|yyyy-mm-dd)", re.IGNORECASE),
            ).all():
                # most likely a datepicker
                try:
                    await expect(locator).not_to_have_attribute(
                        name="readonly", value=re.compile(r".*")
                    )
                    await locator.fill(user.dob)
                except Exception:
                    continue

        # sometimes, the province does not have a textbox and must be clicked
        # only click if combobox

        province_combobox = await self.page.get_by_role(
            "combobox",
            name=re.compile(r"\b(province)", re.IGNORECASE),
        ).all()

        for combobox in province_combobox:
            await combobox.click()
            await sleep(1)
            # option = await self.page.get_by_role(
            #     "option", name=re.compile(rf"\b({user.state})", re.IGNORECASE)
            # ).all()
            # if option:
            #     await option[0].click()

            label = await self.page.get_by_label("province").all()
            if label:
                await self.page.get_by_label("province").select_option(user.state)
            await combobox.click()

        # use the combobox to select the province

        # click if needed to get shipping quote

        quote_button = await self.page.get_by_role(
            "button", name=re.compile(r"\b(estimate|quote)", re.IGNORECASE)
        ).all()
        if quote_button:
            await quote_button[0].click()

    # express checkout
    # captchas...
    # age verifier
    # required account before shipping is estimated
    # some may require email to be filled first
    # include country which can also be a combobox

    async def run(self, url: str, user: UserInformation) -> None:

        await self.page.goto(url)

        await self.add_to_cart()
        # await page.add_locator_handler(
        #     page.get_by_label("Close"), self.handler, times=1
        # )

        # only checkout if shipping quote is not found yet
        if not await self.assert_shipping_quote():
            await self.checkout()

        # .all is finicky. wait until all fields load before filling
        await sleep(1)
        await self.fill_email_label(user)
        await self.fill_shipping_address(user)
