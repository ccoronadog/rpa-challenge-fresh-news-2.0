from datetime import datetime
import dateutil.relativedelta
from robocorp.tasks import task
from robocorp import browser
from robocorp import workitems
from RPA.Excel.Files import Files
from pathlib import Path

import re
import requests

@task
def consume_news_parameters():
    """Consume los work-items creados según los parámetros"""
    browser.configure(
        slowmo=100,
    )

    excel_file = create_excel_file()
    open_news_website()

    for item in workitems.inputs:
        parameters_data = item.payload["parameters_data"]
        print(parameters_data)
        print(parameters_data["search_phrase"])
        searching_phrase(parameters_data["search_phrase"])
        filter_news_results(parameters_data["news_category"])
        page_results = get_page_number()
        for i in range(page_results):
            news_results = get_news_results()
            is_break = process_news_results(news_results, parameters_data["number_months"], 
                                            parameters_data["search_phrase"], excel_file)
            if is_break:
                break
        
        go_home_website()

def open_news_website():
    """Navigates to the given URL"""
    browser.goto("https://www.latimes.com/")
    page = browser.page()
    page.wait_for_load_state(state="load")

def go_home_website():
    """Go back to home page"""
    page = browser.page()
    page.wait_for_load_state()
    page.click("body > ps-header > header > div.absolute.left-1\/2.-translate-x-1\/2")

def submit_search():
    """Click en 'Search' button"""
    submit_search_button = "body > ps-header > header > div.flex.\[\@media_print\]\:hidden > div.ct-hidden.fixed.md\:absolute.top-12\.5.right-0.bottom-0.left-0.z-25.bg-header-bg-color.md\:top-15.md\:bottom-auto.md\:h-25.md\:shadow-sm-2 > form > button"

    page = browser.page()
    page.click(submit_search_button)
    page.wait_for_load_state(state="load")


def searching_phrase(search_phrase):
    """Type 'search phrase' value into website"""

    search_button = "body > ps-header > header > div.flex.\[\@media_print\]\:hidden > button"
    search_form = "body > ps-header > header > div.flex.\[\@media_print\]\:hidden > div.ct-hidden.fixed.md\:absolute.top-12\.5.right-0.bottom-0.left-0.z-25.bg-header-bg-color.md\:top-15.md\:bottom-auto.md\:h-25.md\:shadow-sm-2 > form > label > input"

    page = browser.page()
    page.wait_for_load_state(state="load")

    page.click(search_button)
    page.fill(search_form, search_phrase)
    submit_search()
    

def filter_news_results(new_categoy):
    """Filter news results by category and newest"""
    sort_filter = "Newest"

    page = browser.page()
    page.wait_for_load_state(state="load")

    page.click('//div[contains(@class, "search-results-module-filters-content")]//span[text()="{}"]'.format(new_categoy))
    page.select_option("body > div.page-content > ps-search-results-module > form > div.search-results-module-ajax > ps-search-filters > div > main > div.search-results-module-results-header > div.search-results-module-sorts > div > label > select", sort_filter)

def get_page_number():
    """Get page number to iterate"""
    page = browser.page()
    page.wait_for_load_state(state="load")

    str_number_results = page.locator("body > div.page-content > ps-search-results-module > form > div.search-results-module-ajax > ps-search-filters > div > main > div.search-results-module-pagination > div.search-results-module-page-counts").text_content().replace("1 of ", "")
    str_number_results = str_number_results.replace(",", "")
    str_number = str_number_results.replace(" ", "")
    number_results = int(str_number)
    print("Results: ", number_results)
    return number_results

def get_news_results():
    """Get the results of news by searched phrase and category"""
    page = browser.page()
    page.wait_for_load_state(state="load")
    news = page.locator("body > div.page-content > ps-search-results-module > form > div.search-results-module-ajax > ps-search-filters > div > main > ul > li")  
        
    return news

