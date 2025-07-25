import streamlit as st
from simplify import simplify_text
from explain_terms import explain_terms
from question_gen import question_gen, question_answers


st.set_page_config(layout="centered")


st.title(""" Reading Companion """)

st.write(""" Journals and research articles are brilliant tools for learning and staying informed, but they’re often written in dense, academic language that’s hard to digest. The Reading Companion helps you break through the jargon.
With this tool, you can provide any article or journal extract, and it will:

• Simplify the text into easy-to-read language

• Explain key words and terminology

• Ask follow-up questions to check your understanding

Whether you're a student, curious learner, or just tired of misinformation, the Reading Companion helps you unlock research without the overwhelm!
""")

st.image("cover_image2.png")

with st.expander("💡 See Example"):
    st.subheader("Example")
    st.write("Try to read and understand this scientific paper:")
    st.write("...")
    st.subheader("Example: Climate Change")
    example_text = """Anthropogenic greenhouse gas emissions have led to a radiative forcing imbalance in the Earth’s climate system, resulting in global warming and associated climatic changes."""
    
    if st.button("Reading Companion Test"):
        with st.spinner("Simplifying..."):
            simplified = simplify_text(example_text)
            st.markdown(f"**Original:** {example_text}")
            st.markdown(f"**Simplified:** {simplified}")

    if st.button("Key defintions"):
        with st.spinner("Dictionary..."):
            dictionary = explain_terms(example_text)
            st.markdown(f"**Original:** {example_text}")
            st.markdown(f"**Key terms and Defintions:** \n {dictionary}")

    if st.button("Test Myself"):
        with st.spinner("Generating Questions..."):
            questions_output = question_gen(example_text)
            st.markdown(f"**Original:** {example_text}")
            st.markdown(f"**Questions to check your understanding:** \n {questions_output}") 
        
        print(question_gen)

        with st.expander("💡 See Answers"):  
            question_answers_output = question_answers(questions_output)
            print(question_answers_output)
            st.markdown(f"**Answers:** \n {question_answers_output}")


with st.expander("🛠️ Use Now"):
    st.subheader("Try It Yourself")
    user_input = st.text_area("Paste your article or paragraph below:")
    if st.button("Reading Companion"):
        st.write("🔄 Running AI model... (Coming soon!)")
