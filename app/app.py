import os
import streamlit as st
from pathlib import Path

from reading_companion.core.nlp.simplify import simplify_text
from reading_companion.core.scraping.text_from_url import extract_main_text
from reading_companion.core.nlp.explain_terms import explain_terms
from reading_companion.core.nlp.question_gen import question_gen, question_answers
from reading_companion.core.data.example_text import example_text
import fitz  
from st_social_media_links import SocialMediaIcons
from reading_companion.core.nlp.llm_chunking import token_count, simplify_long_text_with_summary
from reading_companion.core.utils.pdf_gen import data_for_pdf
from reading_companion.app.controllers import decide_source_text, simplify_flow

st.set_page_config(layout="centered")

# Streamlit button click reruns script top to bottom, allow for persistance 
def _ensure_state(section: str):
    st.session_state.setdefault(f"{section}_processed", None)
    st.session_state.setdefault(f"{section}_simplified", None)
    st.session_state.setdefault(f"{section}_overall", None)
    st.session_state.setdefault(f"{section}_questions", None)
    st.session_state.setdefault(f"{section}_answers", None)
    st.session_state.setdefault("uploaded_file", None)


def show_cover_image() -> None:
    """Render cover image if present (and not disabled)."""
    if os.getenv("RC_SKIP_IMAGES"):
        return  # useful for CI

    img_path = Path(__file__).parent / "imgs" / "new_cover_image.png"
    if img_path.exists():
        st.image(str(img_path))
    else:
        # Don’t crash the app if the file is missing in some envs
        st.info("")  # or just pass    

# Header / Site Introduction

st.title(""" Reading Companion """)

st.write(""" Journals and research articles are brilliant tools for learning and staying informed, but they’re often written in academic language that’s hard to digest. The Reading Companion helps you break through the jargon.
With this tool you can provide any article or journal extract, and it will:

• Simplify the text into easy-to-read language
         
• Explain key words and terminology
         
• Ask follow-up questions to check your understanding

Whether you're a student, curious learner, or just tired of misinformation, the Reading Companion helps you understand research!
""")

show_cover_image()

# Tools
def display_tools(user_input, section): 
    
    _ensure_state(section)

    left, middle, right = st.columns(3)
   
    if left.button("Reading Companion", icon="📘", use_container_width=True, key=(section + "1")):
        with st.spinner("Simplifying..."):
            
            # Decide the source text to simplify (raw text or fetched from URL)
            source_text, warn = decide_source_text(
                user_input=user_input,
                uploaded_file_used=bool(st.session_state.get("uploaded_file")),
                fetch_from_url=extract_main_text,
            )
            if warn:
                st.warning(warn)
                return
            
            result = simplify_flow(
                source_text=source_text,
                token_count_fn=token_count,
                simplify_fn=simplify_text,
                chunked_pipeline_fn=simplify_long_text_with_summary,
                token_budget=3000,
            )

            st.session_state[f"{section}_processed"] = result["processed"]
            st.session_state[f"{section}_simplified"] = result["simplified"]
            st.session_state[f"{section}_overall"] = result["overall"]

            if result["chunked"]:
                st.write("That was a lot of text, so we used intelligent chunking.")
                st.markdown(f"**Overall Summary** {result['overall']}")
                st.download_button(
                    label="Export All Simplified Chunks (PDF)",
                    data=data_for_pdf(result["simplified"]),
                    file_name="simplified.pdf",
                    mime="application/pdf",
                )
            else:
                st.markdown(f"**Simplified:** {result['simplified']}")
                

    if middle.button("Key defintions", icon="🔍", use_container_width=True, key=(section + "2")):
        with st.spinner("Finding key terms..."):
            src = st.session_state.get(f"{section}_processed") or user_input
            if not src or not src.strip():
                st.warning("Please run 📘 Reading Companion first, or paste text.")
            else:    
                dictionary = explain_terms(src)
                st.markdown(f"**Key terms and Defintions:** \n {dictionary}")


    if right.button("Generate Questions", icon="📝", use_container_width=True, key=(section + "3")):
       with st.spinner("Generating Questions..."):
            src = st.session_state.get(f"{section}_processed") or user_input
            if not src or not src.strip():
                st.warning("Please run 📘 Reading Companion first, or paste text.")
            else: 
                questions = question_gen(src)
                st.session_state[f"{section}_questions"] = questions
                st.session_state[f"{section}_answers"] = None  # reset answers
                st.markdown(f"**Questions to check your understanding:** \n {questions}") 
        
       with st.expander("💡 See Answers"):  
            answers = question_answers(questions)
            st.markdown(f"**Answers:** \n {answers}")
            st.session_state[f"{section}_answers"] = answers


