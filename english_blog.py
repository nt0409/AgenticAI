import logging
import ollama
import os
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost
from wordpress_xmlrpc.methods.media import UploadFile
import json
import re
from datetime import datetime
from wordpress_xmlrpc.methods.users import GetUserInfo
from wordpress_xmlrpc.methods.posts import GetPost

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

@dataclass
class WordPressConfig:
    """WordPress configuration."""
    url: str
    username: str
    password: str
    xmlrpc_path: str = "xmlrpc.php"

@dataclass
class BlogConfig:
    """Configuration for blog generation."""
    max_words: int = 800
    min_words: int = 400
    output_folder: str = "generated_blogs"
    local_input_folder: str = "local_scraped"
    national_input_folder: str = "national_scraped"
    topic: Optional[str] = None
    wordpress: Optional[WordPressConfig] = None

class BlogFormatter:
    """Handles blog content formatting and structure."""
    
    @staticmethod
    def format_title(title: str) -> str:
        """Format the blog title without any site title or navigation."""
        title = re.sub(r'^\*+.*?\*+\s*\n', '', title)
        title = re.sub(r'^\*\s*About\s*\n', '', title)
        title = re.sub(r'Title:|[\*#]', '', title).strip()
        
        return f'''
            <header class="entry-header">
                <h1 class="entry-title" style="
                    font-size: 32px;
                    line-height: 1.4;
                    color: #333;
                    margin: 40px 0 30px 0;
                    font-weight: 700;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen-Sans, Ubuntu, Cantarell, 'Helvetica Neue', sans-serif;
                    text-decoration: none;
                ">{title}</h1>
            </header>
        '''
    @staticmethod
    def format_section(title: str, content: str) -> str:
        """Format a blog section with inline styles."""
        title = re.sub(r'[\*#]', '', title).strip()
        content = re.sub(r'[\*#]', '', content).strip()
        
        return f'''
            <section class="blog-section" style="margin: 40px 0;">
                <h2 style="
                    color: #2c3e50;
                    font-size: 24px;
                    margin-bottom: 20px;
                    font-weight: 600;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen-Sans, Ubuntu, Cantarell, 'Helvetica Neue', sans-serif;
                ">{title}</h2>
                <div class="section-content" style="
                    line-height: 1.8;
                    color: #444;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen-Sans, Ubuntu, Cantarell, 'Helvetica Neue', sans-serif;
                ">{content}</div>
            </section>
        '''

    @staticmethod
    def format_introduction(section: str) -> str:
        """Format the introduction section."""
        intro = re.sub(r'Introduction:|[\*#]', '', section).strip()
        return f'''
            <div class="introduction" style="
                font-size: 18px;
                line-height: 1.8;
                color: #555;
                margin: 0 0 40px 0;
                font-weight: 400;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen-Sans, Ubuntu, Cantarell, 'Helvetica Neue', sans-serif;
            ">{intro}</div>
        '''
    
    @staticmethod
    def format_key_points(points: List[str]) -> str:
        """Format key points as a styled list."""
        formatted_points = []
        for point in points:
            clean_point = re.sub(r'^[-*•]\s*', '', point).strip()
            formatted_points.append(f'''
                <li style="
                    margin-bottom: 15px;
                    line-height: 1.6;
                    color: #444;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen-Sans, Ubuntu, Cantarell, 'Helvetica Neue', sans-serif;
                ">{clean_point}</li>
            ''')
        
        return f'''
            <div class="key-points" style="margin: 30px 0;">
                <h3 style="
                    color: #2c3e50;
                    font-size: 22px;
                    margin-bottom: 20px;
                    font-weight: 600;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen-Sans, Ubuntu, Cantarell, 'Helvetica Neue', sans-serif;
                ">Key Points</h3>
                <ul style="
                    padding-left: 20px;
                    list-style-type: disc;
                ">{''.join(formatted_points)}</ul>
            </div>
        '''

