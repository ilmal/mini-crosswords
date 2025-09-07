import aiohttp
import asyncio
import json
from datetime import datetime, timedelta
import os
import re

# Set the start date and current date
start_date = datetime(2021, 9, 5)
current_date = datetime.now()

# Base URL template
base_url = "https://www.nytimes.com/svc/crosswords/v6/puzzle/mini/{}.json"

# Directory to save downloaded files
output_dir = "puzzles"
os.makedirs(output_dir, exist_ok=True)

# Puzzle list file
puzzle_list_file = os.path.join(output_dir, "puzzle-list.json")

# Headers from the cURL command
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:142.0) Gecko/20100101 Firefox/142.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Content-type": "application/x-www-form-urlencoded",
    "X-Games-Auth-Bypass": "true",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "TE": "trailers",
    "Cookie": "nyt-a=0Yep4xj60y-dNlx2nQsez6; nyt-purr=cfhheaihhudlhulssdds2fdnd; nyt-jkidd=uid=0&lastRequest=1757277302464&activeDays=%5B0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C1%2C0%2C0%2C1%5D&adv=2&a7dv=2&a14dv=2&a21dv=2&lastKnownType=anon&newsStartDate=&entitlements=; _dd_s=aid=5593d80d-0872-49d3-ac0a-e69f101e0002&rum=0&expire=1757276128922; iter_id=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhaWQiOiI2OGI5MzIwZmU0YTFhYTQ2NDNhNDZiNGEiLCJjb21wYW55X2lkIjoiNWMwOThiM2QxNjU0YzEwMDAxMmM2OGY5IiwiaWF0IjoxNzU2OTY3NDM5fQ.cnvxH9aCk_G_TcEMgLZ6kybJAN3NqEQz2QI_NwV9l1M; datadome=8ukliFY4H6olnvPvAYRBw6Stw3yDfNcRTCvcV6F~~On2zzf4TNJEJqJJ8PIpeFVMKvhZVOSYWeKtMk5RcQ40ZdZmKSzjlCZKFOwhLjnDIbTChYVXr2JQE8mdoZTVralw; _cb=C6_cuLBzTe9aYInvJ; _chartbeat2=.1756967439305.1756967439305.1.DzhrgiDd3DoxDFJgyCG6ngGDlnxBM.1; fides_consent=%7B%22consent%22%3A%7B%7D%2C%22identity%22%3A%7B%22fides_user_device_id%22%3A%22668c5683-4792-4e7c-8492-e3d72d6c23d3%22%7D%2C%22fides_meta%22%3A%7B%22version%22%3A%220.9.0%22%2C%22createdAt%22%3A%222025-09-04T06%3A30%3A38.450Z%22%2C%22updatedAt%22%3A%222025-09-04T06%3A30%3A43.527Z%22%2C%22consentMethod%22%3A%22reject%22%7D%2C%22tcf_consent%22%3A%7B%22system_consent_preferences%22%3A%7B%7D%2C%22system_legitimate_interests_preferences%22%3A%7B%7D%7D%2C%22fides_string%22%3A%22CQXOGEAQXOGEAGXABBENB6FgAAAAAAAAAAAAAAAUAQiyA0CQMAFMGAkgTQAYBgOAJAARIACAASAAoALAAUAIAAFBAAACAEAYEAAEAAAACiAQAJQMAAAAAFAAAACEAEAAIAAAACAAIAIAAAgAAAAAAAAAAAAIAAgCAAgIAAAEAAAAQQAABAAAAAAAAACAAAAAAAAAgACIAIAgAAAAAAAgAAAIBAAAAAAAAQAACAAAAAAgAAAQAAAACACAAAAAAAIAAAAA%2C2~~dv.61.70.83.89.122.143.144.196.202.230.286.311.320.322.327.413.415.445.491.494.523.540.576.591.802.839.981.1031.1046.1097.1166.1188.1276.1307.1364.1415.1558.1577.1584.1721.1725.1827.1843.1845.1917.1942.1944.1962.2008.2027.2039.2056.2068.2072.2107.2109.2130.2135.2166.2177.2219.2279.2309.2322.2325.2328.2331.2343.2359.2376.2387.2416.2488.2567.2568.2571.2572.2577.2596.2604.2605.2608.2657.2661.2677.2695.2813.2821.2862.2869.2882.2900.2908.2914.2918.2929.2941.2963.2987.3002.3005.3008.3024.3048.3077.3089.3106.3119.3126.3173.3188.3210.3219.3227.3237.3250.3253.3257.3281.3299.3300.4131.7235.14237%22%2C%22tcf_version_hash%22%3A%226f02e68eac4f%22%7D; purr-pref-agent=<Go<C_<T1<Tp1r<Tp2r<Tp3r<Tp4r<Tp7r<a0_; purr-cache=<G_<C_<T0<Tp1_<Tp2_<Tp3_<Tp4_<Tp7_<a0_<K0<S0<r<ua; gpp-string=\",,DBABLA~BVQqAAAAAABo.QA\"; RT=\"z=1&dm=nytimes.com&si=892a0e92-9baa-4068-a603-c499028c229b&ss=mf51wbrh&sl=1&tt=sm&bcn=%2F%2F684dd32d.akstat.io%2F&ld=129&hd=33v\"; nyt-gdpr=1; nyt-geo=SE; nyt-traceid=000000000000000076058deb317894d6; nyt-m=B8E4BFC1A85E8416DC260A1D9D75D87B&t=i.0&er=i.1757276918&imu=i.1&prt=i.0&iue=i.0&ifv=i.0&iir=i.0&s=s.tiles&ft=i.0&fv=i.0&ica=i.0&iga=i.0&ird=i.0&e=i.1759327200&igf=i.0&vp=i.0&igu=i.1&igd=i.1&iru=i.1&g=i.1&rc=i.0&vr=l.4.0.0.0.0&uuid=s.a7d8efe3-a89d-4887-9cd6-c47b105f450b&v=i.0&pr=l.4.0.0.0.0&iub=i.0&ira=i.0&n=i.2&cav=i.1&ier=i.0&imv=i.0; _dd_s=rum=0&expire=1757279843616"
}