# Main Section/ Expanders

with st.expander("💡 See Example"):
    st.subheader("Example")
    st.write("Try to read and understand this extract from a scientific paper:") 
    st.write(example_text)
    url = "https://link.springer.com/article/10.1186/s12978-024-01797-y"
    st.write("Link to research paper: [Vitamin D and Reproductive Disorders](%s)" % url)
    st.subheader("Now use our tools:")
    
    display_tools(example_text,"example")


with st.expander("🛠️ Use Now"):
    st.subheader("Try It Yourself")
    user_input = st.text_area("Paste your paragraph below or provide the web link or upload a pdf:")
    
    # Allowing for a file to be uploaded instead 
    st.write("or")
    uploaded_file = st.file_uploader("Choose a file")
    
    if uploaded_file is not None:
        st.session_state["uploaded_file"] = True
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            user_input = ""
            for page in doc:
                user_input += page.get_text()
    else: 
        st.session_state["uploaded_file"] = False
    
    st.write("")

    display_tools(user_input, "use_now")
     

with st.expander("🌟 See our Monthly Top Picks"):
    st.subheader("3 Research papers made simple, for real news: ")
    st.write("""Every month, we handpick 3 research papers we find fascinating covering areas like health, science, psychology, economics, and technology.

We encourage you to start by giving the original paper a go! Then dive into the Reading Companion summary for a simplified version, key definitions, and follow-up questions to test your understanding.

We often end up reading more 'fake news' in our curated feeds than real research-backed insights, perhaps because research papers feel inaccessible or overwhelming. Our aim is to change that by spotlighting great reads each month.

🗓️ New articles drop on the 1st of every month.
             
📚 Whether you're unsure where to begin or not used to reading journals, we've got you covered.""")
    

with st.expander("🔎 Where to search for Research?"):
    st.subheader("Tired of fake news and sensational headlines? Go straight to the source. Here are three excellent **free** places to find research papers:")
    st.markdown("""
1. **[Google Scholar](https://scholar.google.com/)** — The best all-round academic search engine.  
   *Tips:* Use **“Cited by”** to find influential follow-ups, click **“All versions”** for free PDFs, and add filters by year.

2. **[PubMed](https://pubmed.ncbi.nlm.nih.gov/)** — The go-to for medicine, biology, and public health.  
   *Tips:* Turn on the **“Free full text”** filter to surface open-access articles immediately.

3. **[arXiv](https://arxiv.org/)** — Open preprints for physics, computer science, mathematics and more.  
   *Note:* Preprints are often **not yet peer-reviewed**, but they’re fast and freely available.

**Pro tips for better results**
- Add keywords like **review**, **systematic review**, or **meta-analysis** to find high-level summaries.  
- Try advanced search tricks: **"exact phrase"**, **site:edu**, or **filetype:pdf**.  
- If you hit a paywall, look for **“All versions”** on Scholar, check the author’s homepage, or search the **paper title + PDF**.
""")

# Footer

st.subheader("""Thank you for Visiting! Follow Us On Our Platforms:""")

social_media_links = [
    "https://www.instagram.com/ThisIsAnExampleLink",
    "https://www.facebook.com/ThisIsAnExampleLink",
    "https://www.youtube.com/ThisIsAnExampleLink",
    "https://www.github.com/jlnetosci/st-social-media-links",
]

social_media_icons = SocialMediaIcons(social_media_links)
social_media_icons.render(justify_content="start")