class WordPressPublisher:
    def __init__(self, config: WordPressConfig):
        self.config = config
        self.client = Client(
            f"{config.url}/{config.xmlrpc_path}",
            config.username,
            config.password
        )
        self.formatter = BlogFormatter()

    def generate_seo_slug(self, content: str) -> str:
        """Generate SEO-friendly slug."""
        title_match = re.search(r'Title:(.+?)(?:\n|$)', content)
        title = title_match.group(1).strip() if title_match else content.split('\n')[0].strip()

        # Clean up the title
        slug = re.sub(r'[^\w\s-]', '', title.lower())  # Remove special characters
        slug = re.sub(r'[-\s]+', '-', slug)  # Convert spaces to hyphens
        slug = slug.strip('-')  # Remove leading/trailing hyphens

        return slug 

    def format_content(self, content: str) -> str:
        """Format content for WordPress with inline styles."""
        try:
            sections = content.split('\n\n')
            formatted_parts = []
            
            for section in sections:
                section = section.strip()
                if not section:
                    continue
                
                if 'Title:' in section or section.startswith('***'):
                    formatted_parts.append(self.formatter.format_title(section))
                elif 'Introduction:' in section:
                    formatted_parts.append(self.formatter.format_introduction(section))
                elif 'Key Highlights:' in section or 'Key Points:' in section:
                    points = [p for p in section.split('\n')[1:] if p.strip()]
                    formatted_parts.append(self.formatter.format_key_points(points))
                elif ':' in section:
                    title, *content = section.split(':')
                    formatted_parts.append(self.formatter.format_section(
                        title, ':'.join(content)
                    ))
                else:
                    formatted_parts.append(f'''
                        <p style="
                            margin-bottom: 20px;
                            line-height: 1.8;
                            color: #444;
                            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen-Sans, Ubuntu, Cantarell, 'Helvetica Neue', sans-serif;
                        ">{section}</p>
                    ''')
            
            return f'''
                <article class="blog-post" style="
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen-Sans, Ubuntu, Cantarell, 'Helvetica Neue', sans-serif;
                ">{''.join(formatted_parts)}</article>
            '''
            
        except Exception as e:
            logging.error(f"Content formatting failed: {e}")
            return content

    def publish_post(self, content: str, categories: List[str] = ['Blog']) -> Tuple[Optional[str], Optional[str]]:
        """Publish post to WordPress with SEO-friendly URL."""
        try:
            post = WordPressPost()

            # Extract title from content
            title_match = re.search(r'Title:(.+?)(?:\n|$)', content)
            post.title = title_match.group(1).strip() if title_match else content.split('\n')[0].strip()

            # Generate slug
            post.slug = self.generate_seo_slug(content)

            # Format and assign content
            post.content = self.format_content(content)
            post.terms_names = {'category': categories}
            post.post_status = 'publish'

            # Publish the post
            post_id = self.client.call(NewPost(post))

            # Retrieve the actual published post to get the correct slug
            published_post = self.client.call(GetPost(post_id))
            post_slug = published_post.slug
            post_url = published_post.link  # This gets the correct live URL

            logging.info(f"Post published successfully with ID: {post_id}")
            logging.info(f"Correct Post URL: {post_url}")

            return post_id, post_url

        except Exception as e:
            logging.error(f"Failed to publish to WordPress: {e}")
            return None, None

    def generate_meta_description(self, content: str, max_length: int = 160) -> str:
        """Generate SEO meta description from content."""
        clean_content = re.sub(r'<[^>]+>', '', content)
        clean_content = ' '.join(clean_content.split())
        
        if len(clean_content) > max_length:
            clean_content = clean_content[:max_length]
            clean_content = clean_content[:clean_content.rindex(' ')] + '...'
        
        return clean_content

