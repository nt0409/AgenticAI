import logging
import ollama

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


# Function to read content from 'scrape.txt'
def read_text_file() -> str:
    """
    Fetches content from 'scrape.txt' to use as reference for generating a blog.

    Returns:
        str: The content of the file or an error message if the file is not found.
    """
    file_path = "scrape.txt"
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return "Error: The file 'scrape.txt' was not found."
    except Exception as e:
        return f"An error occurred: {e}"


# **Enhanced System Prompt for Concise & Engaging Blog**
SYSTEM_PROMPT = """\
You are an expert AI content writer. Your task is to extract key information from a given text file, \
remove any redundant or duplicate content, and summarize it into a **concise, engaging, and structured blog**. \
**Only use the provided content—do not introduce new facts or details.**

### **Processing Guidelines:**
1. **Step 1:** Use the `read_text_file` tool to fetch content from 'scrape.txt'.  
2. **Step 2:** **Summarize** the content—keep only the most important details.  
3. **Step 3:** Structure the blog with **a strong introduction, key takeaways, and a conclusion**.  
4. **Step 4:** Use **bullet points, short paragraphs, and subheadings** to improve readability.  
5. **Step 5:** **Keep the blog within 300-400 words** for conciseness.  

### **Blog Format Example:**
**Title:** [Short & Catchy Headline]  
**Introduction:** Brief 2-3 sentence intro that sets the context.  
**Key Highlights:** Short, structured bullet points summarizing key details.  
**Conclusion:** A final takeaway or closing thought.  

**Write in a professional yet engaging tone, ensuring clarity and factual accuracy.**
"""


# Function to generate a **concise & summarized** blog automatically
def generate_blog() -> str:
    """
    Automatically processes 'scrape.txt' to generate a structured and summarized blog.

    Returns:
        str: The generated blog content.
    """
    logging.info("Fetching content from 'scrape.txt'...")

    response = ollama.chat(
        model="llama3.1",  # Use the latest Llama model
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "Process the provided content into a concise and engaging blog."},
        ],
        tools=[read_text_file],  # Automatically pass the function as a tool
    )

    # **Handling Tool Calls**
    available_functions = {
        "read_text_file": read_text_file,
    }

    for tool_call in response.message.tool_calls or []:
        function_to_call = available_functions.get(tool_call.function.name)
        if function_to_call:
            file_content = function_to_call()
            logging.info("File content successfully fetched.")
            return file_content
        else:
            logging.error(f"Function not found: {tool_call.function.name}")

    return response.message.content  # Return the AI-generated blog


# **Function to Write Blog to External File**
def save_blog_to_file(blog_content: str, filename: str = "blog.txt") -> None:
    """
    Saves the generated blog content to an external text file.

    Args:
        blog_content (str): The content to be written to the file.
        filename (str): The name of the file where content will be saved (default: 'blog.txt').
    """
    try:
        with open(filename, "w", encoding="utf-8") as file:
            file.write(blog_content)
        logging.info(f"Blog successfully written to {filename}")
    except Exception as e:
        logging.error(f"Failed to write blog to file: {e}")


# **Execute Automatically**
if __name__ == "__main__":
    logging.info("Starting blog generation...")
    blog_output = generate_blog()

    # Save the generated blog content to an external file
    save_blog_to_file(blog_output)

    print("\n### **Generated Blog Content (Saved to blog.txt):**\n")
    print(blog_output)
