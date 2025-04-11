import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from urllib.parse import quote

# Set up Selenium
options = Options()
options.add_argument("--headless=new")
driver = webdriver.Chrome(options=options)
driver.get("https://doerssummit.com/programme/")
driver.implicitly_wait(10)

# Get page content
soup = BeautifulSoup(driver.page_source, "html.parser")
driver.quit()

# Prompt for event date
event_date_input = input("Enter event date (MM/DD/YYYY): ").strip()
event_date_obj = datetime.strptime(event_date_input, "%m/%d/%Y")
date_for_gcal = event_date_obj.strftime("%Y%m%d")

# Extract unique events
blocks = soup.select("div")
seen = set()
events = []

for div in blocks:
    name_el = div.find("p")
    time_el = div.find("span")

    if name_el and time_el:
        name = name_el.get_text(strip=True)
        time_range = time_el.get_text(strip=True)

        if re.match(r"\d{1,2}:\d{2}\s*[ap]m\s*-\s*\d{1,2}:\d{2}\s*[ap]m", time_range, re.IGNORECASE):
            key = (name, time_range)
            if key not in seen:
                seen.add(key)
                events.append((name, time_range))

# Function to convert "8:30AM" to "083000"
def convert_to_24(time_str):
    return datetime.strptime(time_str.strip().upper(), "%I:%M%p").strftime("%H%M%S")

# Print cleaned event list with Google Calendar links
print("\n🎯 Unique Events with Google Calendar Links:\n")
for i, (name, time_range) in enumerate(events, 1):
    start_str, end_str = time_range.upper().split("-")
    start_time = convert_to_24(start_str)
    end_time = convert_to_24(end_str)

    start_dt = f"{date_for_gcal}T{start_time}Z"
    end_dt = f"{date_for_gcal}T{end_time}Z"

    gcal_url = (
        "https://www.google.com/calendar/render"
        f"?action=TEMPLATE"
        f"&text={quote(name)}"
        f"&dates={start_dt}/{end_dt}"
        f"&sf=true"
        f"&output=xml"
    )

    print(f"{i}. {name} — {time_range}")
    print(f"   📅 Add to Calendar: {gcal_url}\n")
