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
            
            # Locate all download links within the div
            download_links = page.locator("div[class='ui buttons iv-file-button'] a.iv-download-file").all()

            for link in download_links:
                file_name = link.locator("span[data-iv-role='label']").inner_text().strip()

                # Wait for the download and save each file synchronously
                with page.expect_download() as download_info:
                    link.click()
                download = download_info.value
                download.save_as(file_name)
                print(f"Downloaded file: {file_name}")

            if page.history_back_available():
                print("Attempting to go back to the previous page...")
                page.go_back()
                page.wait_for_selector("tr[data-object-type='rfp']")
                print("Successfully navigated back to the previous page.")
            else:
                print("No previous page in history.")


            # Extract the text from the solicitation name column
            solicitation_id = row.locator("td:nth-child(2)").inner_text().strip()
            solicitation_name = row.locator("td:nth-child(3)").inner_text().strip()
            solicitation_begin_str = row.locator("td:nth-child(5)").inner_text().strip()
            solicitation_end_str = row.locator("td:nth-child(6)").inner_text().strip()
            solicitation_begin_date_object = datetime.strptime(solicitation_begin_str, date_format)
            solicitation_end_date_object = datetime.strptime(solicitation_end_str, date_format)
            
            solicitations.append({"id": solicitation_id, "name": solicitation_name, "begin": solicitation_begin_date_object, "end": solicitation_end_date_object, "summary": solicitation_summary})
            print(solicitations)

        # Check if the 'Next Page' button is present, if so, click it to load more rows
        if page.locator("button[id='body_x_grid_PagerBtnNextPage']").count() > 0:
            page.locator("button[id='body_x_grid_PagerBtnNextPage']").click()
            # Wait for the page to load after clicking 'Next Page'
            page.wait_for_selector("tr[data-object-type='rfp']")
        else:
            print("No more pages to navigate.")
            break  # Exit the loop if no 'Next Page' button is found

    browser.close()

with sync_playwright() as playwright:
    run(playwright)
