# import logging
# import ollama
# from typing import Dict, Any, Optional
# from dataclasses import dataclass

# # Configure logging
# logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# @dataclass
# class BlogConfig:
#     """Configuration for blog generation."""
#     max_words: int = 400
#     min_words: int = 300
#     output_file: str = "blog.txt"
#     input_file: str = "scrape.txt"

# def read_text_file(filepath: str) -> str:
#     """
#     Read content from a text file.

#     Args:
#         filepath: Path to the text file to read

#     Returns:
#         str: The content of the file or an error message if the file is not found
#     """
#     try:
#         with open(filepath, "r", encoding="utf-8") as file:
#             return file.read()
#     except FileNotFoundError:
#         return f"Error: The file '{filepath}' was not found."
#     except Exception as e:
#         return f"An error occurred: {e}"

# def save_blog_content(content: str, filepath: str) -> bool:
#     """
#     Save blog content to a file.

#     Args:
#         content: The blog content to save
#         filepath: Path where to save the blog

#     Returns:
#         bool: True if save was successful, False otherwise
#     """
#     try:
#         with open(filepath, "w", encoding="utf-8") as file:
#             file.write(content)
#         return True
#     except Exception as e:
#         logging.error(f"Failed to save blog: {e}")
#         return False

# def process_tool_calls(response, available_functions: Dict[str, Any]) -> Optional[str]:
#     """
#     Process tool calls from the model response.

#     Args:
#         response: The model response containing tool calls
#         available_functions: Dictionary of available functions

#     Returns:
#         Optional[str]: The processed content or None if processing failed
#     """
#     if not hasattr(response.message, 'tool_calls') or not response.message.tool_calls:
#         return response.message.content

#     result = []
#     for tool_call in response.message.tool_calls:
#         function_name = tool_call.function.name
#         function_to_call = available_functions.get(function_name)
        
#         if function_to_call:
#             try:
#                 # Parse arguments from the tool call
#                 args = tool_call.function.arguments
#                 if isinstance(args, str):
#                     # Handle case where arguments might be a string
#                     import json
#                     args = json.loads(args)
                
#                 # Execute the function with the provided arguments
#                 output = function_to_call(**args)
#                 result.append(output)
#             except Exception as e:
#                 logging.error(f"Error executing {function_name}: {e}")
#                 continue
#         else:
#             logging.warning(f"Function not found: {function_name}")
    
#     return "\n".join(result) if result else None

# def generate_blog(config: BlogConfig = BlogConfig()) -> str:
#     """
#     Generate a blog post using Ollama with function calling.

#     Args:
#         config: BlogConfig instance with generation parameters

#     Returns:
#         str: The generated blog content
#     """
#     system_prompt = f"""You are an expert AI content writer. Generate a concise, engaging blog post 
#     between {config.min_words} and {config.max_words} words using the provided content from the input file. 
#     Use the read_text_file function to access the content, then structure it with:

#     1. A catchy title
#     2. A brief introduction
#     3. Key points in a clear structure
#     4. A meaningful conclusion

#     Focus on clarity and engagement while maintaining accuracy to the source material."""

#     # Define available functions
#     available_functions = {
#         "read_text_file": read_text_file,
#     }

#     try:
#         # Initial call to get the source content
#         response = ollama.chat(
#             model="llama3.1:8b",
#             messages=[
#                 {"role": "system", "content": system_prompt},
#                 {"role": "user", "content": f"Please read the content from {config.input_file} and create a blog post."}
#             ],
#             tools=[read_text_file]
#         )

#         # Process the tool calls and get the content
#         source_content = process_tool_calls(response, available_functions)
#         if not source_content:
#             raise ValueError("Failed to read source content")

#         # Generate the blog using the source content
#         blog_response = ollama.chat(
#             model="llama3.1:8b",
#             messages=[
#                 {"role": "system", "content": system_prompt},
#                 {"role": "user", "content": source_content}
#             ]
#         )

#         blog_content = blog_response.message.content
        
#         # Save the generated blog
#         if save_blog_content(blog_content, config.output_file):
#             logging.info(f"Blog successfully saved to {config.output_file}")
#         else:
#             logging.error("Failed to save blog")

#         return blog_content

#     except Exception as e:
#         error_msg = f"Error generating blog: {e}"
#         logging.error(error_msg)
#         return error_msg

# if __name__ == "__main__":
#     config = BlogConfig()
#     logging.info("Starting blog generation...")
#     blog_output = generate_blog(config)
#     print("\n### Generated Blog Content ###\n")
#     print(blog_output)


import requests

wordpress_url = "https://newsagents8.wordpress.com"
wordpress_user = "shashwat569800"
wordpress_password = "black@12345600"

post_data = {
    "title": "My Sample Blog Post",  # This is the post title
    "content": """
        <h1 style="font-weight: bold; color: black; text-decoration: underline;">
            My Custom Site Title
        </h1>
        <p>This is a sample blog post where I want to add a custom-styled site title inside the content.</p>
    """,
    "status": "publish"
}

response = requests.post(wordpress_url, auth=(wordpress_user, wordpress_password), json=post_data)

if response.status_code == 201:
    print("Post published successfully:", response.json()["link"])
else:
    print("Failed to publish post:", response.text)
