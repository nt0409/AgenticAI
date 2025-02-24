# AgenticAI

# 📰 AI-Powered News Aggregator & Blog Compiler

## 📌 Overview
This project scrapes the latest news from multiple sources, processes the extracted data, and compiles it into a well-structured blog. Whether you need *local news (Mumbai-based)* or *global/national news*, this tool efficiently gathers, refines, and publishes content automatically.

## 🚀 Features
- *Multi-Source Scraping* – Fetches news from various reliable sources.
- *Automatic Blog Generation* – Summarizes and structures news into an engaging blog format.
- *User Credentials & Publishing* – Supports publishing to predefined URLs via user login.
- *Dynamic Selection* – Choose between *local (Mumbai-based)* and *global (national)* news.
- *Simple Execution* – Just run a single Python script to get started.

## 🛠 Setup Instructions

### 1️⃣ Installation
Ensure you have Python installed, then clone this repository and install dependencies:
bash
# Clone the repository
git clone https://github.com/yourusername/news-scraper-blog.git
cd news-scraper-blog

# Install dependencies
pip install -r requirements.txt


### 2️⃣ Configuration
Create a .env file in the root directory and add your credentials:
ini
PUBLISH_URL=https://yourblogplatform.com/api/publish
USERNAME=your_username
PASSWORD=your_secure_password


### 3️⃣ Running the Scraper
To start scraping and compiling news into a blog, navigate to the project folder and run:
bash
python agent.py

The script will prompt you to select the news type:
- Enter local for *Mumbai-based news*
- Enter global for *national news*

Once selected, the script will scrape news, format it into a blog, and publish it using the credentials provided in the .env file.

## 📌 Example Output
markdown
# Today's Headlines: Mumbai Edition

### 🔹 Major Traffic Updates
Mumbai's traffic congestion saw a significant rise due to...

### 🔹 Political Developments
The latest updates on the Maharashtra state assembly...

### 🔹 Business & Finance
The stock market saw a surge in...

**Read more at [yourblogplatform.com](https://yourblogplatform.com)**


## 🔧 Troubleshooting
- *Issue: The script doesn’t start*  
  Ensure Python is installed and dependencies are installed using pip install -r requirements.txt.
- *Issue: News not scraping properly*  
  Check your internet connection and ensure that news sources are accessible.
- *Issue: Publishing fails*  
  Verify your .env file credentials and publishing URL.

## 📜 License
This project is open-source under the *MIT License*. Feel free to contribute and improve it!
