import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI

# Load environment variables from .env file
load_dotenv()

# Get the API key from the environment
api_key = os.getenv('GOOGLE_API_KEY')

# Set page config
st.set_page_config(page_title="Problem-Solving Aptitude Test", page_icon="🧠", layout="wide")

# Custom CSS to improve the UI
st.markdown("""
<style>
.stTextInput > div > div > input {
    font-size: 16px;
}
.stButton > button {
    width: 100%;
}
.chat-message {
    padding: 1rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
    display: flex;
    align-items: flex-start;
}
.chat-message.user {
    background-color: #e6f3ff;
}
.chat-message.assistant {
    background-color: #f0f0f0;
}
.chat-message .avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    object-fit: cover;
    margin-right: 1rem;
}
.chat-message .message {
    flex-grow: 1;
}
</style>
""", unsafe_allow_html=True)

# Define the system prompt
system_prompt = """
You are an adaptive problem-solving aptitude test assistant designed to assess a user's approach to solving problems in four domains: coding, finance, design, and marketing. Your role is to generate a series of 10 questions that evaluate the user's problem-solving style.

Follow these guidelines:
1. The first question should be open-ended, asking about the user's general approach to problem-solving.
2. Generate 9 multiple-choice questions about different problem scenarios. Each option should represent an approach from one of the four domains (coding, finance, design, marketing).
3. Ensure that the questions are engaging and thought-provoking, helping the user reflect on their problem-solving preferences.
4. After the 10th question, provide a summary of the user's problem-solving style, including a star-based domain recommendation (e.g., ⭐⭐⭐⭐⭐ for the most suitable domain) and a behavioral analysis.

For each interaction, provide:
1. The current question number (1-10)
2. The question text
3. For questions 2-10, provide 4 multiple-choice options labeled A, B, C, and D, each representing a domain-specific approach

Current question: {current_question}
Previous questions and responses:
{previous_qa}

Generate the next question or the final summary:
"""

# Initialize the model and prompt template
llm = GoogleGenerativeAI(model="gemini-pro", google_api_key=api_key)
prompt_template = PromptTemplate.from_template(system_prompt)

# Streamlit app layout
st.title('🧠 Problem-Solving Aptitude Test')

# Initialize session state
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
    st.session_state.previous_qa = []
    st.session_state.test_complete = False
    st.session_state.final_summary = ""

# Function to generate the next question or summary
def generate_next_question():
    chain = prompt_template | llm
    response = chain.invoke({
        "current_question": st.session_state.current_question,
        "previous_qa": "\n".join([f"Q{i+1}: {qa['question']}\nA{i+1}: {qa['answer']}" for i, qa in enumerate(st.session_state.previous_qa)])
    })
    return response

# Function to parse multiple-choice options
def parse_mcq_options(question_text):
    lines = question_text.split('\n')
    question = lines[0]
    options = {line[0]: line[2:] for line in lines[1:] if line.startswith(('A', 'B', 'C', 'D'))}
    return question, options

# Main app logic
if not st.session_state.test_complete:
    if st.session_state.current_question < 10:
        if len(st.session_state.previous_qa) < st.session_state.current_question + 1:
            question = generate_next_question()
            st.session_state.previous_qa.append({"question": question, "answer": ""})
        
        st.subheader(f"Question {st.session_state.current_question + 1} of 10")
        
        if st.session_state.current_question == 0:
            st.markdown(st.session_state.previous_qa[st.session_state.current_question]["question"])
            user_response = st.text_area("Your answer:", key=f"question_{st.session_state.current_question}")
        else:
            question, options = parse_mcq_options(st.session_state.previous_qa[st.session_state.current_question]["question"])
            st.markdown(question)
            user_response = st.radio("Choose your answer:", options.keys(), format_func=lambda x: f"{x}: {options[x]}")
        
        if st.button("Submit"):
            st.session_state.previous_qa[st.session_state.current_question]["answer"] = user_response
            st.session_state.current_question += 1
            if st.session_state.current_question == 10:
                st.session_state.final_summary = generate_next_question()
                st.session_state.test_complete = True
            st.experimental_rerun()
    
    else:
        st.session_state.test_complete = True
        st.experimental_rerun()

else:
    st.success("Test complete! Here's your problem-solving style summary:")
    st.markdown(st.session_state.final_summary)
    
    if st.button("Start New Test"):
        st.session_state.current_question = 0
        st.session_state.previous_qa = []
        st.session_state.test_complete = False
        st.session_state.final_summary = ""
        st.experimental_rerun()

# Add a sidebar with some information
st.sidebar.title("About the Problem-Solving Aptitude Test")
st.sidebar.info(
    """Welcome to the Problem-Solving Aptitude Test!

This test is designed to assess your problem-solving approach in four key domains:
1. Coding
2. Finance
3. Design
4. Marketing

The test consists of 10 questions:
- 1 open-ended question about your general problem-solving approach
- 9 multiple-choice questions presenting different problem scenarios

Answer thoughtfully, and at the end, you'll receive:
- A star-based domain recommendation
- A behavioral analysis of your problem-solving style

Good luck!"""
)

# Add a disclaimer at the bottom of the sidebar
st.sidebar.markdown("---")
st.sidebar.caption(
    "Disclaimer: This aptitude test is for informational purposes only and should not be considered as professional career advice. "
    "Always consult with career counselors or industry professionals for personalized guidance."
)