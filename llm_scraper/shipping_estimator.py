import re
from asyncio import TaskGroup, sleep, timeout

from playwright.async_api import Locator, Page, expect

from util.decorators import ignore_timeout, timeit


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
    def __init__(
        self,
        page: Page,
        default_fill_timeout: int = 100,
        default_click_timeout=3000,
    ):
        self.page = page
        self.default_fill_timeout = default_fill_timeout
        self.default_click_timeout = default_click_timeout

    async def add_to_cart(self, quantity: int = 2) -> None:

        if quantity > 1:
            # quantity can be a spinbutton

            spin_button = await self.page.get_by_role(
                "spinbutton",
                name=re.compile(r"\b(qty|quantity|stock)", re.IGNORECASE),
            ).all()
            if spin_button:
                await spin_button[0].fill(
                    str(quantity), timeout=self.default_fill_timeout
                )

            textbox = await self.page.get_by_role(
                "textbox", name=re.compile(r"\b(qty|quantity)", re.IGNORECASE)
            ).all()
            if textbox:
                await textbox[0].fill(str(quantity), timeout=self.default_fill_timeout)

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
            # await locator[0].click(force=True)
            await locator[0].click()

        # try:
        #     add_to_cart_button = await self.page.get_by_role(
        #         "button", name=re.compile(r"\b(add to cart)", re.IGNORECASE)
        #     ).all()
        #     if add_to_cart_button:
        #         await expect(add_to_cart_button[0]).to_be_focused()
        #         await add_to_cart_button[0].click()
        # except:
        #     pass

    async def close_dialog_handler(self) -> None:
        await self.page.get_by_role(
            "button", name=re.compile(r"(close|dialog|cancel|exit|x)", re.IGNORECASE)
        ).click(timeout=10000)

    async def age_verification_popup_handler(self) -> None:
        await self.page.get_by_role(
            "button", name=re.compile(r"(yes)", re.IGNORECASE)
        ).click(timeout=10000)

    async def assert_shipping_quote(self) -> bool:
        await sleep(0.5)
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

    @ignore_timeout
    async def fill_email_label(self, user: UserInformation) -> None:
        # there are some weird sites with an email label instead of textbox
        try:
            email_label = await self.page.get_by_label("email").all()

            if email_label:
                await expect(email_label[0]).to_be_visible(
                    timeout=self.default_fill_timeout
                )
                await email_label[0].fill(user.email, timeout=self.default_fill_timeout)
        except AssertionError:
            pass

        # Email should be filled first. Other form fields might not show if
        # no email is given
        for locator in await self.page.get_by_role(
            "textbox", name=re.compile(r"(email)", re.IGNORECASE)
        ).all():
            try:
                await expect(locator).to_be_visible(timeout=self.default_fill_timeout)
                await locator.fill(user.email, timeout=self.default_fill_timeout)
            except AssertionError:
                continue

        # there might exist a continue button
        # 'continue shopping' should be avoided however

        continue_button = await self.page.get_by_role(
            "button",
            # TODO:
            name=re.compile(r"(continue|next)(?!\s+shopping)", re.IGNORECASE),
        ).all()

        if continue_button:
            await continue_button[0].click(timeout=self.default_click_timeout)

    @ignore_timeout
    async def click_option_state(self, user: UserInformation) -> None:

        # in the case that the combobox is a
        # separate element from the combobox element
        # or if select_option is not available due
        # to lack of <select>

        try:
            province_combobox = await self.page.get_by_role(
                "combobox",
                name=re.compile(r"(province)", re.IGNORECASE),
            ).all()
            for combobox in province_combobox:
                await combobox.click(timeout=100)
            option = await self.page.get_by_role(
                "option", name=re.compile(rf"({user.state})", re.IGNORECASE)
            ).all()
            if option:
                tag = await option[0].evaluate("el => el.tagName")
                if tag != "SELECT":
                    await option[0].click(timeout=self.default_fill_timeout)
        except Exception:
            pass

    @ignore_timeout
    async def fill_full_name(self, user: UserInformation) -> None:
        try:
            # First Name
            for locator in await self.page.get_by_role(
                "textbox", name="first name"
            ).all():
                await locator.fill(user.first_name, timeout=self.default_fill_timeout)

            # Last Name
            for locator in await self.page.get_by_role(
                "textbox", name="last name"
            ).all():
                await locator.fill(user.last_name, timeout=self.default_fill_timeout)
        except Exception:
            pass

    @ignore_timeout
    async def fill_state_combobox(self, user: UserInformation) -> None:
        # TODO:
        # sometimes, the province does not have a textbox and must be clicked

        await self.page.get_by_role(
            "combobox", name=re.compile(r"(province)", re.IGNORECASE)
        ).click(timeout=self.default_click_timeout)
        await sleep(1)
        await self.page.get_by_role(
            "combobox", name=re.compile(rf"({user.state})", re.IGNORECASE)
        ).and_(self.page.get_by_role("textbox")).fill(
            "Ontario", timeout=self.default_click_timeout
        )

    @ignore_timeout
    async def fill_zip(self, user: UserInformation) -> None:
        # Zip code
        for locator in await self.page.get_by_role(
            "textbox", name=re.compile(r"(postal|zip)", re.IGNORECASE)
        ).all():  # use _or to fill also postal
            await locator.fill(user.zip_code, timeout=self.default_fill_timeout)

    @ignore_timeout
    async def fill_city(self, user: UserInformation) -> None:
        # City
        for locator in await self.page.get_by_role(
            "textbox", name=re.compile(r"(town|city)", re.IGNORECASE)
        ).all():
            await locator.fill(user.city, timeout=self.default_fill_timeout)

    @ignore_timeout
    async def fill_shipping_address(self, user: UserInformation) -> None:
        # Street address
        for locator in await self.page.get_by_role(
            "textbox",
            name=re.compile(r"(?<!(email ))(address)", re.IGNORECASE),
        ).all():
            await locator.fill(user.address, timeout=self.default_fill_timeout)

    @ignore_timeout
    async def fill_phone_number(self, user: UserInformation) -> None:
        # Phone number
        for locator in await self.page.get_by_role(
            "textbox", name=re.compile(r"(phone|mobile)", re.IGNORECASE)
        ).all():
            await locator.fill(user.phone, timeout=self.default_fill_timeout)

    @ignore_timeout
    async def fill_firearms_license(self, user: UserInformation) -> None:
        # firearms license
        for locator in await self.page.get_by_role(
            "textbox", name=re.compile(r"(firearms|license)", re.IGNORECASE)
        ).all():
            await locator.fill(user.firearms_license, timeout=self.default_fill_timeout)

    @ignore_timeout
    async def fill_dob(self, user: UserInformation) -> None:
        # date of birth
        # TODO: some websites disable textbox and only allow datepicker...
        for locator in await self.page.get_by_role(
            "textbox",
            name=re.compile(r"(age|date of birth|yyyy-mm-dd)", re.IGNORECASE),
        ).all():
            try:
                # most likely a datepicker if not editable
                await expect(locator).to_be_editable(timeout=self.default_fill_timeout)
                await locator.fill(user.dob, timeout=self.default_fill_timeout)
            except AssertionError:
                continue

    @ignore_timeout
    async def select_option_state(self, user: UserInformation) -> None:
        for locator in await self.page.get_by_label(
            re.compile(r"(state|province)", re.IGNORECASE)
        ).all():
            try:
                tag = await locator.evaluate("el => el.tagName")
                if tag == "SELECT":
                    await locator.select_option(
                        # TODO: enum
                        ["ontario", "ON", "on", "Ontario"],
                        timeout=self.default_click_timeout,
                    )
                    return
            except Exception:
                pass

    async def add_page_handler(self, element, handler) -> None:
        await self.page.add_locator_handler(
            element,
            handler,
            no_wait_after=True,
        )

    async def click_quote_shipping(self) -> None:
        quote_button = await self.page.get_by_role(
            "button", name=re.compile(r"(estimate|quote)", re.IGNORECASE)
        ).all()
        if quote_button:
            await quote_button[0].click(timeout=self.default_fill_timeout)

    async def fill_user_information(self, user: UserInformation) -> None:
        # There can be multiple elements with the same name corresponding to
        # a billing and shipping address. we should fill all locators
        # All fields are case insensitive, unless exact is set to true

        # express checkout
        # captchas...
        # age verifier
        # required account before shipping is estimated
        # some may require email to be filled first
        # include country which can also be a combobox
        await self.fill_full_name(user)

        await self.fill_phone_number(user)
        await self.fill_shipping_address(user)
        await self.fill_city(user)
        await self.fill_zip(user)

        await self.fill_dob(user)
        await self.fill_firearms_license(user)

        await self.select_option_state(user)
        await self.click_option_state(user)

    async def init_handlers(self):
        async with TaskGroup() as tg:
            page_handler_tasks = []
            page_handler_tasks.append(
                tg.create_task(
                    self.add_page_handler(
                        self.page.get_by_text(
                            re.compile(r"(emails|newsletter|sign up)", re.IGNORECASE)
                        ),
                        self.close_dialog_handler,
                    ),
                )
            )

            page_handler_tasks.append(
                tg.create_task(
                    self.add_page_handler(
                        self.page.get_by_text(
                            re.compile(
                                r"(18).*(years)",
                                re.IGNORECASE,
                            )
                        ),
                        self.age_verification_popup_handler(),
                    ),
                )
            )

    async def go_to(self, url: str) -> None:
        # wait_until="domcontentloaded" will not wait on slow loading images
        # await self.init_handlers()
        await self.page.goto(url, wait_until="load")
        await self.page.add_locator_handler(
            self.page.get_by_text(
                re.compile(
                    r"(verify)",
                    re.IGNORECASE,
                )
            ),
            self.age_verification_popup_handler,
            no_wait_after=True,
        )

    @timeit
    async def run(self, url: str, user: UserInformation) -> None:

        # wait_until="domcontentloaded" will not wait on slow loading images
        await self.page.goto(url, wait_until="domcontentloaded")

        await sleep(3)
        await self.add_to_cart()
        # await page.add_locator_handler(
        #     page.get_by_label("Close"), self.handler, times=1
        # )

        # only checkout if shipping quote is not found yet
        if not await self.assert_shipping_quote():
            await self.checkout()

        # .all is finicky. wait until all fields load before filling
        # TODO: sleep isn't robust, use web assertions
        await sleep(2)
        await self.page.wait_for_load_state("load")
        await self.fill_email_label(user)
        await self.page.wait_for_load_state("load")
        await sleep(1)
        await self.fill_user_information(user)
        await self.click_quote_shipping()
        await self.page.wait_for_load_state("domcontentloaded")
