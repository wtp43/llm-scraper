import asyncio
import re
from concurrent.futures import ThreadPoolExecutor

import html2text
from bs4 import BeautifulSoup
from playwright.async_api import Browser, async_playwright
from playwright.sync_api import sync_playwright


class ScraperClient:
    def __init__(self, cpu_count=1):
        self.cpu_count = cpu_count
        self.text_maker = html2text.HTML2Text()
        self.text_maker.skip_internal_links = True
        self.text_maker.ignore_emphasis = True
        self.text_maker.single_line_break = True
        self.text_maker.escape_snob = True
        self.text_maker.drop_white_space = True

    def run(self, urls, slow_mo=0):
        htmls = asyncio.run(self.batch_scrape(urls, slow_mo=slow_mo))
        htmls = self.batch_process_html(htmls)
        return htmls

    async def batch_scrape(self, urls, slow_mo=0) -> list[str]:
        # higher slow_mo is required for js pages
        htmls = None

        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(
                headless=False, channel="chrome", slow_mo=slow_mo
            )
            async with asyncio.TaskGroup() as tg:
                # While waiting, new tasks may still be added to the group (for example, by passing tg into one of the coroutines and calling tg.create_task() in that coroutine). Once the last task has finished and the async with block is exited, no new tasks may be added to the group.
                tasks = [tg.create_task(self.worker(browser, url)) for url in urls]

            htmls = [task.result() for task in tasks]
        return htmls

    def batch_process_html(self, htmls: list[str]) -> list[str]:
        processed_htmls = htmls
        # process has more initial overhead than thread:
        # new processes create a complete copy of their parent process
        # to have access to program state
        with ThreadPoolExecutor() as executor:
            processed_htmls = list(executor.map(self.clean_html, htmls))
        return processed_htmls

    async def worker(self, browser: Browser, url: str):
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(url)
        return await page.content()

    def sync_scrape(self, url: str):
        content = None
        with sync_playwright() as p:
            # Channel can be "chrome", "msedge", "chrome-beta", "msedge-beta" or "msedge-dev".
            browser = p.chromium.launch(channel="chrome", headless=False, slow_mo=1000)
            page = browser.new_page()
            page.goto(url)
            content = page.content()
            browser.close()
        return content

    def clean_html(self, html: str):
        # benchmark html.parser vs lxml
        soup = BeautifulSoup(html, "html.parser")
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
            # Remove tags
            data.decompose()

        soup.smooth()
        content = str(soup.prettify())
        # TODO: return markdown directly
        return content

    def html_to_markdown(self, html: str):
        text = self.text_maker.handle(html)
        lines = text.split("\n")
        text = [line for line in lines if line]
        # text = re.sub(r"^\n$", "", text)
        return "\n".join(text)

    def batch_convert_html_to_markdown(self, htmls):
        markdown_docs = []
        with ThreadPoolExecutor() as executor:
            markdown_docs = list(executor.map(self.html_to_markdown, htmls))
        return markdown_docs