def read_text_file(file_path: str) -> str:
    """Reads content from the provided text file."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return f"Error: The file {file_path} was not found."
    except Exception as e:
        return f"An error occurred reading {file_path}: {e}"

def determine_blog_topic(file_content: str) -> str:
    """Uses the LLM to determine the best blog topic based on the provided content."""
    try:
        response = ollama.chat(
            model="llama3.1:8b",
            messages=[
                {
                    "role": "system", 
                    "content": "Analyze the provided content and extract the main topic or theme."
                },
                {"role": "user", "content": file_content}
            ]
        )
        return response.message.content.strip()
    except Exception as e:
        logging.error(f"Error determining blog topic: {e}")
        return "Unknown Topic"

def get_source_files(config: BlogConfig) -> List[Tuple[str, str]]:
    """
    Get all text files from local and national folders.
    
    Returns:
        List of tuples containing (filepath, category)
    """
    files = []
    
    # Check if folders exist and create if they don't
    if not os.path.exists(config.local_input_folder):
        os.makedirs(config.local_input_folder)
        logging.info(f"Created folder: {config.local_input_folder}")
    
    if not os.path.exists(config.national_input_folder):
        os.makedirs(config.national_input_folder)
        logging.info(f"Created folder: {config.national_input_folder}")
    
    if not os.path.exists(config.output_folder):
        os.makedirs(config.output_folder)
        logging.info(f"Created folder: {config.output_folder}")
    
    # Get local files
    if os.path.exists(config.local_input_folder):
        for filename in os.listdir(config.local_input_folder):
            if filename.endswith('.txt'):
                filepath = os.path.join(config.local_input_folder, filename)
                files.append((filepath, "Local"))
    
    # Get national files
    if os.path.exists(config.national_input_folder):
        for filename in os.listdir(config.national_input_folder):
            if filename.endswith('.txt'):
                filepath = os.path.join(config.national_input_folder, filename)
                files.append((filepath, "National"))
    
    return files

def generate_blog(file_path: str, category: str, config: BlogConfig) -> Tuple[str, bool]:
    """Generate blog content and publish to WordPress if configured."""
    
    wordpress_publisher = None if not config.wordpress else WordPressPublisher(config.wordpress)
    
    # Read content from input file
    file_content = read_text_file(file_path)
    if "Error" in file_content:
        logging.error(f"Could not read input file {file_path}. Skipping.")
        return file_content, False
    
    # Extract filename without extension for output file
    filename = os.path.basename(file_path)
    filename_without_ext = os.path.splitext(filename)[0]
    
    # Determine topic
    config.topic = determine_blog_topic(file_content)
    logging.info(f"Determined blog topic for {filename}: {config.topic}")

    system_prompt = """\
        You are an expert AI content analyst and writer, specializing in transforming raw data into clear, engaging, and SEO-optimized blog posts. Your task is to:

        1. ANALYZE & CLEAN DATA:
        - Extract key information from raw input
        - Remove duplicates and redundant information
        - Identify the most important points and insights

        2. STRUCTURE THE BLOG:
        Title: Create a clear, engaging title with primary SEO keywords
        Introduction: Brief context-setting opening with relevant keywords naturally incorporated
        Key Points: Main takeaways or highlights with keyword variations for better ranking
        Analysis: Insights and implications with internal linking suggestions if applicable
        Conclusion: Final thoughts or summary with a call-to-action (CTA) to engage readers

        3. WRITING STYLE:
        - Clear and professional tone
        - Short, concise, and focused paragraphs
        - Active voice
        - No technical jargon unless necessary
        - Engaging but factual
        - Naturally integrate high-ranking keywords and long-tail keyword variations 

        4. SEO OPTIMIZATION:
        - Use **primary and secondary SEO keywords** naturally in headings and throughout the content
        - Optimize **meta description** within 150-160 characters summarizing the post with keywords
        - Maintain a **keyword density of 1-2%** without overstuffing
        - Ensure content is structured with **proper H1, H2, and H3 tags**
        - Include **internal links** (where applicable) to relevant blog content
        - Use **SEO-friendly URLs** by keeping slugs concise and keyword-rich
        - Write compelling **meta titles** under 60 characters to maximize CTR
        - Encourage user engagement through a clear **Call-to-Action (CTA)** in the conclusion

        5. FORMAT:
        - Use clean, simple formatting
        - No markdown symbols or special characters
        - Clear section breaks
        - Consistent structure throughout

        Focus on delivering valuable insights in a well-organized, easy-to-read format, ensuring maximum search engine visibility. Keep the content within 300 words while maintaining high readability and engagement.
    """

    try:
        # Generate blog content
        response = ollama.chat(
            model="llama3.1:8b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Create a blog post about: {config.topic}\n\nReference content: {file_content}"}
            ]
        )

        blog_content = response.message.content

        # Save locally
        output_file = os.path.join(config.output_folder, f"{filename_without_ext}_blog.txt")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(blog_content)

        logging.info(f"Blog successfully written to {output_file}")

        # Format and publish to WordPress if configured
        if wordpress_publisher:
            # Add the source category (Local or National) to the post categories
            categories = ['Blog', category]
            post_id, post_url = wordpress_publisher.publish_post(blog_content, categories=categories)
            if post_id:
                logging.info(f"Successfully published {filename} to WordPress with ID: {post_id}")
                logging.info(f"Post URL: {post_url}")

        return blog_content, True

    except Exception as e:
        error_msg = f"Error generating blog for {file_path}: {e}"
        logging.error(error_msg)
        return error_msg, False

def process_all_files(config: BlogConfig):
    """Process all files in the local and national folders."""
    source_files = get_source_files(config)
    
    if not source_files:
        logging.warning("No source files found in the specified folders.")
        return
    
    logging.info(f"Found {len(source_files)} files to process.")
    
    success_count = 0
    failure_count = 0
    
    for file_path, category in source_files:
        logging.info(f"Processing {file_path} as {category} news...")
        blog_content, success = generate_blog(file_path, category, config)
        
        if success:
            success_count += 1
        else:
            failure_count += 1
    
    logging.info(f"Processing complete. {success_count} blogs generated successfully, {failure_count} failures.")

if __name__ == "__main__":
    # Example configuration
    wp_config = WordPressConfig(
        url="https://newsagents8.wordpress.com",
        username="shashwat569800",
        password="black@12345600"
    )
    
    config = BlogConfig(
        wordpress=wp_config,
        min_words=400,
        max_words=600,
        local_input_folder="local_scraped",
        national_input_folder="national_scraped",
        output_folder="generated_blogs"
    )
    
    logging.info("Starting blog generation process for multiple files...")
    process_all_files(config)