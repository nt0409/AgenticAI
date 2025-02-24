import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import random
from urllib.parse import quote, urlparse
import re
from datetime import datetime
from difflib import SequenceMatcher

class NewsRelatedFinder:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.google.com/',
            'DNT': '1',
        }
        
        self.news_sources = [
            'indiatoday.in',
            'ndtv.com',
            'hindustantimes.com',
            'indianexpress.com',
            'thehindu.com',
            'news18.com',
            'timesofindia.indiatimes.com',
            'economictimes.indiatimes.com',
            'livemint.com',
            'moneycontrol.com',
            'firstpost.com',
            'indiatvnews.com'
        ]

        # Important location keywords
        self.locations = {
            'mumbai', 'delhi', 'bangalore', 'kolkata', 'chennai', 'hyderabad',
            'marine lines', 'bandra', 'andheri', 'borivali', 'thane', 'vashi',
            'india', 'maharashtra'
        }

        # Event type keywords
        self.event_types = {
            'fire', 'accident', 'crash', 'protest', 'election', 'arrest',
            'launch', 'announcement', 'inauguration', 'death', 'murder',
            'robbery', 'theft', 'festival', 'celebration'
        }

    def clean_title(self, title):
        """Clean and normalize news title"""
        # Remove common suffixes
        title = re.sub(r'\s*[-|]\s*(?:Live Updates?|Breaking News?|Watch|Latest|Today News).*$', '', title, flags=re.I)
        # Remove year in parentheses
        title = re.sub(r'\s*\(\d{4}\)\s*$', '', title)
        # Remove special characters but keep important punctuation
        title = re.sub(r'[^\w\s,-]', ' ', title)
        return title.strip()

    def extract_entities(self, title):
        """Extract location and event type from title"""
        words = set(w.lower() for w in title.split())
        locations = words & self.locations
        events = words & self.event_types
        return locations, events

    def extract_keywords(self, title):
        """Enhanced keyword extraction focusing on key entities and context"""
        title = self.clean_title(title)
        words = title.lower().split()
        
        # Extract locations and event types
        locations, events = self.extract_entities(title)
        
        # Get important context words (longer words are often more meaningful)
        context_words = [w for w in words if len(w) > 3 and 
                        not w.isdigit() and
                        w not in {'says', 'said', 'will', 'new', 'news', 'update', 
                                'year', 'day', 'latest', 'watch', 'breaking'}]
        
        # Prioritize locations and events in the query
        keywords = list(locations) + list(events) + context_words
        
        # Remove duplicates while preserving order
        seen = set()
        keywords = [x for x in keywords if not (x in seen or seen.add(x))]
        
        return ' '.join(keywords[:5])  # Limit to top 5 most relevant keywords

    def calculate_similarity(self, title1, title2):
        """Calculate similarity between two titles using multiple metrics"""
        # Clean titles
        clean1 = self.clean_title(title1).lower()
        clean2 = self.clean_title(title2).lower()
        
        # Extract entities
        loc1, event1 = self.extract_entities(clean1)
        loc2, event2 = self.extract_entities(clean2)
        
        # Location and event type matching
        loc_match = bool(loc1 & loc2)
        event_match = bool(event1 & event2)
        
        # Sequence matcher for overall similarity
        sequence_ratio = SequenceMatcher(None, clean1, clean2).ratio()
        
        # Word overlap
        words1 = set(clean1.split())
        words2 = set(clean2.split())
        word_overlap = len(words1 & words2) / max(len(words1), len(words2))
        
        # Combined score with weights
        similarity = (
            (0.4 * sequence_ratio) +  # Overall sequence similarity
            (0.3 * word_overlap) +    # Word overlap
            (0.2 * int(loc_match)) +  # Location match
            (0.1 * int(event_match))  # Event type match
        )
        
        return similarity

    def search_google_news(self, title, max_results=5, retries=3):
        """Search Google News with improved query and filtering"""
        keywords = self.extract_keywords(title)
        sites = ' OR '.join([f'site:{src}' for src in self.news_sources])
        
        # Add date restriction to get more recent and relevant results
        search_query = quote(f'"{keywords}" {sites}')
        url = f'https://www.google.com/search?q={search_query}&tbm=nws&gl=IN&num={max_results*2}'  # Request more results for better filtering
        
        related_articles = []
        original_entities = self.extract_entities(title)
        
        for attempt in range(retries):
            try:
                response = requests.get(url, headers=self.headers, timeout=15)
                if response.status_code != 200:
                    print(f"Search failed: {response.status_code}")
                    continue
                    
                soup = BeautifulSoup(response.text, 'html.parser')
                articles = soup.find_all('div', class_='SoaBEf')
                
                for article in articles:
                    try:
                        title_elem = article.find('div', role='heading')
                        article_title = title_elem.get_text().strip() if title_elem else None
                        
                        if not article_title:
                            continue
                            
                        # Calculate similarity score
                        similarity = self.calculate_similarity(title, article_title)
                        
                        # Only include articles with high similarity
                        if similarity < 0.4:  # Increased threshold for better accuracy
                            continue
                            
                        link_elem = article.find('a', href=True)
                        if not link_elem:
                            continue
                            
                        article_link = link_elem['href'].split('&')[0]
                        if not article_link.startswith('http'):
                            continue
                            
                        domain = urlparse(article_link).netloc.lower()
                        if not any(src in domain for src in self.news_sources):
                            continue
                            
                        related_articles.append({
                            'title': article_title,
                            'url': article_link,
                            'source': domain,
                            'similarity': similarity
                        })
                        
                    except Exception as e:
                        print(f"Article processing error: {str(e)}")
                        continue
                
                # Sort by similarity and take top results
                related_articles.sort(key=lambda x: x['similarity'], reverse=True)
                related_articles = related_articles[:max_results]
                
                if related_articles:
                    break
                    
                time.sleep(random.uniform(5, 8))
                
            except Exception as e:
                print(f"Attempt {attempt+1} failed: {str(e)}")
                time.sleep(random.uniform(10, 15))
                continue
            
        return related_articles

    def process_news_csv(self, input_file, output_file):
        """Process CSV file with improved filtering"""
        try:
            df = pd.read_csv(input_file, delimiter='|')
            print(f"Processing {len(df)} articles from {input_file}")
            
            results = []
            
            for idx, row in df.iterrows():
                original_title = row['title']
                original_url = row['url']
                original_source = row['source']
                
                print(f"\nProcessing ({idx+1}/{len(df)}: {original_title[:80]}...")
                
                related_articles = self.search_google_news(original_title)
                
                # Filter out duplicates and original article
                filtered = []
                seen_urls = {original_url.lower()}
                
                for article in related_articles:
                    art_url = article['url'].lower()
                    if (art_url != original_url.lower() and 
                        not any(src in art_url for src in seen_urls)):
                        filtered.append(article)
                        seen_urls.add(art_url)
                
                result = {
                    'original_title': original_title,
                    'original_url': original_url,
                    'original_source': original_source,
                    'related_count': len(filtered),
                    'related_sources': '|'.join(a['source'] for a in filtered),
                    'related_urls': '|'.join(a['url'] for a in filtered),
                    'related_titles': '|'.join(a['title'] for a in filtered),
                    'similarity_scores': '|'.join(str(round(a['similarity'], 2)) for a in filtered)
                }
                
                results.append(result)
                
                # Progress saving
                if (idx + 1) % 5 == 0:
                    pd.DataFrame(results).to_csv(output_file, index=False, sep='|')
                    print(f"Saved interim results after {idx+1} articles")
                
                time.sleep(random.uniform(2, 4))
            
            # Final save
            pd.DataFrame(results).to_csv(output_file, index=False, sep='|')
            print(f"Processing complete. Results saved to {output_file}")
            
        except Exception as e:
            print(f"CSV processing error: {str(e)}")

def main():
    finder = NewsRelatedFinder()
    
    print("Starting national news processing...")
    finder.process_news_csv('national_news.csv', 'national_perspectives.csv')
    
    print("\nStarting local news processing after 30 second cooldown...")
    time.sleep(30)
    finder.process_news_csv('mumbai_news.csv', 'mumbai_perspectives.csv')

if __name__ == "__main__":
    main()