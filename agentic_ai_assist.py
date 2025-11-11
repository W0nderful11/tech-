import os
import uuid
import streamlit as st
from datetime import datetime
import google.generativeai as genai

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY", "AIzaSyD6PyP36fsGs3CY1zBt0q-0u99PNCKz164"))
model = genai.GenerativeModel('gemini-2.5-flash')

# App title and description
st.set_page_config(
    page_title="AgenticAI Assist",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🤖 AgenticAI Assist")
st.subheader("Autonomous Task Agents for Productivity")
st.markdown("""
AgenticAI Assist is a web platform that provides autonomous, multi-step task agents tailored to students and young professionals. 
The system's core differentiator is User-Verified Autonomy: agents propose plans and sources and require explicit user approval before execution.
""")

# Initialize session state
if "tasks" not in st.session_state:
    st.session_state.tasks = []
if "current_task" not in st.session_state:
    st.session_state.current_task = None

# Agent templates
agent_templates = {
    "Research Brief": "Create a research brief on the given topic with key points, sources, and summary.",
    "Summarization": "Summarize the provided text or topic into key points and main ideas.",
    "Study Plan": "Create a study plan for the given subject with timeline, resources, and milestones."
}

# Sidebar for task management
with st.sidebar:
    st.header("Task Management")
    
    # Create new task
    with st.expander("Create New Task", expanded=True):
        task_name = st.text_input("Task Name")
        task_description = st.text_area("Task Description")
        selected_template = st.selectbox("Agent Template", list(agent_templates.keys()))
        
        if st.button("Create Task"):
            if task_name and task_description:
                task_id = str(uuid.uuid4())[:8]
                new_task = {
                    "id": task_id,
                    "name": task_name,
                    "description": task_description,
                    "template": selected_template,
                    "status": "Created",
                    "created_at": datetime.now(),
                    "approved": False,
                    "plan": None,
                    "result": None
                }
                st.session_state.tasks.append(new_task)
                st.success(f"Task '{task_name}' created!")
            else:
                st.error("Please fill in task name and description.")

    # Task list
    st.subheader("Active Tasks")
    for task in st.session_state.tasks:
        if st.button(f"{task['name']} ({task['status']})", key=task['id']):
            st.session_state.current_task = task

# Main content
tab1, tab2 = st.tabs(["Task Management", "Direct AI Chat"])

with tab1:
    if st.session_state.current_task:
        task = st.session_state.current_task
        
        st.header(f"Task: {task['name']}")
        st.write(f"**Description:** {task['description']}")
        st.write(f"**Template:** {task['template']}")
        st.write(f"**Status:** {task['status']}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Generate Plan", disabled=task['status'] != 'Created'):
                with st.spinner("Generating plan..."):
                    prompt = f"""
                    You are a triage agent for {task['template']} tasks.
                    Task: {task['description']}
                    
                    Create a detailed execution plan with specific steps, relevant sources, and expected outcomes.
                    For {task['template']} tasks, focus on:
                    - Research Brief: Key research areas, data sources, analysis methods
                    - Summarization: Analysis approach, key extraction, summary structure
                    - Study Plan: Learning objectives, timeline, resources, assessment
                    
                    Respond ONLY with a valid JSON object in this exact format:
                    {{
                        "plan": "Detailed description of the execution strategy and approach",
                        "sources": ["Source 1: brief description", "Source 2: brief description"],
                        "steps": ["Step 1: detailed action", "Step 2: detailed action", "Step 3: detailed action"]
                    }}
                    
                    Make steps actionable and specific. Sources should be relevant to the task.
                    """
                    try:
                        response = model.generate_content(prompt)
                        # Parse JSON from response
                        import json
                        try:
                            plan = json.loads(response.text)
                            task['plan'] = plan
                            task['status'] = 'Plan Generated'
                            st.success("Plan generated!")
                            st.rerun()
                        except json.JSONDecodeError:
                            task['plan'] = {
                                "plan": f"Execute {task['template']} for: {task['description'][:100]}...",
                                "sources": [
                                    f"Primary source: {task['description'][:200]}...",
                                    "General knowledge base for AI and autonomous agents",
                                    "Academic papers on multi-agent systems"
                                ],
                                "steps": [
                                    "Step 1: Analyze the input content and identify key themes",
                                    "Step 2: Extract relevant information and structure findings",
                                    "Step 3: Generate comprehensive output based on template requirements",
                                    "Step 4: Review and validate results for accuracy"
                                ]
                            }
                            task['status'] = 'Plan Generated'
                            st.success("Plan generated with default structure!")
                            st.rerun()
                        except Exception as e:
                            if "429" in str(e) or "quota" in str(e).lower():
                                st.error("API quota exceeded. Please check your Google AI billing.")
                            else:
                                st.error(f"Error generating plan: {e}")
                    except Exception as e:
                        st.error(f"Error generating plan: {e}")
        
        with col2:
            if task['status'] == 'Plan Generated' and not task['approved']:
                if st.button("Approve & Run"):
                    task['approved'] = True
                    task['status'] = 'Approved'
                    st.success("Task approved! Running...")
                    st.rerun()
        
        with col3:
            if task['approved'] and task['status'] == 'Approved':
                if st.button("Execute Task"):
                    with st.spinner("Executing task..."):
                        prompt = f"""
                        You are an AI agent for {task['template']}.
                        Task: {task['description']}
                        Plan: {task['plan']}
                        
                        Execute the task and provide the final result.
                        Respond ONLY with a valid JSON object in this exact format:
                        {{
                            "title": "Report Title",
                            "outline": ["section1", "section2"],
                            "report": "full detailed report in markdown",
                            "sources": ["source1", "source2"],
                            "word_count": 1234
                        }}
                        """
                        try:
                            response = model.generate_content(prompt)
                            task['result'] = response.text
                            task['status'] = 'Completed'
                            st.success("Task completed!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error executing task: {e}")
        
        # Display plan
        if task['plan']:
            st.subheader("Generated Plan")
            st.json(task['plan'])
        
        # Display result
        if task['result']:
            st.subheader("Task Result")
            st.markdown(task['result'])
            
        # Back button
        if st.button("Back to Tasks"):
            st.session_state.current_task = None
            st.rerun()

    else:
        st.header("Welcome to AgenticAI Assist")
        st.write("Select a task from the sidebar or create a new one.")
        
        # Display all tasks
        if st.session_state.tasks:
            st.subheader("All Tasks")
            for task in st.session_state.tasks:
                st.write(f"- **{task['name']}**: {task['status']} (Created: {task['created_at'].strftime('%Y-%m-%d %H:%M')})")

with tab2:
    st.header("Direct AI Chat with Gemini")
    st.write("Ask Gemini directly for any questions or tasks.")
    
    # Test API button
    if st.button("Test Gemini API"):
        with st.spinner("Testing API..."):
            try:
                test_response = model.generate_content("Hello, Gemini! Respond with 'API is working'.")
                st.success(f"API Test Successful: {test_response.text.strip()}")
            except Exception as e:
                st.error(f"API Test Failed: {e}")
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask Gemini..."):
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Generate response
        with st.spinner("Gemini is thinking..."):
            try:
                response = model.generate_content(prompt)
                ai_response = response.text
            except Exception as e:
                if "429" in str(e) or "quota" in str(e).lower():
                    ai_response = "Error: API quota exceeded. Please check your Google AI billing or wait for reset."
                else:
                    ai_response = f"Error: {e}"
        
        # Add AI response
        st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
        
        # Rerun to update chat
        st.rerun()