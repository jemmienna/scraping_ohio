from playwright.sync_api import sync_playwright, Playwright
from rich import print
from datetime import datetime

def run(playwright: Playwright):
    start_url = "https://ohiobuys.ohio.gov/page.aspx/en/rfp/request_browse_public?historyBack=1"
    chrome = playwright.chromium
    browser = chrome.launch(headless=False)
    page = browser.new_page()
    page.goto(start_url)

    date_format = "%m/%d/%Y %I:%M:%S %p"
    
    while True:
        # Wait for the table rows to load
        page.wait_for_selector("tr[data-object-type='rfp']")

        solicitations = []
        # Locate all rows with 'data-object-type="rfp"'
        rows = page.locator("tr[data-object-type='rfp']").all()
        
        # Extract solicitation names from the current page
        for row in rows:
            detail_url = row.locator("td:nth-child(1) a").get_attribute("href")
            page.goto("https://ohiobuys.ohio.gov"+detail_url)
            solicitation_summary = page.locator("div[id='body_x_tabc_rfp_ext_prxrfp_ext_x_lblSummary']").inner_text()
            page.go_back()

            # Wait for the table rows to load
            page.wait_for_selector("tr[data-object-type='rfp']")

            # Extract the text from the solicitation name column
            solicitation_id = row.locator("td:nth-child(2)").inner_text().strip()
            solicitation_name = row.locator("td:nth-child(3)").inner_text().strip()
            solicitation_begin_str = row.locator("td:nth-child(5)").inner_text().strip()
            solicitation_end_str = row.locator("td:nth-child(6)").inner_text().strip()
            solicitation_begin_date_object = datetime.strptime(solicitation_begin_str, date_format)
            solicitation_end_date_object = datetime.strptime(solicitation_end_str, date_format)
            
            solicitations.append({"id":solicitation_id, "name":solicitation_name, "begin":solicitation_begin_date_object, "end":solicitation_end_date_object, "summary":solicitation_summary})
            print(solicitations)

        if page.locator("button[id='body_x_grid_PagerBtnNextPage']").count() > 0:
            page.locator("button[id='body_x_grid_PagerBtnNextPage']").click()

with sync_playwright() as playwright:
    run(playwright)
