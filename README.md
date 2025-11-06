# 📘 Reading Companion

See the live demo here: http://readingcompanion-402223167.eu-west-2.elb.amazonaws.com/

The **Reading Companion** is a tool designed to make research articles, journals, and technical texts easier to understand. Whether you're a student, curious learner, or just tired of fake news, this app helps you break through the jargon.

## ✨ Features
- **Simplify Technical Text**: Rewrite academic or technical content into plain English, perfect for readers of all levels. Just paste the link of the scientific paper, paste your text or upload the PDF you wish to simplify. 
- **Key Definitions**: Extract and explain important terms and jargon.  
- **Questions & Answers**: Generate follow-up questions and answers to test understanding.  
- **Summaries of Long Texts**: Break down long, hard-to-read documents into digestible parts, then provide a concise overall summary. You can download this summary/the chunks as a PDF. 

## ⚙️ How It Works
The app is powered by **ChatGPT** but with extra processing steps to ensure accuracy and readability:

1. **Text Extraction from URLs**  
   Many research papers are online and ChatGPT alone isn’t always able to open or interpret these links correctly.  
   That’s why we first **extract the raw text content from the page**. This ensures that only the relevant article body is passed forward, without ads, navigation bars, or cookie banners.  

2. **Chunking for Large Documents**  
   ChatGPT has a *context window* - a limit to how many tokens (words + characters) it can process at once.  
   Research papers often exceed this limit, so instead of cutting text off, we **split the document into chunks** at natural sentence boundaries. Each chunk is simplified individually.  
   Finally, we produce an **overall summary** from the simplified chunks, ensuring that key details aren’t lost.

3. **Better Accuracy**  
   By combining **text extraction** and **chunking**, the Reading Companion delivers more reliable and detailed simplifications than sending a raw link or giant block of text directly to ChatGPT.

## 🛠️ Tech Stack
- [Streamlit](https://streamlit.io/) – for the web app interface  
- [OpenAI GPT](https://platform.openai.com/) – for simplification, definitions, and summaries  
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) & scraping helpers – for extracting clean text from research articles  
- [tiktoken](https://github.com/openai/tiktoken) – for token counting and chunking logic
- [Docker](https://www.docker.com/) - for depolyment environment
- [AWS](https://aws.amazon.com/ecs/) - to host my demo! 

## 🚀 Perfect For
- Students looking to understand academic research  
- Lifelong learners wanting accurate insights beyond clickbait headlines  
- Anyone struggling with dense or jargon-heavy writing

