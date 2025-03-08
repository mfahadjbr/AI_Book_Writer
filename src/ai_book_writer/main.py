import logging
import streamlit as st
from agents import BookWriterAgents
from tasks import BookWriterTasks
from crewai import Crew, LLM
from dotenv import load_dotenv
import os
from litellm.exceptions import BadRequestError

# Load environment variables
load_dotenv()
api_keys = os.getenv("GEMINI_API_KEY")

# Initialize model
model = LLM(model="gemini/gemini-2.0-flash-exp", api_key=api_keys)

# Streamlit UI
st.set_page_config(page_title="AI Book Writer", page_icon="📖", layout="centered")
st.title("📖 AI Book Writer")
st.markdown("Generate book content with AI-powered agents.")

# Form for user input
with st.form("book_form"):
    st.subheader("Book Details")
    
    col1, col2 = st.columns(2)
    with col1:
        word_count = st.text_input("Word Count", placeholder="Enter the total word count")
        Book_Title = st.text_input("Book Title", placeholder="Enter the book title")
        Author_Name = st.text_input("Author Name", placeholder="Enter author's name")
    with col2:
        Target_Audience = st.text_input("Target Audience", placeholder="Who is this book for?")
        Writing_Style = st.selectbox(
            "Writing Style",
            ["Formal", "Casual", "Technical", "Creative", "Persuasive"],
            index=0
        )
    
    submit = st.form_submit_button("Generate Book")

# Agents and Tasks
agents = BookWriterAgents()
tasks = BookWriterTasks()

Content_Strategist = agents.Content_Strategist()
Writer = agents.Writer()

Content_Strategist_Task = tasks.Content_Strategist_Task(
    agent=Content_Strategist,
    word_count=word_count,
    Book_Title=Book_Title,
    Author_Name=Author_Name,
    Target_Audience=Target_Audience,
    Writing_Style=Writing_Style
)

def save_to_markdown(text, filename="output.md"):
    with open(filename, "w", encoding="utf-8") as file:
        file.write(text)
    st.success(f"✅ Markdown file saved as {filename}")

def download_button(filename):
    with open(filename, "rb") as file:
        st.download_button(
            label="📥 Download Output",
            data=file,
            file_name=filename,
            mime="text/markdown"
        )

def format_output(text):
    formatted_text = f"# {Book_Title}\n\n**Author:** {Author_Name}\n\n**Target Audience:** {Target_Audience}\n\n**Writing Style:** {Writing_Style}\n\n{text}"
    return formatted_text

Writer_Task = tasks.Writer_Task(
    agent=Writer,
    context=[Content_Strategist_Task],
    callback=lambda text: save_to_markdown(format_output(text))
)

crew = Crew(
    agents=[Content_Strategist, Writer],
    tasks=[Content_Strategist_Task, Writer_Task],
    verbose=True,
)

# Process when button is clicked
if submit:
    with st.spinner("Processing... Please wait..."):
        try:
            results = crew.kickoff()
            formatted_results = format_output(results)
            st.text_area("Generated Content", formatted_results, height=700)
            save_to_markdown(formatted_results)
            download_button("output.md")
        except BadRequestError as e:
            st.error("An error occurred while processing your request. Please check your inputs and try again.")
            logging.error(f"BadRequestError: {e}", exc_info=True)
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
            logging.error(f"Error: {e}", exc_info=True)


