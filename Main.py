# #main.py

# import asyncio
# import os
# from crawl import NewsCrawler
# from src import NewsScraper, process_csv_files

# async def main():
#     print("\n===== NEWS CRAWLER AND SCRAPER =====\n")
    
#     # Step 1: Run the crawler to gather article URLs
#     crawler = NewsCrawler()
    
#     # Get user input for news type
#     while True:
#         news_level = input("What type of news do you want to crawl? (national/state): ").strip().lower()
#         if news_level in ['national', 'state']:
#             break
#         print("Invalid input. Please enter 'national' for Indian national news or 'state' for state-specific news.")
    
#     # If state is selected, ask which state
#     news_type = 'national'  # Default
#     if news_level == 'state':
#         states = ['maharashtra', 'karnataka', 'bihar', 'delhi', 'westbengal']
#         state_names = "Maharashtra, Karnataka, Bihar, Delhi, West Bengal"
        
#         while True:
#             state_input = input(f"Which state's news do you want? ({state_names}): ").strip().lower()
#             # Remove spaces and normalize input
#             state_input = state_input.replace(" ", "")
            
#             # Handle "west bengal" as a special case
#             if state_input == "westbengal" or state_input == "bengal":
#                 state_input = "westbengal"
            
#             if state_input in states:
#                 news_type = state_input
#                 break
#             print(f"Invalid state. Please enter one of: {state_names}")
    
#     print(f"\nCrawling {news_type} news articles from the last 3 days...")
#     articles = crawler.crawl_news(news_type)
    
#     filename = f"{news_type}_news.csv"
#     # Save to appropriate folder
#     csv_saved = crawler.save_to_csv(articles, filename, news_level)
    
#     if not csv_saved:
#         print("No articles were found to scrape. Exiting.")
#         return
    
#     # Step 2: Run the scraper on the collected URLs
#     print("\n===== SCRAPING ARTICLES =====\n")
    
#     # Define the input and output folders based on the news level
#     input_folder = 'national' if news_level == 'national' else 'local'
#     output_folder = f"{input_folder}_scraped"
    
#     # Process the CSV files to scrape articles
#     await process_csv_files(input_folder, output_folder)
    
#     print("\n===== CRAWLING AND SCRAPING COMPLETE =====")
#     print(f"Scraped articles are saved in the '{output_folder}' folder")

# if __name__ == "__main__":
#     asyncio.run(main())




import asyncio
import os
import subprocess
from crawl import NewsCrawler
from src import NewsScraper, process_csv_files

async def main():
    print("\n===== NEWS CRAWLER, SCRAPER, AND BLOG GENERATOR =====\n")
    
    # Get all user inputs at the beginning
    
    # Input 1: News level (national/state)
    while True:
        news_level = input("What type of news do you want to crawl? (national/state): ").strip().lower()
        if news_level in ['national', 'state']:
            break
        print("Invalid input. Please enter 'national' for Indian national news or 'state' for state-specific news.")
    
    # Input 2: State selection (if applicable)
    news_type = 'national'  # Default
    if news_level == 'state':
        states = ['maharashtra', 'karnataka', 'bihar', 'delhi', 'westbengal']
        state_names = "Maharashtra, Karnataka, Bihar, Delhi, West Bengal"
        
        while True:
            state_input = input(f"Which state's news do you want? ({state_names}): ").strip().lower()
            # Remove spaces and normalize input
            state_input = state_input.replace(" ", "")
            
            # Handle "west bengal" as a special case
            if state_input == "westbengal" or state_input == "bengal":
                state_input = "westbengal"
            
            if state_input in states:
                news_type = state_input
                break
            print(f"Invalid state. Please enter one of: {state_names}")
    
    # Input 3: Language selection for blog generation
    while True:
        language = input("In which language do you want to generate blogs? (english/hindi): ").strip().lower()
        if language in ['english', 'hindi']:
            break
        print("Invalid input. Please enter 'english' or 'hindi'.")
    
    # Confirm all selections before proceeding
    print("\n===== SELECTED OPTIONS =====")
    print(f"News Type: {news_level.capitalize()}")
    if news_level == 'state':
        print(f"State: {news_type.capitalize()}")
    print(f"Blog Language: {language.capitalize()}")
    print("============================\n")
    
    # Step 1: Run the crawler to gather article URLs
    print("\n===== CRAWLING NEWS ARTICLES =====\n")
    crawler = NewsCrawler()
    print(f"Crawling {news_type} news articles from the last 3 days...")
    articles = crawler.crawl_news(news_type)
    
    filename = f"{news_type}_news.csv"
    # Save to appropriate folder
    csv_saved = crawler.save_to_csv(articles, filename, news_level)
    
    if not csv_saved:
        print("No articles were found to scrape. Exiting.")
        return
    
    # Step 2: Run the scraper on the collected URLs
    print("\n===== SCRAPING ARTICLES =====\n")
    
    # Define the input and output folders based on the news level
    input_folder = 'national' if news_level == 'national' else 'local'
    output_folder = f"{input_folder}_scraped"
    
    # Process the CSV files to scrape articles
    await process_csv_files(input_folder, output_folder)
    
    print("\n===== CRAWLING AND SCRAPING COMPLETE =====")
    print(f"Scraped articles are saved in the '{output_folder}' folder")
    
    # Step 3: Generate blogs in the selected language
    print(f"\n===== GENERATING {language.upper()} BLOGS =====\n")
    try:
        if language == 'english':
            subprocess.run(['python', 'english_blog.py', output_folder], check=True)
        else:  # hindi
            subprocess.run(['python', 'hindi_blog.py', output_folder], check=True)
        
        print(f"\n===== {language.upper()} BLOG GENERATION COMPLETE =====")
    except subprocess.CalledProcessError as e:
        print(f"Error running the {language} blog generation script: {e}")
    except FileNotFoundError:
        print(f"Error: {language}_blog.py script not found. Please make sure it exists in the current directory.")

if __name__ == "__main__":
    asyncio.run(main())