def process_news_results(news_results, numberMonths, search_phrase, excel_file):
    """Process and validate each result"""
    page = browser.page()
    page.wait_for_load_state(state="load")

    today = datetime.now()
    current_date = today.strftime("%m/%Y")
    last_month = today - dateutil.relativedelta.relativedelta(months=1) 
    last_two_months = today - dateutil.relativedelta.relativedelta(months=2)
    previous_month = last_month.strftime("%m/%Y")
    previous_two_months = last_two_months.strftime("%m/%Y")

    is_break = False

    if news_results.count() == 0:
        submit_search()

    for i in range(news_results.count()):

        new_date = convert_date(news_results.nth(i).locator("p.promo-timestamp").text_content())
        if numberMonths == 1 and new_date == current_date:
            process_new(news_results, i, search_phrase, excel_file)
        elif (numberMonths == 2) and (new_date == current_date or new_date == previous_month):
            process_new(news_results, i, search_phrase, excel_file)
        elif (numberMonths == 3) and (new_date == current_date or new_date == previous_two_months):
            process_new(news_results, i, search_phrase, excel_file)
        else:
            is_break = True
        
        if is_break:
            break
        
    page.click("body > div.page-content > ps-search-results-module > form > div.search-results-module-ajax > ps-search-filters > div > main > div.search-results-module-pagination > div.search-results-module-next-page")
    page.wait_for_load_state(state="load")   

    return is_break


def convert_date(str_new_date):
    date = datetime.strptime(str_new_date, "%B %d, %Y")
    return date.strftime("%m/%Y")

def create_excel_file():
    excel_file = "output/Fresh News.xlsx"
    lib = Files()
    lib.create_workbook(path=excel_file, fmt="xlsx")
    lib.set_cell_value(1, "A", "TITLE")
    lib.set_cell_value(1, "B", "DATE")
    lib.set_cell_value(1, "C", "DESCRIPTION")
    lib.set_cell_value(1, "D", "PICTURE PATH")
    lib.set_cell_value(1, "E", "SEARCHED PHRASES")
    lib.set_cell_value(1, "F", "HAS AMOUNT OF MONEY")
    lib.auto_size_columns("A", "F")
    lib.save_workbook()

    return excel_file

def add_datarow_to_excel_file(title, date, description, picture, search_phrases, has_amount_of_money, excel_file):
    """Write news data into excel file"""
    row_data = [[title, date, description, picture, search_phrases, has_amount_of_money]]
    excel = Files()
    excel.open_workbook(excel_file)
    excel.append_rows_to_worksheet(row_data, name="Sheet")
    excel.auto_size_columns("A", "F")
    excel.save_workbook()
    excel.close_workbook()

def count_of_search_phrases(title, description, search_phrase):
    """Find the count of phrases in Title and Description"""
    str_concatenated = title + description
    return str_concatenated.count(search_phrase)

def has_amount_of_money(title, description):
    """Validate if title and description contains any amount of money"""
    str_concatenated = title + description
    regex_pattern = r'\$?\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?|\b\d+\s*(?:dollars|USD)?\b'

    has_amount_of_money = re.findall(regex_pattern, str_concatenated)

    return bool(has_amount_of_money)

def download_image(image_url, screenshot_path):
    """save the image of the new"""
    response = requests.get(image_url)
    response.raise_for_status()

    screenshot = Path(screenshot_path)
    screenshot.parent.mkdir(parents=True, exist_ok=True)

    with open(screenshot, "wb") as file:
        file.write(response.content)

def process_new(news_results, i, search_phrase, excel_file):
    """Process and save date of the list of news"""
    regex_pattern = r'[^a-zA-Z0-9\s]'
    page = browser.page()
    page.wait_for_load_state(state="load")

    new_title = news_results.nth(i).locator("h3.promo-title").text_content()
    screenshotName = "output/" + re.sub(regex_pattern, "", new_title) + ".png"
    new_description = news_results.nth(i).locator("p.promo-description").text_content()
    new_date = news_results.nth(i).locator("p.promo-timestamp").text_content()
    img_url = news_results.nth(i).locator("div.promo-media > a > picture > img").get_attribute("src")
    download_image(img_url, screenshotName)
    new_searched_phrases = count_of_search_phrases(new_title, new_description, search_phrase)
    new_has_amount_of_money = has_amount_of_money(new_title, new_description)
    add_datarow_to_excel_file(new_title, new_date, new_description, screenshotName, 
                              str(new_searched_phrases), str(new_has_amount_of_money), excel_file)