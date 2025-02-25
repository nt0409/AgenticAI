import logging
import ollama
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost
from wordpress_xmlrpc.methods.media import UploadFile
import json
import os
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
    local_scraped_folder: str = "local_scraped"
    national_scraped_folder: str = "national_scraped"
    topic: Optional[str] = None
    wordpress: Optional[WordPressConfig] = None
    category: str = "Hindi"  # Default category

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

    def publish_post(self, content: str, categories: List[str] = ['Hindi']) -> Tuple[Optional[str], Optional[str]]:
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

            logging.info(f"Hindi post published successfully with ID: {post_id}")
            logging.info(f"Hindi Post URL: {post_url}")

            return post_id, post_url

        except Exception as e:
            logging.error(f"Failed to publish Hindi post to WordPress: {e}")
            return None, None

def read_text_file(file_path: str) -> str:
    """Reads content from the provided text file."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return "Error: The file was not found."
    except Exception as e:
        return f"An error occurred: {e}"

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

def translate_to_hindi(content: str) -> str:
    """
    Translates the provided content into Hindi using the LLM.

    Args:
        content (str): The English content to be translated.

    Returns:
        str: The Hindi translated content.
    """
    try:
        response = ollama.chat(
            model="llama3.1:8b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a highly accurate translation model. "
                        "Translate the following English text into Hindi, ensuring the tone, context, and meaning are preserved:"
                        "Heading:"
                            "Font: Larger and Bolder (e.g., 24px, Bold)"
                            "Example:"
                            "भारत में तकनीकी विकास"
                            "Body:"

                            "Font: Smaller and Regular (e.g., 16px, Regular)"
                            "Example:"
                                "भारत में तकनीकी विकास तेजी से बढ़ रहा है। यह शिक्षा, स्वास्थ्य और अन्य क्षेत्रों में नई संभावनाएँ उत्पन्न कर रहा है।"
                    )
                },
                {"role": "user", "content": content}
            ]
        )
        translated_content = response.message.content.strip()
        return translated_content
    except Exception as e:
        logging.error(f"Error during Hindi translation: {e}")
        return "Error: Could not perform translation."

def generate_hindi_blog_from_file(file_path: str, config: BlogConfig) -> Tuple[str, bool, str]:
    """
    Generate blog content in English, translate to Hindi, and optionally publish only the Hindi version.

    Args:
        file_path (str): Path to the input file.
        config (BlogConfig): The configuration for the blog generation.

    Returns:
        Tuple[str, bool, str]: Tuple containing the Hindi blog content, whether the operation succeeded, and the output file path.
    """
    wordpress_publisher = None if not config.wordpress else WordPressPublisher(config.wordpress)

    # Read content from input file
    file_content = read_text_file(file_path)
    if "Error" in file_content:
        logging.error(f"Could not read input file {file_path}. Skipping.")
        return file_content, False, ""

    # Determine topic
    topic = determine_blog_topic(file_content)
    logging.info(f"Determined blog topic from {file_path}: {topic}")

    # Generate blog content in English (intermediate step)
    system_prompt = (
        "You are a professional blog writer. Create a detailed, well-structured blog post based on the following topic:"
        "1. STRUCTURE THE BLOG:"
        "Title: Create a clear, engaging title with primary SEO keywords"
        "Introduction: Brief context-setting opening with relevant keywords naturally incorporated"
        "Key Points: Main takeaways or highlights with keyword variations for better ranking"
        "Analysis: Insights and implications with internal linking suggestions if applicable"
        "Conclusion: Final thoughts or summary with a call-to-action (CTA) to engage readers"
    )
    try:
        response = ollama.chat(
            model="llama3.1:8b",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {"role": "user", "content": f"Create a blog post about: {topic}\n\nReference content: {file_content}"}
            ]
        )
        blog_content = response.message.content.strip()
        logging.info(f"Generated English blog content for {file_path} as intermediate step.")
    except Exception as e:
        logging.error(f"Error generating blog content for {file_path}: {e}")
        return "Error: Blog generation failed.", False, ""

    # Translate blog content to Hindi
    hindi_translation = translate_to_hindi(blog_content)
    logging.info(f"Successfully translated blog content from {file_path} to Hindi.")

    # Get file name without extension
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    
    # Create output folder if it doesn't exist
    os.makedirs(config.output_folder, exist_ok=True)
    
    # Output file path
    output_file_path = os.path.join(config.output_folder, f"{file_name}_hindi.txt")
    
    # Save Hindi version to file
    with open(output_file_path, "w", encoding="utf-8") as hindi_file:
        hindi_file.write(hindi_translation)
    logging.info(f"Hindi blog saved to {output_file_path}")

    # Determine category based on folder
    categories = ["Hindi", "Blog"]
    if "local" in file_path.lower():
        categories.append("Local News")
    elif "national" in file_path.lower():
        categories.append("National News")

    # Optionally publish to WordPress (Hindi only)
    if wordpress_publisher:
        post_id, post_url = wordpress_publisher.publish_post(
            hindi_translation,
            categories=categories
        )
        if post_id:
            logging.info(f"Hindi blog from {file_path} published successfully with ID: {post_id}")
            logging.info(f"Post URL: {post_url}")
        else:
            logging.error(f"Failed to publish Hindi blog from {file_path} to WordPress")

    return hindi_translation, True, output_file_path

def process_folder(folder_path: str, config: BlogConfig) -> List[Tuple[str, bool, str]]:
    """
    Process all text files in a folder.

    Args:
        folder_path (str): Path to the folder containing text files.
        config (BlogConfig): The configuration for blog generation.

    Returns:
        List[Tuple[str, bool, str]]: List of tuples containing the Hindi blog content, 
                                   whether the operation succeeded, and the output file path.
    """
    results = []
    
    if not os.path.exists(folder_path):
        logging.warning(f"Folder {folder_path} does not exist. Skipping.")
        return results
        
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".txt"):
            file_path = os.path.join(folder_path, file_name)
            logging.info(f"Processing file: {file_path}")
            
            hindi_blog, success, output_path = generate_hindi_blog_from_file(file_path, config)
            results.append((hindi_blog, success, output_path))
            
    return results

def process_all_folders(config: BlogConfig) -> Dict[str, List[Tuple[str, bool, str]]]:
    """
    Process all folders specified in the config.

    Args:
        config (BlogConfig): The configuration for blog generation.

    Returns:
        Dict[str, List[Tuple[str, bool, str]]]: Dictionary mapping folder names to results.
    """
    results = {}
    
    # Process local scraped content
    logging.info(f"Processing local scraped content from {config.local_scraped_folder}")
    local_results = process_folder(config.local_scraped_folder, config)
    results["local"] = local_results
    
    # Process national scraped content
    logging.info(f"Processing national scraped content from {config.national_scraped_folder}")
    national_results = process_folder(config.national_scraped_folder, config)
    results["national"] = national_results
    
    return results

if __name__ == "__main__":
    # Example configuration
    wp_config = WordPressConfig(
        url="https://newsagents8.wordpress.com",
        username="shashwat569800",
        password="black@12345600"
    )
    
    config = BlogConfig(
        wordpress=wp_config,
        local_scraped_folder="local_scraped",
        national_scraped_folder="national_scraped",
        output_folder="generated_blogs",
        min_words=400,
        max_words=600
    )
    
    logging.info("Starting Hindi blog generation process...")
    
    # Process all folders
    results = process_all_folders(config)
    
    # Print summary
    logging.info("=== Blog Generation Summary ===")
    
    total_processed = 0
    total_succeeded = 0
    
    for folder, folder_results in results.items():
        processed = len(folder_results)
        succeeded = sum(1 for _, success, _ in folder_results if success)
        
        logging.info(f"{folder.capitalize()} folder: Processed {processed} files, {succeeded} succeeded")
        
        total_processed += processed
        total_succeeded += succeeded
        
    logging.info(f"Total: Processed {total_processed} files, {total_succeeded} succeeded")
    
    if total_succeeded > 0:
        logging.info(f"Generated blogs saved to {config.output_folder}")