from playwright.sync_api import sync_playwright, Playwright
from rich import print

def run(playwright: Playwright):
    start_url = "https://ohiobuys.ohio.gov/page.aspx/en/rfp/request_browse_public?historyBack=1"
    chrome = playwright.chromium
    browser = chrome.launch(headless=False)
    page = browser.new_page()
    page.goto(start_url)
    
    # Wait for the table rows to load
    page.wait_for_selector("tr[data-object-type='rfp']")

    solicitation_names = []
    
    while True:
        # Locate all rows with 'data-object-type="rfp"'
        rows = page.locator("tr[data-object-type='rfp']").all()
        
        # Extract solicitation names from the current page
        for row in rows:
            # Extract the text from the solicitation name column
            solicitation_name = row.locator("td:nth-child(3)").inner_text().strip()  # Adjust column if needed
            if solicitation_name:
                solicitation_names.append(solicitation_name)
            print(solicitation_names)

        page.locator("button[id='body_x_grid_PagerBtnNextPage']").click()

with sync_playwright() as playwright:
    run(playwright)
