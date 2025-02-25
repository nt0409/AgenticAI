#src.py

import asyncio
from playwright.async_api import async_playwright
import re
from datetime import datetime
import os
from urllib.parse import urlparse
import json
from bs4 import BeautifulSoup
import random
import csv
import glob

class NewsScraper:
    def __init__(self):
        self.output_dir = "scraped_articles"
        os.makedirs(self.output_dir, exist_ok=True)
        self.log_file = os.path.join(self.output_dir, "scraping_log.json")
        
        # Enhanced noise patterns
        self.noise_patterns = [
            r'Share\s+(?:on\s+)?(?:Facebook|Twitter|WhatsApp|LinkedIn|Email)',
            r'(?:Published|Updated|Posted)\s+(?:On|By|Date):?\s*.*?\d{4}',
            r'Listen to Story',
            r'Watch Live TV',
            r'Download App',
            r'Follow Us',
            r'SIGN IN',
            r'Subscribe',
            r'TRENDING TOPICS:.*',
            r'Must Read.*?(?=\n|$)',
            r'Published By:.*?(?=\n|$)',
            r'In Short.*?(?=\n|$)',
            r'\d+ Views',
            r'Advertisement|ADVERTISEMENT',
            r'Copyright ©.*?\d{4}',
            r'All rights reserved',
            r'Read More',
            r'Also Read:.*?(?=\n|$)',
            r'Click here to.*?(?=\n|$)',
            r'Follow us on.*?(?=\n|$)',
        ]
        self.noise_regex = re.compile('|'.join(self.noise_patterns), re.IGNORECASE | re.MULTILINE)

        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15"
        ]

    async def setup_browser(self):
        """Configure browser with anti-detection measures"""
        browser = await self.playwright.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-features=site-per-process',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--disable-gpu',
                '--window-size=1920,1080',
            ]
        )
        
        context = await browser.new_context(
            user_agent=random.choice(self.user_agents),
            viewport={'width': 1920, 'height': 1080},
            bypass_csp=True,
            extra_http_headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
            }
        )

        # Add stealth scripts
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            
            window.chrome = {
                runtime: {},
                loadTimes: function() {},
                csi: function() {},
                app: {}
            };
        """)
        
        return browser, context

    async def wait_for_content(self, page):
        """Enhanced waiting strategy for content"""
        try:
            # Wait for initial load
            await page.wait_for_load_state('domcontentloaded', timeout=30000)
            
            # Try multiple content indicators
            content_selectors = [
                'article',
                '.article-content',
                '.story-content',
                'div[class*="article"]',
                '.entry-content',
                'p'
            ]
            
            # Wait for any of the selectors to appear
            for selector in content_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=5000)
                    return True
                except:
                    continue
                    
            return False
            
        except Exception as e:
            print(f"Wait error (non-critical): {e}")
            return False

    async def scrape_article(self, url, title, source, timestamp, output_dir):
        self.playwright = await async_playwright().start()
        try:
            browser, context = await self.setup_browser()
            page = await context.new_page()
            
            print(f"\nScraping: {url}")
            
            # Enhanced page loading strategy
            try:
                # Initial navigation with longer timeout
                response = await page.goto(
                    url,
                    wait_until='domcontentloaded',
                    timeout=60000
                )
                
                if not response.ok:
                    print(f"Failed to load page: {response.status}")
                    return None
                
                # Wait for content to be available
                content_found = await self.wait_for_content(page)
                if not content_found:
                    print("Warning: Content indicators not found, but continuing...")
                
                # Add random delay to mimic human behavior
                await page.wait_for_timeout(random.randint(2000, 4000))
                
                # Scroll smoothly
                await page.evaluate("""
                    window.scrollTo({
                        top: document.body.scrollHeight,
                        behavior: 'smooth'
                    });
                """)
                await page.wait_for_timeout(1000)
                
                # Try multiple extraction methods
                content = None
                
                # Method 1: Direct HTML method
                try:
                    content = await page.evaluate("""() => {
                        const article = document.querySelector('article, .article-content, .story-content');
                        return article ? article.innerText : null;
                    }""")
                except:
                    pass
                
                # Method 2: BeautifulSoup fallback
                if not content:
                    html = await page.content()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Remove unwanted elements
                    for elem in soup.select('script, style, nav, header, footer, iframe, .ads, .social-share'):
                        elem.decompose()
                    
                    # Try multiple selectors
                    article = (
                        soup.find('article') or 
                        soup.find(class_=lambda x: x and 'article' in x.lower()) or
                        soup.find(class_=lambda x: x and 'story' in x.lower()) or
                        soup.find('main')
                    )
                    
                    if article:
                        content = article.get_text(separator='\n', strip=True)
                
                # Method 3: Paragraph collection
                if not content:
                    paragraphs = await page.evaluate("""() => {
                        return Array.from(document.getElementsByTagName('p'))
                            .filter(p => p.innerText.length > 50)
                            .map(p => p.innerText)
                            .join('\\n\\n');
                    }""")
                    if paragraphs:
                        content = paragraphs
                
                if content:
                    cleaned_content = self.clean_content(content)
                    if cleaned_content:
                        print("\nContent found! Saving...")
                        return self.save_content(url, cleaned_content, title, source, timestamp, output_dir)
                
                print("No valid content could be extracted")
                return None
                
            except Exception as e:
                print(f"Scraping error: {e}")
                return None
                
        finally:
            await context.close()
            await browser.close()
            await self.playwright.stop()

    def clean_content(self, content):
        """Enhanced content cleaning"""
        if not content:
            return None
            
        # Remove noise patterns
        content = self.noise_regex.sub('', content)
        
        # Clean up whitespace
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
        content = re.sub(r'[ \t]+', ' ', content)
        
        # Remove lines that look like navigation elements
        lines = [line.strip() for line in content.split('\n')]
        lines = [
            line for line in lines 
            if len(line) > 30 or re.search(r'\d{4}', line)
            and not any(x in line.lower() for x in ['click', 'subscribe', 'follow', 'download'])
        ]
        
        # Remove duplicate paragraphs
        seen = set()
        unique_lines = []
        for line in lines:
            normalized = re.sub(r'\s+', ' ', line.lower())
            if normalized not in seen:
                seen.add(normalized)
                unique_lines.append(line)
        
        cleaned = '\n\n'.join(unique_lines).strip()
        
        # Only return if we have substantial content
        return cleaned if len(cleaned) > 200 else None

    def generate_filename(self, title):
        """Generate a filename based on title and timestamp"""
        # Create a safe filename from the title by replacing disallowed characters
        safe_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in title)
        safe_title = safe_title[:50].strip()  # Limit title length
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{safe_title}_{timestamp}.txt"

    def save_content(self, url, content, title, source, timestamp, output_dir):
        """Save content to file and update log"""
        try:
            filename = self.generate_filename(title)
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Title: {title}\n")
                f.write(f"URL: {url}\n")
                f.write(f"Source: {source}\n")
                f.write(f"Original Timestamp: {timestamp}\n")
                f.write(f"Scraped Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("-" * 80 + "\n\n")
                f.write(content)
            
            log_entry = {
                "title": title,
                "url": url,
                "source": source,
                "filename": filename,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "success"
            }
            
            self._update_log(log_entry)
            
            print(f"\nContent saved to: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"Error saving content: {e}")
            return None

    def _update_log(self, log_entry):
        """Update the log file with new entry"""
        try:
            log_data = []
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r') as f:
                    try:
                        log_data = json.load(f)
                    except json.JSONDecodeError:
                        pass
            
            log_data.append(log_entry)
            
            with open(self.log_file, 'w') as f:
                json.dump(log_data, f, indent=2)
                
        except Exception as e:
            print(f"Error updating log: {e}")

async def process_csv_files(folder, output_folder):
    """Process all CSV files in the specified folder"""
    print(f"\nProcessing CSV files from {folder} folder")
    
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Find all CSV files in the folder
    csv_files = glob.glob(os.path.join(folder, "*.csv"))
    
    if not csv_files:
        print(f"No CSV files found in {folder} folder")
        return
    
    scraper = NewsScraper()
    
    # Process each CSV file
    for csv_file in csv_files:
        print(f"\nProcessing CSV file: {csv_file}")
        
        try:
            with open(csv_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter='|')
                # Skip header row
                next(reader, None)
                
                for row in reader:
                    if len(row) >= 4:  # Ensure we have title, url, source, timestamp
                        title = row[0].strip()
                        url = row[1].strip()
                        source = row[2].strip()
                        timestamp = row[3].strip()
                        
                        print(f"\nProcessing article: {title}")
                        
                        if url:
                            # Scrape the article
                            result = await scraper.scrape_article(url, title, source, timestamp, output_folder)
                            if not result:
                                print(f"Scraping failed for URL: {url}")
                        else:
                            print(f"Missing URL for article: {title}")
                    else:
                        print(f"Invalid row format: {row}")
                        
        except Exception as e:
            print(f"Error processing CSV file {csv_file}: {e}")

async def main():
    # Process both local and national folders
    modes = [
        ("local", "local_scraped"),
        ("national", "national_scraped")
    ]
    
    for source_folder, output_folder in modes:
        if os.path.exists(source_folder):
            await process_csv_files(source_folder, output_folder)
        else:
            print(f"Folder {source_folder} does not exist")

if __name__ == "__main__":
    asyncio.run(main())