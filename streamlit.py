import streamlit as st
from simplify import simplify_text, simplify_from_urls, validate_length
from explain_terms import explain_terms
from question_gen import question_gen, question_answers
from example_text import example_text
from urlextract import URLExtract
import fitz  


st.set_page_config(layout="centered")

st.title(""" Reading Companion """)

st.write(""" Journals and research articles are brilliant tools for learning and staying informed, but they’re often written in academic language that’s hard to digest. The Reading Companion helps you break through the jargon.
With this tool you can provide any article or journal extract, and it will:

• Simplify the text into easy-to-read language
         
• Explain key words and terminology
         
• Ask follow-up questions to check your understanding

Whether you're a student, curious learner, or just tired of misinformation, the Reading Companion helps you understand research!
""")

st.image("new_cover_image.png")

def display_tools(user_input, section): 
    
    left, middle, right = st.columns(3)
   
    if left.button("Reading Companion", icon="📘", use_container_width=True, key=(section + "1")):
        with st.spinner("Simplifying..."):
            # user_input = validate_length(user_input, 5000)
            # if len(urls) >=1: 
            #     simplified = simplify_from_urls(urls)  
            # else: 
            simplified = simplify_text(user_input)

            st.markdown(f"**Simplified:** {simplified}") 

    if middle.button("Key defintions", icon="🔍", use_container_width=True, key=(section + "2")):
        with st.spinner("Dictionary..."):
            dictionary = explain_terms(example_text)
            st.markdown(f"**Key terms and Defintions:** \n {dictionary}")

    if right.button("Generate Questions", icon="📝", use_container_width=True, key=(section + "3")):
       with st.spinner("Generating Questions..."):
            questions_output = question_gen(example_text)
            st.markdown(f"**Questions to check your understanding:** \n {questions_output}") 
        
       with st.expander("💡 See Answers"):  
            question_answers_output = question_answers(questions_output)
            st.markdown(f"**Answers:** \n {question_answers_output}")



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
    user_input = st.text_area("Paste your paragraph below or provide the web link:")
    
    # Checking if the user input has any urls
    extractor = URLExtract()
    urls = extractor.find_urls(user_input)
    print(urls)
    
    # Allowing for a file to be uploaded instead 
    st.write("or")
    uploaded_file = st.file_uploader("Choose a file")
    
    if uploaded_file is not None:

        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            user_input = ""
            for page in doc:
                user_input += page.get_text()

        
    st.write("")

    display_tools(user_input, "use_now")
     

with st.expander("See our Monthly Top Picks"):
    st.subheader("3 Research papers made simple, for real news: ")
    st.write("""Every month, we handpick 3 research papers we find fascinating covering areas like health, science, psychology, economics, and technology.

We encourage you to start by giving the original paper a go! Then dive into the Reading Companion summary for a simplified version, key definitions, and follow-up questions to test your understanding.

We often end up reading more 'fake news' in our curated feeds than real research-backed insights, perhaps because research papers feel inaccessible or overwhelming. Our aim is to change that by spotlighting great reads each month.

🗓️ New articles drop on the 1st of every month.
             
📚 Whether you're unsure where to begin or not used to reading journals, we've got you covered.""")