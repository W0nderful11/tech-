import os
import uuid
import asyncio
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai

from pydantic import BaseModel

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

# Set up page configuration
st.set_page_config(
    page_title="Agentic AI",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Make sure API key is set
if not os.environ.get("GOOGLE_API_KEY"):
    st.error("Please set your GOOGLE_API_KEY environment variable")
    st.stop()

# App title and description
st.title("📰 Gemini Researcher Agent")
st.subheader("Powered by Google Gemini")
st.markdown("""
This app demonstrates the power of Google Gemini by creating a multi-agent system 
that researches news topics and generates comprehensive research reports.
""")

# Define data models
class ResearchPlan(BaseModel):
    topic: str
    search_queries: list[str]
    focus_areas: list[str]

class ResearchReport(BaseModel):
    title: str
    outline: list[str]
    report: str
    sources: list[str]
    word_count: int

# Custom tool for saving facts found during research
def save_important_fact(fact: str, source: str = None) -> str:
    """Save an important fact discovered during research.
    
    Args:
        fact: The important fact to save
        source: Optional source of the fact
    
    Returns:
        Confirmation message
    """
    if "collected_facts" not in st.session_state:
        st.session_state.collected_facts = []
    
    st.session_state.collected_facts.append({
        "fact": fact,
        "source": source or "Not specified",
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })
    
    return f"Fact saved: {fact}"

# Define the agents as functions
def triage_agent(topic):
    prompt = f"""You are the coordinator of this research operation. Your job is to:
    1. Understand the user's research topic: {topic}
    2. Create a research plan with the following elements:
       - topic: A clear statement of the research topic
       - search_queries: A list of 3-5 specific search queries that will help gather information
       - focus_areas: A list of 3-5 key aspects of the topic to investigate
    3. Return the plan in JSON format with topic, search_queries, and focus_areas.
    """
    response = model.generate_content(prompt)
    # Parse JSON from response
    import json
    try:
        plan = json.loads(response.text)
        return ResearchPlan(**plan)
    except:
        return ResearchPlan(topic=topic, search_queries=[f"Research {topic}"], focus_areas=[f"General info on {topic}"])

def research_agent(query):
    prompt = f"""You are a research assistant. Given a search term: {query}, produce a concise summary of the results. The summary must be 2-3 paragraphs and less than 300 words. Capture the main points. Write succinctly, no need to have complete sentences or good grammar. This will be consumed by someone synthesizing a report, so its vital you capture the essence and ignore any fluff. Do not include any additional commentary other than the summary itself."""
    response = model.generate_content(prompt)
    return response.text

def editor_agent(topic, research_data):
    prompt = f"""You are a senior researcher tasked with writing a cohesive report for a research query: {topic}. 
    You will be provided with initial research: {research_data}.
    You should first come up with an outline for the report that describes the structure and flow of the report. Then, generate the report and return that as your final output.
    The final output should be in markdown format, and it should be lengthy and detailed. Aim for 5-10 pages of content, at least 1000 words.
    Return in JSON format with title, outline (list), report, sources (list), word_count.
    """
    response = model.generate_content(prompt)
    import json
    try:
        report = json.loads(response.text)
        return ResearchReport(**report)
    except:
        return ResearchReport(title=topic, outline=["Introduction", "Body", "Conclusion"], report=research_data, sources=[], word_count=len(research_data.split()))

# Create sidebar for input and controls
with st.sidebar:
    st.header("Research Topic")
    user_topic = st.text_input(
        "Enter a topic to research:",
    )
    
    start_button = st.button("Start Research", type="primary", disabled=not user_topic)
    
    st.divider()
    st.subheader("Example Topics")
    example_topics = [
        "What are the best cruise lines in USA for first-time travelers who have never been on a cruise?",
        "What are the best affordable espresso machines for someone upgrading from a French press?",
        "What are the best off-the-beaten-path destinations in India for a first-time solo traveler?"
    ]
    
    for topic in example_topics:
        if st.button(topic):
            user_topic = topic
            start_button = True

# Main content area with two tabs
tab1, tab2 = st.tabs(["Research Process", "Report"])

# Initialize session state for storing results
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = str(uuid.uuid4().hex[:16])
if "collected_facts" not in st.session_state:
    st.session_state.collected_facts = []
if "research_done" not in st.session_state:
    st.session_state.research_done = False
if "report_result" not in st.session_state:
    st.session_state.report_result = None

# Main research function
def run_research(topic):
    # Reset state for new research
    st.session_state.collected_facts = []
    st.session_state.research_done = False
    st.session_state.report_result = None
    
    with tab1:
        message_container = st.container()
        
    # Create error handling container
    error_container = st.empty()
        
    # Start with the triage agent
    with message_container:
        st.write("🔍 **Triage Agent**: Planning research approach...")
    
    triage_result = triage_agent(topic)
    
    # Check if the result is a ResearchPlan object
    if hasattr(triage_result, 'topic'):
        research_plan = triage_result
        plan_display = {
            "topic": research_plan.topic,
            "search_queries": research_plan.search_queries,
            "focus_areas": research_plan.focus_areas
        }
    else:
        # Fallback
        research_plan = {
            "topic": topic,
            "search_queries": ["Researching " + topic],
            "focus_areas": ["General information about " + topic]
        }
        plan_display = research_plan
    
    with message_container:
        st.write("📋 **Research Plan**:")
        st.json(plan_display)
    
    # Simulate research by calling research_agent for each query
    research_summaries = []
    for query in research_plan.search_queries:
        summary = research_agent(query)
        research_summaries.append(summary)
        # Save some facts
        save_important_fact(summary[:100], "Gemini Research")
    
    # Display facts
    with message_container:
        st.write("📚 **Collected Facts**:")
        for fact in st.session_state.collected_facts:
            st.info(f"**Fact**: {fact['fact']}\n\n**Source**: {fact['source']}")
    
    # Editor Agent phase
    with message_container:
        st.write("📝 **Editor Agent**: Creating comprehensive research report...")
    
    try:
        research_data = "\n".join(research_summaries)
        report_result = editor_agent(topic, research_data)
        
        st.session_state.report_result = report_result
        
        with message_container:
            st.write("✅ **Research Complete! Report Generated.**")
            
            # Preview a snippet of the report
            if hasattr(report_result, 'report'):
                report_preview = report_result.report[:300] + "..."
            else:
                report_preview = str(report_result)[:300] + "..."
                
            st.write("📄 **Report Preview**:")
            st.markdown(report_preview)
            st.write("*See the Report tab for the full document.*")
            
    except Exception as e:
        st.error(f"Error generating report: {str(e)}")
        st.session_state.report_result = f"# Research on {topic}\n\n{research_data}"
    
    st.session_state.research_done = True

# Run the research when the button is clicked
if start_button:
    with st.spinner(f"Researching: {user_topic}"):
        try:
            run_research(user_topic)
        except Exception as e:
            st.error(f"An error occurred during research: {str(e)}")
            # Set a basic report result so the user gets something
            st.session_state.report_result = f"# Research on {user_topic}\n\nUnfortunately, an error occurred during the research process. Please try again later or with a different topic.\n\nError details: {str(e)}"
            st.session_state.research_done = True

# Display results in the Report tab
with tab2:
    if st.session_state.research_done and st.session_state.report_result:
        report = st.session_state.report_result
        
        # Handle different possible types of report results
        if hasattr(report, 'title'):
            # We have a properly structured ResearchReport object
            title = report.title
            
            # Display outline if available
            if hasattr(report, 'outline') and report.outline:
                with st.expander("Report Outline", expanded=True):
                    for i, section in enumerate(report.outline):
                        st.markdown(f"{i+1}. {section}")
            
            # Display word count if available
            if hasattr(report, 'word_count'):
                st.info(f"Word Count: {report.word_count}")
            
            # Display the full report in markdown
            if hasattr(report, 'report'):
                report_content = report.report
                st.markdown(report_content)
            else:
                report_content = str(report)
                st.markdown(report_content)
            
            # Display sources if available
            if hasattr(report, 'sources') and report.sources:
                with st.expander("Sources"):
                    for i, source in enumerate(report.sources):
                        st.markdown(f"{i+1}. {source}")
            
            # Add download button for the report
            st.download_button(
                label="Download Report",
                data=report_content,
                file_name=f"Report1.md",
                mime="text/markdown"
            )
        else:
            # Handle string or other type of response
            report_content = str(report)
            title = user_topic.title()
            
            st.title(f"{title}")
            st.markdown(report_content)
            
            # Add download button for the report
            st.download_button(
                label="Download Report",
                data=report_content,
                file_name=f"Report2.md",
                mime="text/markdown"
            )