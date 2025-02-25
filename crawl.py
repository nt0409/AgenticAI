#crawl.py

import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import random
from datetime import datetime, timedelta
import re
import os

class NewsCrawler:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'DNT': '1',
        }
        
        # Define news sources - National and State-specific
        self.sources = {
            'national': [
                {
                    'name': 'Times of India - India',
                    'base_url': 'https://timesofindia.indiatimes.com',
                    'feed_url': 'https://timesofindia.indiatimes.com/india'
                },
                {
                    'name': 'NDTV',
                    'base_url': 'https://www.ndtv.com',
                    'feed_url': 'https://www.ndtv.com/india'
                }
            ],
            'maharashtra': [
                {
                    'name': 'Times of India - Maharashtra',
                    'base_url': 'https://timesofindia.indiatimes.com',
                    'feed_url': 'https://timesofindia.indiatimes.com/city/mumbai'
                },
                {
                    'name': 'Hindustan Times - Maharashtra',
                    'base_url': 'https://www.hindustantimes.com',
                    'feed_url': 'https://www.hindustantimes.com/cities/mumbai-news'
                }
            ],
            'karnataka': [
                {
                    'name': 'Times of India - Karnataka',
                    'base_url': 'https://timesofindia.indiatimes.com',
                    'feed_url': 'https://timesofindia.indiatimes.com/city/bengaluru'
                },
                {
                    'name': 'Deccan Herald',
                    'base_url': 'https://www.deccanherald.com',
                    'feed_url': 'https://www.deccanherald.com/state'
                }
            ],
            'bihar': [
                {
                    'name': 'Times of India - Bihar',
                    'base_url': 'https://timesofindia.indiatimes.com',
                    'feed_url': 'https://timesofindia.indiatimes.com/city/patna'
                },
                {
                    'name': 'Hindustan Times - Bihar',
                    'base_url': 'https://www.hindustantimes.com',
                    'feed_url': 'https://www.hindustantimes.com/cities/patna-news'
                }
            ],
            'delhi': [
                {
                    'name': 'Times of India - Delhi',
                    'base_url': 'https://timesofindia.indiatimes.com',
                    'feed_url': 'https://timesofindia.indiatimes.com/city/delhi'
                },
                {
                    'name': 'Hindustan Times - Delhi',
                    'base_url': 'https://www.hindustantimes.com',
                    'feed_url': 'https://www.hindustantimes.com/cities/delhi-news'
                }
            ],
            'westbengal': [
                {
                    'name': 'Times of India - West Bengal',
                    'base_url': 'https://timesofindia.indiatimes.com',
                    'feed_url': 'https://timesofindia.indiatimes.com/city/kolkata'
                },
                # {
                #     'name': 'Telegraph India',
                #     'base_url': 'https://www.telegraphindia.com',
                #     'feed_url': 'https://www.telegraphindia.com/west-bengal'
                # }
            ]
        }

    def extract_date_from_url(self, url):
        """Try to extract date from URL to check if it's recent"""
        date_patterns = [
            r'(\d{4})/(\d{1,2})/(\d{1,2})',  # YYYY/MM/DD
            r'(\d{4})-(\d{1,2})-(\d{1,2})',  # YYYY-MM-DD
            r'/(\d{4})(\d{2})(\d{2})/',      # YYYYMMDD
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, url)
            if match:
                try:
                    year, month, day = map(int, match.groups())
                    article_date = datetime(year, month, day)
                    
                    # Check if article is within last 3 days
                    three_days_ago = datetime.now() - timedelta(days=3)
                    if article_date >= three_days_ago:
                        return True
                except ValueError:
                    continue
        
        # If we can't determine the date from URL, include it anyway
        return True

    def crawl_source(self, source, max_articles=5, retries=3):
        """Crawl a specific news source"""
        articles = []
        
        for attempt in range(retries):
            try:
                print(f"Crawling {source['name']}...")
                response = requests.get(source['feed_url'], headers=self.headers, timeout=15)
                
                if response.status_code != 200:
                    print(f"Failed to fetch from {source['name']}: {response.status_code}")
                    time.sleep(random.uniform(1, 3))
                    continue
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find all links that might be news articles
                links = soup.find_all('a', href=True)
                
                # Process each link
                for link in links:
                    url = link['href']
                    
                    # Skip empty, javascript, and anchor links
                    if not url or url.startswith('javascript:') or url.startswith('#'):
                        continue
                    
                    # Make relative URLs absolute
                    if not url.startswith('http'):
                        if url.startswith('/'):
                            url = source['base_url'] + url
                        else:
                            url = source['base_url'] + '/' + url
                    
                    # Only include URLs from the same domain
                    domain = source['base_url'].split('//')[1].split('/')[0]
                    if domain not in url:
                        continue
                    
                    # Skip duplicate URLs
                    if any(article['url'] == url for article in articles):
                        continue
                    
                    # Skip URLs with query parameters (often not articles)
                    if '?' in url and ('search' in url.lower() or 'tag' in url.lower()):
                        continue
                        
                    # Skip category pages, tag pages, etc.
                    skip_patterns = ['category', 'tag/', 'author/', 'topics/', 'videos/', 'photos/', 'section/']
                    if any(pattern in url.lower() for pattern in skip_patterns):
                        continue
                    
                    # Try to extract title
                    # First look for header elements within the link
                    title_elem = None
                    for selector in ['h1', 'h2', 'h3', '.headline', '.title', '[class*="title"]', '[class*="heading"]']:
                        elements = link.select(selector)
                        if elements:
                            title_elem = elements[0]
                            break
                    
                    # If no header found, use the link text itself if substantial
                    if not title_elem:
                        title_text = link.get_text().strip()
                        if len(title_text) >= 30 and len(title_text) <= 200:  # Reasonable title length
                            title_elem = link
                    
                    # Skip if no valid title element found
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text().strip()
                    
                    # Skip if title is too short or empty
                    if not title or len(title) < 20:
                        continue
                    
                    # Check if the article seems recent based on URL
                    if self.extract_date_from_url(url):
                        articles.append({
                            'title': title,
                            'url': url,
                            'source': source['name'],
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                    
                    # Stop if we have enough articles
                    if len(articles) >= max_articles:
                        break
                
                if articles:
                    print(f"Found {len(articles)} articles from {source['name']}")
                    break
                else:
                    print(f"No articles found from {source['name']}, trying another source")
                
                time.sleep(random.uniform(1, 2))
                
            except Exception as e:
                print(f"Attempt {attempt+1} failed for {source['name']}: {str(e)}")
                time.sleep(random.uniform(2, 4))
                
        return articles

    def crawl_news(self, news_type='national'):
        """Crawl news based on type (national or state)"""
        all_articles = []
        
        for source in self.sources[news_type]:
            source_articles = self.crawl_source(source)
            all_articles.extend(source_articles)
            
            # Add a small delay between sources
            time.sleep(random.uniform(1, 3))
        
        return all_articles

    def save_to_csv(self, articles, filename, news_level='national'):
        """Save articles to CSV file in the appropriate folder"""
        try:
            if not articles:
                print(f"No articles to save to {filename}")
                return False
            
            # Create appropriate folder if it doesn't exist
            folder = 'national' if news_level == 'national' else 'local'
            if not os.path.exists(folder):
                os.makedirs(folder)
                print(f"Created {folder} folder")
            
            # Full path for the file
            file_path = os.path.join(folder, filename)
                
            df = pd.DataFrame(articles)
            df = df.drop_duplicates(subset=['url'])  # Remove any duplicate URLs
            df.to_csv(file_path, index=False, sep='|')
            print(f"Successfully saved {len(df)} articles to {file_path}")
            return True
        except Exception as e:
            print(f"Error saving to CSV: {str(e)}")
            return False

def main():
    crawler = NewsCrawler()
    
    # Step 1: Get user input for news type (national or state)
    while True:
        news_level = input("What type of news do you want to crawl? (national/state): ").strip().lower()
        if news_level in ['national', 'state']:
            break
        print("Invalid input. Please enter 'national' for Indian national news or 'state' for state-specific news.")
    
    # Step 2: If state is selected, ask which state
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
    
    print(f"\nCrawling {news_type} news articles from the last 3 days...")
    articles = crawler.crawl_news(news_type)
    
    filename = f"{news_type}_news.csv"
    # Pass news_level to determine which folder to use
    crawler.save_to_csv(articles, filename, news_level)
    
    print("\nCrawling complete!")

if __name__ == "__main__":
    main()