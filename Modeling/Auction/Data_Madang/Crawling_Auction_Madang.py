from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import os
# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException

def parse_page(html):
    soup = BeautifulSoup(html, "html.parser")
    data_list = []

    items = soup.select("a.search_list")
    print(f"Found {len(items)} items to parse.")

    for item in items:
        try:
            # 소재지
            address_element = item.select_one(".list_text_addr")
            address = address_element.get_text(strip=True) if address_element else "N/A"
            
            # 면적
            area_element = item.select_one(".list_area_wrapper")
            area = ' '.join(area_element.get_text().split()) if area_element else ""
            
            building_area_match = re.search(r"건물\s*([\d,.]+)", area)
            if building_area_match:
                building_area = building_area_match.group(1).replace(',', '')
            else:
                building_area = "N/A"

            land_area_match = re.search(r"토지\s*([\d,.]+)", area)
            if land_area_match:
                land_area = land_area_match.group(1).replace(',', '')
            else:
                land_area = "N/A"
            
            # 기타 정보
            special_element = item.select_one(".mul_special_right_wrapper")
            special = special_element.get_text().split() if special_element else "N/A"

            #감정가
            price_element = item.select_one(".price")
            price = price_element.get_text(strip=True) if price_element else "N/A"

            # 최저가
            min_price_element = item.select_one(".price.low")
            min_price_text = min_price_element.get_text(strip=True) if min_price_element else "N/A"
            if min_price_text != "N/A":
                min_price = min_price_text.replace('최', '').replace('원', '').replace(',', '')
            else:
                min_price = None

            # 낙찰가
            win_price_element = item.select_one(".price.sold")
            win_price_text = win_price_element.get_text(strip=True) if win_price_element else "N/A"
            if win_price_text != "N/A":
                win_price = win_price_text.replace('낙', '').replace('원', '').replace(',', '')
            else:
                win_price = None

            # 진행상태
            status_element = item.select_one(".state")
            status = status_element.get_text(strip=True) if status_element else "N/A"

            # 매각기일
            sale_date_element = item.select_one(".date")
            sale_date = sale_date_element.get_text(strip=True) if sale_date_element else "N/A"
            
            # 유찰횟수
            uchal_element = item.select_one(".uchal")
            uchal_text = uchal_element.get_text(strip=True) if uchal_element else "N/A"
            uchal_match = re.search(r'\d+', uchal_text)
            if uchal_match:
                ucal = int(uchal_match.group(0))
            else:
                ucal = "N/A"
            
            
            data_list.append({
                "소재지": address,
                "건물면적": building_area,
                "토지면적": land_area,
                "감정가": price,
                "최저가": min_price,
                "낙찰가": win_price,
                "매각기일": sale_date,
                "유찰횟수": ucal,
                "기타정보": special,
                "진행상태": status
            })
            
        except Exception as e:
            print(f"⚠️ Error parsing an item: {e}")
            continue
    
    print(f"Successfully parsed {len(data_list)} items.")
    print("--- Sample Parsed Data (first 5) ---")
    for d in data_list[:15]:
        print(d)
    return data_list


# --- Main Execution ---
def scrape_by_state(state_code, max_page, start_page=0):
    """
    Crawls auction data for a specific state code, from a start page up to a maximum page number.
    
    Args:
        state_code (int): The state code to filter by (e.g., 40, 50).
        max_page (int): The maximum page number to scrape.
        start_page (int): The page number to start scraping from. Defaults to 0.
    """
    print(f"\n{'='*20} Starting scrape for State: {state_code} from Page: {start_page} {'='*20}")

    # Create a unique output directory for this state, located next to the script.
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, f"auction_results_state_{state_code}")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Directory '{output_dir}' created.")

    base_url = f"https://madangs.com/search?addr=11+41+27+29+28+26+30+31&court=&asset_classification=&build_area_max=0&build_area_min=0&disposal_method=undefined&eval_p_max=0&eval_p_min=0&g_use_type=2000,2001,2007&land_area_max=0&land_area_min=0&list_type=1&low_p_max=0&low_p_min=0&state={state_code}&g_state=undefined&share=2&g_share=2&special=&contain_special=0&uchal=&use_type=2000&sort=bd_asc&start_date=2020-01-01&end_date=2025-09-01&page={{page}}"
    
    driver = None
    try:
        # --- Driver and Initial Setup ---
        options = webdriver.ChromeOptions()
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        # Go to the start page to set the display mode
        print(f"--- Initial Setup: Setting display mode on page {start_page} ---")
        driver.get(base_url.format(page=start_page))

        print("Waiting for initial loading overlay...")
        WebDriverWait(driver, 10).until(EC.invisibility_of_element_located((By.ID, "loading")))
        print("✅ Loading overlay gone.")

        print("Waiting for the display mode button...")
        display_mode_button_selector = ".swiper-slide.filter_swiper_slide.js_display_mode"
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, display_mode_button_selector)))
        display_mode_button = driver.find_element(By.CSS_SELECTOR, display_mode_button_selector)
        display_mode_button.click()
        print("✅ Display mode button clicked.")

        print("Waiting for list view to load after click...")
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.search_list")))
        print("✅ Initial setup complete. Starting pagination.")
        
        # --- Pagination and Scraping Loop ---
        for page_num in range(start_page, max_page + 1, 60):
            if page_num != start_page:
                auction_site = base_url.format(page=page_num)
                print(f"--- Navigating to Page: {page_num} ---")
                driver.get(auction_site)
                
                print("Waiting for page content to load...")
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.search_list")))
                print("✅ Page content loaded.")
            else:
                 print(f"--- Processing Page: {page_num} (already loaded) ---")

            try:
                dynamic_html = driver.page_source
                parsed_results = parse_page(dynamic_html)
            
                if parsed_results:
                    df = pd.DataFrame(parsed_results)
                    file_path = os.path.join(output_dir, f"madangs_results_page_{page_num}.csv")
                    df.to_csv(file_path, index=False, encoding="utf-8-sig")
                    print(f"✅ Saved {len(df)} rows to {file_path}")
                else:
                    print("No results found on this page. This might be the end for this state.")
                    break

            except Exception as e:
                print(f" An error occurred while processing page {page_num}: {e}")
                error_log_path = os.path.join(output_dir, "error_log.txt")
                with open(error_log_path, "a", encoding="utf-8") as f:
                    f.write(f"Error on page {page_num} for state {state_code}: {e}\nURL: {base_url.format(page=page_num)}\n\n")
                continue
            
            time.sleep(1)

    except Exception as e:
        print(f" A critical error occurred during the Selenium process for state {state_code}: {e}")
    finally:
        if driver:
            driver.quit()
            print(f" Browser closed for state {state_code}.")
    
    print(f"--- Scraping process finished for State: {state_code} ---")


if __name__ == "__main__":
    # Define the scraping tasks: (state_code, max_page, start_page)
    tasks = [
        (40, 33300, 7920),
        (50, 10440, 0)
    ]

    for i, (state, max_p, start_p) in enumerate(tasks):
        try:
            scrape_by_state(state_code=state, max_page=max_p, start_page=start_p)
        except Exception as e:
            print(f" A fatal, unrecoverable error occurred during the task for state {state}. ")
            print(f"Error: {e}")
            # Log this major failure
            with open("fatal_error_log.txt", "a", encoding="utf-8") as f:
                f.write(f"Fatal error on state {state} task: {e}\n\n")

        # If it's not the last task, wait before starting the next one
        if i < len(tasks) - 1:
            print(f"\n{'='*20} Task for state {state} finished. Waiting for 5 seconds before next task... {'='*20}\n")
            time.sleep(5)

