import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_watches(page_count):
    
    watches_dict = {}

    try:
        for n in range(1, page_count+1):
            url = f"https://www.liveauctioneers.com/c/watches/97/?page={n}"

            response = requests.get(url)

            if response.status_code != 200:
                print(f"Failed to get the webpage: {response.status_code}")
                return []

            soup = BeautifulSoup(response.text, 'html.parser')

            watches_list = soup.find_all('section', class_ = "CategorySearchCard__CategorySearchCardGrid-sc-1o7izf2-1 dliokm")

            for watch in watches_list:
                
                name_element = watch.find('span', class_='hui-text-body-primary text-text-primary')
                if name_element:
                    watch_name = name_element.text
                else:
                    # Skip or log the missing name
                    print(f"Missing watch name on page {n}")
                    continue

                price_element = watch.find('span', class_ = 'FormattedCurrency__StyledFormattedCurrency-sc-1ugrxi1-0 cqnbDD')

                if price_element:
                    watch_price_str = price_element.text
                    if watch_price_str[0] != "$":
                        print(f"Not in USD in page {n}. Excluding result to avoid confusion")
                        continue 
                    else:
                        watch_price = float(watch_price_str.replace('$', '').replace(',', ''))
                else:
                    print(f"Missing watch price on page {n}")
                    continue
                
                watches_dict[watch_name] = watch_price
        
        return watches_dict
    
    except Exception as e:
        print(f"Error has occurred: {e}")
        return []

def watch_shortlist(page_count, target_price, plus_minus):
    
    watches = get_watches(page_count = page_count)
    
    shortlist_df = pd.DataFrame()

    price_lower_bound = max(0, target_price - plus_minus)
    price_upper_bound = target_price + plus_minus

    for key, value in watches.items():
        if value >= price_lower_bound and value <= price_upper_bound:
            row = pd.DataFrame({"Name": [key], "Price": [value]})
            shortlist_df = pd.concat([shortlist_df, row], ignore_index=True)
    
    shortlist_df = shortlist_df.sort_values(by=["Price"], ascending= True)
    
    return shortlist_df

maxPageCount = int(input("How deep (in terms of number of pages) do you want to dive into the auction listing? "))
targetPrice = int(input("What's your target price? (I suggest you don't go below 100 if you're serious about buying one of these watches) "))
plusMinus = int(input("How much higher than your target price are you willing to go? "))

watch_list = watch_shortlist(page_count = maxPageCount, target_price = targetPrice, plus_minus = plusMinus)

print(watch_list)