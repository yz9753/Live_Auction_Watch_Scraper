import requests
from bs4 import BeautifulSoup
import pandas as pd

# Create a function that scrapes the LiveAuctioneers' watch auction listings
def get_watches(page_count):
    '''
    Input: page_count (int): number of pages of watch listings the user would like to scrape
    Process: the function goes through the n number of pages and extracts each product's name and current listed price
    Output: dictionary of all watch listings {name: price}
    '''

    # Initialize an empty dictionary to store the watch names and their corresponding prices.
    watches_dict = {}

    try:
        # Loop through each page from 1 to page_count
        for n in range(1, page_count+1):
            # Construct the URL for each page of the watch listings. Replace for different products
            url = f"https://www.liveauctioneers.com/c/watches/97/?page={n}"

            # Send a GET request to the URL
            response = requests.get(url)

            # Check if the response is successful (status code 200). If not, log the error and return an empty dictionary.
            if response.status_code != 200:
                print(f"Failed to get the webpage: {response.status_code}")
                return {}

            # Parse the content using BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all sections that correspond to individual watch listings, defined by the below class name.
            watches_list = soup.find_all('section', class_ = "CategorySearchCard__CategorySearchCardGrid-sc-1o7izf2-1 dliokm")
            
            # Loop through each watch listing found in the current page
            for watch in watches_list:
                
                # Extract the watch name from the span element with the specified class name
                name_element = watch.find('span', class_='hui-text-body-primary text-text-primary')
                # If the name element exists, store that in the watch_name variable. If not, skip and print message to show missing name in the corresponding page.
                if name_element:
                    watch_name = name_element.text
                else:
                    print(f"Missing watch name on page {n}")
                    continue
                
                # Perform similar analysis and storing for the price element
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
                
                # Finanlly, store the name and price as a key, value pair
                watches_dict[watch_name] = watch_price
        # return the finalized watches dictionary
        return watches_dict
    
    except Exception as e:
        print(f"Error has occurred: {e}")
        return {}

# Create a function that filters watches based on a target price range
def watch_shortlist(page_count, target_price, plus_minus):
    '''
    Input: 
        page_count (int): number of pages of watch listings the user would like to scrape
        target_price (float/int): The target price around which to filter watches
        plus_minus (float/int): The range (plus or minus) to apply to the target price

    Process: Use the get_watches function to get the full directory of listed watches and extract those within the specified price range
    Output: a DataFrame containing watch names and their prices within the specified price range in ascending order
    '''
    
    # Call the function to scrape watches from the auction site for the specified number of pages
    watches = get_watches(page_count = page_count)
    
    # Initialize an empty DataFrame to hold the shortlisted watches
    shortlist_df = pd.DataFrame()

    # Calculate the lower and upper price bounds for the filter
    price_lower_bound = max(0, target_price - plus_minus)
    price_upper_bound = target_price + plus_minus

    # Iterate over the scraped watches (key = watch name, value = watch price)
    for key, value in watches.items():

        # If the watch price falls within the specified price range
        if value >= price_lower_bound and value <= price_upper_bound:
            
            # Create a new DataFrame row with the watch name and price
            row = pd.DataFrame({"Name": [key], "Price": [value]})

            # Append the new row to the shortlist DataFrame using pd.cocat
            shortlist_df = pd.concat([shortlist_df, row], ignore_index=True)
    
    # Sort the final shortlist DataFrame by price in ascending order
    shortlist_df = shortlist_df.sort_values(by=["Price"], ascending= True)
    
    # Return the final shortlist dataframe
    return shortlist_df

# Add user interactability
maxPageCount = int(input("How deep (in terms of number of pages) do you want to dive into the auction listing? "))
targetPrice = int(input("What's your target price? (I suggest you don't go below 100 if you're serious about buying one of these watches) "))
plusMinus = int(input("How much higher than your target price are you willing to go? "))

watch_list = watch_shortlist(page_count = maxPageCount, target_price = targetPrice, plus_minus = plusMinus)

print(watch_list)