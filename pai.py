import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from dotenv import load_dotenv
import os
import google.generativeai as genai
from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI

# Load environment variables
load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')

# Page config
st.set_page_config(page_title="Marketing Knowledge Assessment", page_icon="📊", layout="wide")

# Custom CSS
st.markdown("""
<style>
.stTextInput > div > div > input {
    font-size: 16px;
}
.stButton > button {
    width: 100%;
}
.question-card {
    padding: 1.5rem;
    border-radius: 0.5rem;
    background-color: #f8f9fa;
    margin-bottom: 1rem;
    border: 1px solid #dee2e6;
}
.results-card {
    padding: 2rem;
    border-radius: 0.5rem;
    background-color: #ffffff;
    margin-bottom: 1rem;
    border: 1px solid #e9ecef;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

# Define the marketing topics and questions
MARKETING_TOPICS = {
    "Digital Marketing Fundamentals": [
        {
            "question": "Which digital marketing channel typically has the highest ROI?",
            "options": {
                "A": "Email Marketing",
                "B": "Social Media Marketing",
                "C": "Display Advertising",
                "D": "Print Media"
            },
            "correct": "A"
        }
    ],
    "Content Strategy": [
        {
            "question": "What is the most important factor in creating a successful content strategy?",
            "options": {
                "A": "Posting frequently",
                "B": "Understanding your audience",
                "C": "Using trending hashtags",
                "D": "Having a large budget"
            },
            "correct": "B"
        }
    ],
    "Personal Branding": [
        {
            "question": "Which element is most crucial for personal branding?",
            "options": {
                "A": "Having a large following",
                "B": "Posting daily content",
                "C": "Consistency in messaging and values",
                "D": "Using professional photos"
            },
            "correct": "C"
        }
    ]
}

# Initialize session state
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
    st.session_state.correct_answers = 0
    st.session_state.answers = {}
    st.session_state.topic_scores = {topic: 0 for topic in MARKETING_TOPICS.keys()}
    st.session_state.test_complete = False

def calculate_topic_scores():
    scores = {}
    max_scores = {}
    for topic in MARKETING_TOPICS:
        total_questions = len(MARKETING_TOPICS[topic])
        correct = sum(1 for q in range(len(MARKETING_TOPICS[topic]))
                     if st.session_state.answers.get(f"{topic}_{q}") == 
                     MARKETING_TOPICS[topic][q]["correct"])
        scores[topic] = (correct / total_questions) * 100 if total_questions > 0 else 0
        max_scores[topic] = 100
    return scores, max_scores

def generate_recommendations(scores):
    recommendations = []
    for topic, score in scores.items():
        if score < 60:
            recommendations.append(f"📚 Focus on improving your knowledge of {topic}")
        elif score < 80:
            recommendations.append(f"📈 Consider advanced learning in {topic}")
        else:
            recommendations.append(f"🌟 Excellent understanding of {topic}!")
    return recommendations

def main():
    st.title('📊 Marketing Knowledge Assessment')
    
    if not st.session_state.test_complete:
        # Calculate total questions
        total_questions = sum(len(questions) for questions in MARKETING_TOPICS.values())
        current_topic = None
        current_question_index = 0
        
        # Find current topic and question
        questions_seen = 0
        for topic, questions in MARKETING_TOPICS.items():
            if questions_seen + len(questions) > st.session_state.current_question:
                current_topic = topic
                current_question_index = st.session_state.current_question - questions_seen
                break
            questions_seen += len(questions)
        
        if current_topic:
            st.subheader(f"Question {st.session_state.current_question + 1} of {total_questions}")
            st.markdown(f"**Topic: {current_topic}**")
            
            question_data = MARKETING_TOPICS[current_topic][current_question_index]
            with st.container():
                st.markdown(f"**{question_data['question']}**")
                answer = st.radio("Select your answer:", 
                                options=list(question_data['options'].keys()),
                                format_func=lambda x: f"{x}: {question_data['options'][x]}")
                
                if st.button("Submit Answer"):
                    question_key = f"{current_topic}_{current_question_index}"
                    st.session_state.answers[question_key] = answer
                    
                    if answer == question_data['correct']:
                        st.session_state.correct_answers += 1
                        st.session_state.topic_scores[current_topic] += 1
                    
                    st.session_state.current_question += 1
                    
                    if st.session_state.current_question >= total_questions:
                        st.session_state.test_complete = True
                    st.experimental_rerun()
    
    else:
        st.success("Assessment Complete! 🎉")
        
        # Calculate and display scores
        scores, max_scores = calculate_topic_scores()
        
        # Create score visualization
        fig = go.Figure(data=[
            go.Bar(name='Your Score', x=list(scores.keys()), y=list(scores.values())),
            go.Bar(name='Maximum Score', x=list(max_scores.keys()), y=list(max_scores.values()))
        ])
        
        fig.update_layout(
            title='Your Performance by Topic',
            barmode='group',
            yaxis_title='Score (%)',
            xaxis_title='Topics',
            showlegend=True
        )
        
        st.plotly_chart(fig)
        
        # Display recommendations
        st.subheader("Recommendations")
        recommendations = generate_recommendations(scores)
        for rec in recommendations:
            st.markdown(f"- {rec}")
        
        if st.button("Start New Assessment"):
            st.session_state.current_question = 0
            st.session_state.correct_answers = 0
            st.session_state.answers = {}
            st.session_state.topic_scores = {topic: 0 for topic in MARKETING_TOPICS.keys()}
            st.session_state.test_complete = False
            st.experimental_rerun()

# Sidebar
st.sidebar.title("About the Assessment")
st.sidebar.markdown("""
This assessment evaluates your marketing knowledge across multiple domains:
- Digital Marketing Fundamentals
- Content Strategy
- Personal Branding
- Social Media Marketing
- SEO and Analytics
""")

if __name__ == "__main__":
    main()