# Load or initialize puzzle list
puzzle_list = []
if os.path.exists(puzzle_list_file):
    try:
        with open(puzzle_list_file, 'r') as f:
            puzzle_list = json.load(f)
    except json.JSONDecodeError:
        print("Warning: puzzle-list.json is corrupted, initializing empty list.")

# Generate list of dates to process
dates = []
current = start_date
while current <= current_date:
    date_str = current.strftime("%Y-%m-%d")
    # Check if date is already in puzzle list
    if not any(puzzle["date"] == date_str for puzzle in puzzle_list):
        dates.append(date_str)
    current += timedelta(days=1)

async def fetch_puzzle(session, date_str):
    url = base_url.format(date_str)
    headers["Referer"] = f"https://www.nytimes.com/crosswords/game/mini/{date_str}"
    file_name = f"{date_str}.json"
    file_path = os.path.join(output_dir, file_name)
    
    try:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                try:
                    puzzle_data = await response.json()
                    
                    # Validate response structure
                    if not puzzle_data or not puzzle_data.get("body") or not isinstance(puzzle_data.get("body"), list) or not puzzle_data.get("body"):
                        print(f"Skipping {date_str}: Invalid API response - missing body")
                        return
                    
                    # Extract publication date
                    publication_date = puzzle_data.get("body")[0].get("publicationDate")
                    if not publication_date or not isinstance(publication_date, str) or not re.match(r"^\d{4}-\d{2}-\d{2}$", publication_date):
                        print(f"Warning: Invalid or missing publicationDate for {date_str}. Using {date_str} as fallback.")
                        publication_date = date_str
                    
                    file_name = f"{publication_date}.json"
                    file_path = os.path.join(output_dir, file_name)
                    
                    # Skip if file already exists
                    if os.path.exists(file_path):
                        print(f"Skipping {date_str}: File {file_name} already exists")
                        return
                    
                    # Save puzzle JSON with indentation
                    with open(file_path, 'w') as f:
                        json.dump(puzzle_data, f, indent=2)
                    
                    # Update puzzle list
                    async with asyncio.Lock():
                        puzzle_list.append({"date": publication_date, "file": file_name})
                        with open(puzzle_list_file, 'w') as f:
                            json.dump(puzzle_list, f, indent=2)
                    
                    print(f"Saved puzzle for {publication_date}")
                    
                except json.JSONDecodeError:
                    print(f"Skipping {date_str}: Invalid JSON response")
            else:
                print(f"Skipping {date_str}: HTTP {response.status}")
                
    except aiohttp.ClientError as e:
        print(f"Skipping {date_str}: Error - {e}")

async def main():
    # Limit concurrent requests to avoid overwhelming the server
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_puzzle(session, date_str) for date_str in dates]
        await asyncio.gather(*tasks, return_exceptions=True)

if __name__ == "__main__":
    asyncio.run(main())
    print("Download process completed.")
