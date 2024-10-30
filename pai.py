import streamlit as st
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
        },
        {
            "question": "What is the primary purpose of SEO?",
            "options": {
                "A": "To increase website loading speed",
                "B": "To improve search engine rankings",
                "C": "To manage social media posts",
                "D": "To create email campaigns"
            },
            "correct": "B"
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
        },
        {
            "question": "Which metric best indicates content engagement?",
            "options": {
                "A": "Number of views",
                "B": "Time spent on page",
                "C": "Social media shares",
                "D": "Number of backlinks"
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
        },
        {
            "question": "What is the best platform for B2B personal branding?",
            "options": {
                "A": "TikTok",
                "B": "Instagram",
                "C": "LinkedIn",
                "D": "Facebook"
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
    for topic in MARKETING_TOPICS:
        total_questions = len(MARKETING_TOPICS[topic])
        correct = sum(1 for q in range(len(MARKETING_TOPICS[topic]))
                     if st.session_state.answers.get(f"{topic}_{q}") == 
                     MARKETING_TOPICS[topic][q]["correct"])
        scores[topic] = (correct / total_questions) * 100 if total_questions > 0 else 0
    return scores

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

def display_results_chart(scores):
    # Create two columns for the chart
    chart_data = {
        "Topics": list(scores.keys()),
        "Scores": list(scores.values())
    }
    
    # Display bar chart using Streamlit
    st.bar_chart(scores)
    
    # Display numeric scores
    st.subheader("Detailed Scores:")
    for topic, score in scores.items():
        st.write(f"{topic}: {score:.1f}%")

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
        scores = calculate_topic_scores()
        
        # Display results
        st.subheader("Your Performance")
        display_results_chart(scores)
        
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

Each section contains multiple-choice questions to test your understanding.
Your results will show your strengths and areas for improvement.
""")

if __name__ == "__main__":
    main()