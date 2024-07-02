from datetime import datetime
from dateutil import parser
import dateutil.relativedelta
from robocorp import browser, workitems
from RPA.Excel.Files import Files
from pathlib import Path
import re
import requests

class ProcessNews:
    def __init__(self, config):
        self.browser = browser
        self.excel = Files()
        self.config = config
        self.site_url = config.get("site_url")

    def consume_news_parameters(self):
        """Consume work-items created by params"""
        self.browser.configure(
            slowmo=100,
            )

        self.create_excel_file()
        self.open_news_website()

        for item in workitems.inputs:
            parameters_data = item.payload["parameters_data"]
            print(parameters_data)
            self.searching_phrase(parameters_data["search_phrase"])
            self.filter_news_results(parameters_data["news_category"])
            page_results = self.get_page_number()
            for i in range(page_results):
                news_results = self.get_news_results()
                is_break = self.process_news_results(news_results, parameters_data["number_months"], 
                                                     parameters_data["search_phrase"])
                if is_break:
                    break
            self.go_home_website()

    def open_news_website(self):
        """Navigates to the given URL"""
        self.browser.goto(self.site_url)
        page = self.browser.page()
        page.wait_for_load_state(state="load")

    def go_home_website(self):
        """Go back to home page"""
        page = self.browser.page()
        page.wait_for_load_state()
        page.click("body > ps-header > header > div.absolute.left-1\/2.-translate-x-1\/2")

    def submit_search(self):
        """Click 'Search' button"""
        submit_search_button = "body > ps-header > header > div.flex.\[\@media_print\]\:hidden > div.ct-hidden.fixed.md\:absolute.top-12\.5.right-0.bottom-0.left-0.z-25.bg-header-bg-color.md\:top-15.md\:bottom-auto.md\:h-25.md\:shadow-sm-2 > form > button"

        page = self.browser.page()
        page.click(submit_search_button)
        page.wait_for_load_state(state="load")

    def searching_phrase(self, search_phrase):
        """Type 'search phrase' value into website"""
        search_button = "body > ps-header > header > div.flex.\[\@media_print\]\:hidden > button"
        search_form = "body > ps-header > header > div.flex.\[\@media_print\]\:hidden > div.ct-hidden.fixed.md\:absolute.top-12\.5.right-0.bottom-0.left-0.z-25.bg-header-bg-color.md\:top-15.md\:bottom-auto.md\:h-25.md\:shadow-sm-2 > form > label > input"

        page = self.browser.page()
        page.wait_for_load_state(state="load")
        page.click(search_button)
        page.fill(search_form, search_phrase)
        self.submit_search()

    def filter_news_results(self, news_category):
        """Filter news results by category and newest"""
        sort_filter = "Newest"
        page = self.browser.page()
        page.wait_for_load_state(state="load")
        page.click(f'//div[contains(@class, "search-results-module-filters-content")]//span[text()="{news_category}"]')
        page.select_option("body > div.page-content > ps-search-results-module > form > div.search-results-module-ajax > ps-search-filters > div > main > div.search-results-module-results-header > div.search-results-module-sorts > div > label > select", sort_filter)

    def get_page_number(self):
        """Get page number to iterate"""
        page = self.browser.page()
        page.wait_for_load_state(state="load")
        str_number_results = page.locator("body > div.page-content > ps-search-results-module > form > div.search-results-module-ajax > ps-search-filters > div > main > div.search-results-module-pagination > div.search-results-module-page-counts").text_content().replace("1 of ", "")
        str_number_results = str_number_results.replace(",", "").replace(" ", "")
        number_results = int(str_number_results)
        return number_results

    def get_news_results(self):
        """Get the results of news by searched phrase and category"""
        page = self.browser.page()
        page.wait_for_load_state(state="load")
        news = page.locator("body > div.page-content > ps-search-results-module > form > div.search-results-module-ajax > ps-search-filters > div > main > ul > li")  
        return news

    def process_news_results(self, news_results, number_months, search_phrase):
        """Process and validate each result"""
        today = datetime.now()
        current_date = today.strftime("%m/%Y")
        last_month = today - dateutil.relativedelta.relativedelta(months=1) 
        last_two_months = today - dateutil.relativedelta.relativedelta(months=2)
        previous_month = last_month.strftime("%m/%Y")
        previous_two_months = last_two_months.strftime("%m/%Y")

        is_break = False

        if news_results.count() == 0:
            self.submit_search()

        for i in range(news_results.count()):
            new_date = self.convert_date(news_results.nth(i).locator("p.promo-timestamp").text_content())
            if number_months == 1 and new_date == current_date:
                self.process_new(news_results, i, search_phrase)
            elif number_months == 2 and (new_date == current_date or new_date == previous_month):
                self.process_new(news_results, i, search_phrase)
            elif number_months == 3 and (new_date == current_date or new_date == previous_two_months):
                self.process_new(news_results, i, search_phrase)
            else:
                is_break = True
            
            if is_break:
                break
            
        page = self.browser.page()
        page.click("body > div.page-content > ps-search-results-module > form > div.search-results-module-ajax > ps-search-filters > div > main > div.search-results-module-pagination > div.search-results-module-next-page")
        page.wait_for_load_state(state="load")   

        return is_break

    def convert_date(self, str_new_date):
        try:
            date_obj = parser.parse(str_new_date)
            return date_obj.strftime("%m/%Y")
        except ValueError:
        # Handle the case where the date string does not match any known format
            return None

    def create_excel_file(self):
        excel_file = "output/Fresh News.xlsx"
        self.excel.create_workbook(path=excel_file, fmt="xlsx")
        self.excel.set_cell_value(1, "A", "TITLE")
        self.excel.set_cell_value(1, "B", "DATE")
        self.excel.set_cell_value(1, "C", "DESCRIPTION")
        self.excel.set_cell_value(1, "D", "PICTURE PATH")
        self.excel.set_cell_value(1, "E", "SEARCHED PHRASES")
        self.excel.set_cell_value(1, "F", "HAS AMOUNT OF MONEY")
        self.excel.auto_size_columns("A", "F")
        self.excel.save_workbook()

    def add_datarow_to_excel_file(self, title, date, description, picture, search_phrases, has_amount_of_money):
        """Write news data into excel file"""
        row_data = [[title, date, description, picture, search_phrases, has_amount_of_money]]
        self.excel.open_workbook("output/Fresh News.xlsx")
        self.excel.append_rows_to_worksheet(row_data, name="Sheet")
        self.excel.auto_size_columns("A", "F")
        self.excel.save_workbook()
        self.excel.close_workbook()

    def count_of_search_phrases(self, title, description, search_phrase):
        """Find the count of phrases in Title and Description"""
        str_concatenated = title + description
        return str_concatenated.count(search_phrase)

    def has_amount_of_money(self, title, description):
        """Validate if title and description contains any amount of money"""
        str_concatenated = title + description
        regex_pattern = r'\$?\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?|\b\d+\s*(?:dollars|USD)?\b'
        has_amount_of_money = re.findall(regex_pattern, str_concatenated)
        return bool(has_amount_of_money)

    def download_image(self, image_url, screenshot_path):
        """Save the image of the news"""
        response = requests.get(image_url)
        response.raise_for_status()
        screenshot = Path(screenshot_path)
        screenshot.parent.mkdir(parents=True, exist_ok=True)
        with open(screenshot, "wb") as file:
            file.write(response.content)

    def process_new(self, news_results, i, search_phrase):
        """Process and save date of the list of news"""
        regex_pattern = r'[^a-zA-Z0-9\s]'
        page = self.browser.page()
        page.wait_for_load_state(state="load")

        new_title = news_results.nth(i).locator("h3.promo-title").text_content()
        screenshot_name = "output/screenshots/" + re.sub(regex_pattern, "", new_title) + ".png"
        new_description = news_results.nth(i).locator("p.promo-description").text_content()
        new_date = news_results.nth(i).locator("p.promo-timestamp").text_content()
        img_url = news_results.nth(i).locator("div.promo-media > a > picture > img").get_attribute("src")
        self.download_image(img_url, screenshot_name)
        new_searched_phrases = self.count_of_search_phrases(new_title, new_description, search_phrase)
        new_has_amount_of_money = self.has_amount_of_money(new_title, new_description)
        self.add_datarow_to_excel_file(new_title, new_date, new_description, screenshot_name, 
                                       str(new_searched_phrases), str(new_has_amount_of_money))
