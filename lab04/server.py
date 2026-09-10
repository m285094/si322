import getpass
import requests
import re
import sys
import json
from bs4 import BeautifulSoup

def parse_schedule_html(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
 
    # --- Name ---
    # Name appears as: <b><font color="#000080">FIRST MIDDLE LAST /id/blk</b>
    name_tag = soup.find("b")
    name_text = name_tag.get_text(strip=True)
    name_only = re.sub(r"\s*/\d+/\d+\s*$", "", name_text).strip()
    parts = name_only.split()
    first_name = parts[0]
    last_name = parts[-1]
    middle_name = " ".join(parts[1:-1]) if len(parts) > 2 else ""
 
    # --- Schedule table ---
    schedule = []
    sched_header = soup.find("th", id="TITLE")
    sched_table = sched_header.find_parent("table")
    rows = sched_table.find_all("tr", class_="cgrldatarow")
    for row in rows:
        cells = row.find_all("td")
        schedule.append({
            "title": cells[0].get_text(strip=True),
            "course": cells[1].get_text(strip=True),
            "section": cells[2].get_text(strip=True),
            "meeting_time": cells[3].get_text(strip=True),
            "bld_room": cells[4].get_text(strip=True),
            "instructor": cells[5].get_text(strip=True),
        })
 
    # --- Schedule Matrix ---
    matrix_header = soup.find(string=re.compile("Schedule Matrix"))
    matrix_table = matrix_header.find_parent(["font", "h2"]).find_next("table")
 
    matrix_rows = matrix_table.find_all("tr")
    day_row = matrix_rows[1]  # row with MON/TUE/WED/... headers
    days = [th.get_text(strip=True) for th in day_row.find_all("th")]
 
    schedule_matrix = {}
    for row in matrix_rows[2:]:
        cells = row.find_all("td")
        if not cells:
            continue
        period = cells[0].get_text(strip=True)
        day_values = {}
        for day, cell in zip(days, cells[1:]):
            val = cell.get_text(strip=True)
            day_values[day] = val if val and val != "\xa0" else None
        schedule_matrix[period] = day_values
 
    return {
        "first_name": first_name,
        "last_name": last_name,
        "middle_name": middle_name,
        "schedule": schedule,
        "schedule_matrix": schedule_matrix,
    }

def print_readable(result: dict) -> None:
    name = f"{result['first_name']} {result['middle_name']} {result['last_name']}".replace("  ", " ")
    print("=" * 70)
    print(f"Midshipman: {name}")
    print("=" * 70)
 
    # --- Schedule ---
    print("\nSCHEDULE")
    print("-" * 70)
    course_w = 7
    sect_w = 7
    time_w = 12
    room_w = 14
    header = f"{'Course':<{course_w}} {'Sect':<{sect_w}} {'Meeting Time':<{time_w}} {'Room':<{room_w}} Title"
    print(header)
    print("-" * 70)
    for c in result["schedule"]:
        print(
            f"{c['course']:<{course_w}} {c['section']:<{sect_w}} "
            f"{c['meeting_time']:<{time_w}} {c['bld_room']:<{room_w}} "
            f"{c['title']} ({c['instructor']})"
        )
 
    # --- Matrix ---
    print("\nSCHEDULE MATRIX")
    print("-" * 70)
    days = list(next(iter(result["schedule_matrix"].values())).keys())
    col_w = 8
    header = f"{'Period':<8}" + "".join(f"{d:<{col_w}}" for d in days)
    print(header)
    print("-" * 70)
    for period, day_values in result["schedule_matrix"].items():
        row = f"{period:<8}"
        for d in days:
            val = day_values[d] or "-"
            row += f"{val:<{col_w}}"
        print(row)
    print()

if __name__ == "__main__":

    s = requests.Session()
    s.verify = False

    login_url = "https://login.usna.edu/oam/server/obrareq.cgi?encquery%3D1KyfR2bc8k8ACxcScVhOU7ws7rKFwlAsFnyyAGy9hv6VVnpBSPxsFxhBS4cO7qcUSM2pynPyBHs4w7B%2Fuz9BP85xSEkoWfY2OIG4T1VjXdgn0fIJa292Lnk42m9MerzYaPBKzAN4r%2Bft5g06GAWdKP98hn0FW9HWuVuFk7csqA2ktBfxt2zSjSN1Md%2B5ypTZcGwoWfFM1h7DDH4kJynRuaEqLwHs2datm9zRgL%2BI4M83kLSafUJG9P6mzg1DrTzHdzxAl2Zx3%2BwuNP1abRPdGA%3D%3D%20agentid%3DUSNA_OHS12c_WebGateAgent%20ver%3D1%20crmethod%3D2"
    username = input("Username: ")
    password = getpass.getpass(prompt="Password: ")
    
    login_headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
    }
    
    login_payload = {
        "username": username,
        "password": password
    }

    # s.post(login_url, headers=login_headers, data=login_payload)

    # if not any("OAMAuthnCookie" in c.name for c in s.cookies):
    #     print("\n[ERROR] Login failed - incorrect username or password.")
    #     sys.exit(1)

    # print("Login succeeded!")
    # print(f"Logged in as {username}\n")

    r_login = s.post(login_url, headers=login_headers, data=login_payload)

    # If login fails, OAM typically re-renders the login page (containing a password field) 
    # or stays on the login URL. Let's check for failure indicators:
    if "password" in r_login.text.lower() or "invalid" in r_login.text.lower():
        print("\n[ERROR] Login failed - incorrect username or password.")
        sys.exit(1)

    print("Login succeeded!")
    print(f"Logged in as {username}\n")

    schedule_url="https://mids.usna.edu/ITSD/mids/drgwq010$mids.actionquery"

    print("Schedules - Query Midshipmen")
    alpha = input("Alpha (default ''): ")
    last_name = input("Last Name (default ''): ")
    co_num = input("Company (default ''): ")
    ac_year = input("Academic Year (default '2027'): ")
    sem = input("Semester ('fall','spring','summer' default 'fall'): ").upper()
    blk_num = input("Block Number ('1','2','3' default '1'): ")
    maj_code = input("Major Code (default ''): ")
    adviser = input("Adviser (default ''): ")

    params = {
        "P_ALPHA": alpha,
        "P_LAST_NAME": last_name,
        "P_MICO_CO_NBR": co_num,
        "P_SECOF_COOF_SEBLDA_AC_YR": ac_year if ac_year != "" else "2027",
        "P_SECOF_COOF_SEBLDA_SEM": sem if sem != "" else "FALL",
        "P_SECOF_COOF_SEBLDA_BLK_NBR": blk_num,
        "P_MAJOR_CODE": maj_code,
        "P_NOMI_FORMATTED_NAME": adviser,
        "Z_ACTION": "QUERY",
        "Z_CHK": "0"
    }

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Content-Length": "196",
        "Content-Type": "application/x-www-form-urlencoded",
        # "Cookie": "f5_cspm=1234; WSG$DRGWQ010$URL0=/ITSD/mids/drgwq010$.startup; WSG$DRGWQ010$CAP0=Schedules_-_Query_Midshipmen; f5avraaaaaaaaaaaaaaaa_session_=ALLGKNPAAFDFJHMHDJBEIFDIFGCGAEEOFMMECBCOFLOBKHLLKJMMBECLNIMHMGENGKMDAGIBFLELBFPIBPBAJODCHLHKLMDMJMJENHOGGNKKOFPLFAONHAHKBKDABGHL; _ga=GA1.1.1475175361.1789048760; nmstat=207be5a8-6712-28bd-a22a-0df09b1c024a; BIGipServermids_prod=!fLZW56HVRdd5LNR94KzTDZcqOm0eDwQma8FHMQw0clqDJB3yyCWymoA/XfzFZBvT8LPwllKWxGeQi3A=; f5avraaaaaaaaaaaaaaaa_session_=OJOKNEMHPBADHBGMKDDOFPNMFDDPMFLHNBELLAKEECONFGODBEMGMPDIDODPMGCCNAGDAAPNOHGJGGOIIMHAHLCGGLAGPPAMNDCHMELHFLDFPEEJPBPEHNPIMFPFNFBC; _ga_LY79N0FLBS=GS2.1.s1789048760$o1$g1$t1789048832$j49$l0$h0; OAMAuthnCookie_mids.usna.edu:443=4mkD76OAtpaIpv%2FZEQ8bV9zH14WKwq%2BCGljRuUyUCb1GahKi3O427i2dAYfGlNKTnRc%2F1XPMGq7AbFQLo8ipCxB6iA1BxbDuStvsEPMZ6aUZWqn0Gp9kLrYpe2QU4KePemT746fcvMELnQYWyTZsoDMv2nmN%2BZD8CKcMUj3lmjWjbU4YSPauRwUsYDnwfulrabsqnzEebrYnIVClqkpU5slTX2LHtynrPEN64rcp5SHXmYxXUS55fbhPCnlb1%2FErSAGQsI748ksbyr3l0MwT%2Bo6%2BeZH0TyhTcXWRcOULb%2BLeRq464J6x8zAx3994RRqJH1De10xdP1cFTldo82LWfPtx%2FlTgTl9uLe7ihCcVHdXqaDb8Cf4ikr5zuLMpM7ggPUQGaIl%2BVdd%2F5LNFBURezHvdrVZnCsWOq3jX8tUt%2BfAuV7tSDsxRCA7%2FQ7Vzekj4%2Fcx2nfbjxqjQeEUdAeUrszjwarCsR5eqE5UCAkMVpGeOt7NRsBsgfgY9YCqcO77UKmUpZ0I7%2Bt8QDwl36znFA4rTadWfQYQ1MWORU3xMsfYo7uXpCc1Wwum39Cfn%2FLx06ibAEyx1U%2BcZObTMtVk2iA%3D%3D; f5avr0528938678aaaaaaaaaaaaaaaa_cspm_=IEFIKDKMLFPIDGDFOJLMHGPHFBMILOLOIAFGLNCHGDMNLNIKDDCFMPCILPKHKHELDGECOCMHAOEBEBEJDMOABPMMAJANILGLFCEKBKOMIOPNNCNPLJMEDHDDPNLOLMAE",
        "Host": "mids.usna.edu",
        "Origin": "https://mids.usna.edu",
        "Referer": "https://mids.usna.edu/ITSD/mids/drgwq010$.startup",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36",
        "sec-ch-ua": "\"Not=A?Brand\";v=\"99\", \"Google Chrome\";v=\"151\", \"Chromium\";v=\"151\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Linux\""
    }

    r = s.post(schedule_url, data=params, headers=headers)



    result = parse_schedule_html(r.text)
    print_readable(result)

# with open("resp.html", "w", encoding="utf-8") as file:
#     file.write(r.text)

# print("Saved response to resp.html")
