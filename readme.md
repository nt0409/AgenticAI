# 🏆 Flipr Hackathon 2025 - AI News Crawler & Blog Generator 🚀

An **autonomous AI-powered system** to **crawl**, **scrape**, **generate**, and **publish** news articles **automatically** in multiple languages. **Fully optimized for SEO, ensuring 90+ scores on Google PageSpeed Insights!**

## 🌟 Why This Project?

💡 **AI-Driven Automation:** No human intervention needed! The system fetches, processes, and posts blogs seamlessly.  
🌍 **Multilingual Support:** Generates blogs in **English & Hindi**.  
📰 **Covers National & State-Specific News:** Fetches from leading Indian news sources.  
⚡ **SEO-Optimized Content:** Achieves high search engine rankings effortlessly.  
🤖 **Powered by Open-Source AI:** Utilizes **LLaMA 3.1 8B** for high-quality blog generation.  
✍️ **Instant WordPress Publishing:** Automates content posting directly to your WordPress blog.  

🔗 **Live Demo:** [NewsAgents8 Blog](https://newsagents8.wordpress.com/)  

---

## 📌 System Components

### 🔍 1. AI-Powered News Crawler (`crawl.py`)
- Uses **Playwright** for efficient, headless web crawling.
- Supports both **national** and **state-specific** news sources.
- Stores article URLs, publication dates, and titles.

### 📝 2. Smart News Scraper (`src.py`)
- Extracts **text, images, metadata** using **BeautifulSoup**.
- Cleans, processes, and structures the extracted content.

### 🤖 3. AI Blog Generators
- **English Blog Generator** (`english_blog.py`)
- **Hindi Blog Generator** (`hindi_blog.py`)
- Uses **LLaMA 3.1 8B** via **Ollama** for engaging, high-quality content.
- Implements **SEO optimization** for **90+ Google PageSpeed Insights** scores.

### 🌐 4. WordPress Auto-Publishing
- Uploads **text, media files, tags, and categories**.
- Manages post status (**draft/publish**).

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository
```sh
git clone <your-repo-url>
cd <your-repo-folder>
```

### 2️⃣ Install Dependencies
```sh
pip install -r requirements.txt
playwright install  # Install Playwright browsers
```

### 3️⃣ Configure Environment Variables
Create a `.env` file in the root directory:
```env
WP_URL="https://newsagents8.wordpress.com"
WP_USERNAME="shashwat569800"
WP_PASSWORD="black@12345600"
OLLAMA_MODEL="llama3"
SEO_TARGET_SCORE=90
```

### 4️⃣ Run the System 🚀
```sh
python main.py
```

---

## 📢 How It Works

1️⃣ Choose **National** or **State-Level** news.  
2️⃣ If **State-Level**, select a **state** (Maharashtra, Karnataka, Bihar, Delhi, West Bengal).  
3️⃣ Pick **English or Hindi** for blog generation.  
4️⃣ The AI:
   - Scrapes news ✅
   - Generates a blog ✅
   - Optimizes for SEO ✅
   - Publishes it automatically ✅

---

## 🚀 SEO-Optimized Blog Generation
🔹 **High-Quality Content:** AI maintains accuracy & readability.  
🔹 **Keyword Optimization:** Strategic placement for search visibility.  
🔹 **Schema Markup:** Boosts Google indexing.  
🔹 **Image Optimization:** ALT tags & fast loading.  
🔹 **Mobile-Responsive Formatting.**  

---

## 📁 Directory Structure
```
├── main.py              # Main entry point
├── crawl.py             # News crawler module
├── src.py               # News scraper module
├── english_blog.py      # English blog generator
├── hindi_blog.py        # Hindi blog generator
├── .env                 # Environment variables
├── requirements.txt     # Dependencies
├── national/            # Storage for national news
├── local/               # Storage for state-specific news
└── scraped_content/     # Processed blog data
```

---

## ⚡ Advanced Customization

### 🔧 Customizing LLM Parameters
Modify blog generator settings:
```python
response = ollama.generate(
    model=os.getenv("OLLAMA_MODEL"),
    prompt=prompt,
    temperature=0.7,
    max_tokens=int(os.getenv("BLOG_MAX_LENGTH", 1500))
)
```

### 🌍 Adding More States
Modify `main.py`:
```python
states = ['maharashtra', 'karnataka', 'bihar', 'delhi', 'westbengal', 'new_state']
```
Add corresponding sources in `crawl.py`.

---

## 🔥 Troubleshooting & Security

🛠 **Common Issues:**
- **Crawling errors?** Check your internet or Playwright installation.
- **Scraping errors?** Ensure BeautifulSoup selectors match site structure.
- **Blog generation fails?** Verify Ollama is running.
- **WordPress publishing issues?** Confirm XML-RPC access is enabled.

🔒 **Security Notes:**
- **Never commit your `.env` file!**
- Use a password manager for credentials.
- Rotate WordPress passwords periodically.

---

## 📜 License & Acknowledgements

📜 **License:** [MIT License](LICENSE)  
🙏 Special thanks to **Playwright, Ollama, and BeautifulSoup** communities.  

---

🎯 **Built for Flipr Hackathon 2025**  
🚀 **AI-Powered. Fully Automated. SEO-Optimized.**
