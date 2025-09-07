import requests
from datetime import datetime, timedelta
import os
import time

# Set the start date and current date
start_date = datetime(2021, 9, 5)
current_date = datetime.now()

# Base URL template
base_url = "https://www.nytimes.com/svc/crosswords/v6/puzzle/mini/{}.json"

# Directory to save downloaded files
output_dir = "nyt_mini_crosswords"
os.makedirs(output_dir, exist_ok=True)

# Headers from the cURL command
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:142.0) Gecko/20100101 Firefox/142.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Content-type": "application/x-www-form-urlencoded",
    "X-Games-Auth-Bypass": "true",
    "Connection": "keep-alive",
    "Referer": "https://www.nytimes.com/crosswords/game/mini/2021/09/05",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "TE": "trailers"
}

# Iterate through each date from start_date to current_date
current = start_date
while current <= current_date:
    # Format the date as YYYY-MM-DD
    date_str = current.strftime("%Y-%m-%d")
    url = base_url.format(date_str)
    # Update Referer header for the specific date
    headers["Referer"] = f"https://www.nytimes.com/crosswords/game/mini/{date_str}"
    file_path = os.path.join(output_dir, f"{date_str}.json")
    
    # Skip if file already exists
    if os.path.exists(file_path):
        print(f"Skipping {date_str}: File already exists")
        current += timedelta(days=1)
        continue
    
    try:
        # Send HTTP request with headers
        response = requests.get(url, headers=headers)
        
        # Check if request was successful
        if response.status_code == 200:
            # Save the JSON content to a file
            with open(file_path, 'w') as f:
                f.write(response.text)
            print(f"Downloaded {date_str}")
        else:
            print(f"Skipping {date_str}: HTTP {response.status_code}")
            
    except requests.RequestException as e:
        print(f"Skipping {date_str}: Error - {e}")
    
    # Move to the next date
    current += timedelta(days=1)
    
    # Add a small delay to avoid overwhelming the server
    time.sleep(0.5)

print("Download process completed.")
