# AgenticAI Assist

Autonomous Task Agents for Productivity

**Group:** IT-2305  
**Team members:** Azamat Ubaidullauly, Nikita Verbakhovskiy, Atembek Shaimerden  
**NetIDs:** <AzamatNetID>, <NikitaNetID>, <AtembekNetID>  
**Lecturer:** PhD Assoc. Prof. Nurguzhina Assel  
**Date:** November 11, 2025

**Confidentiality statement:** The information in this document is confidential and provided for course assessment and project development purposes only.

## Abstract

AgenticAI Assist is a web platform that provides autonomous, multi-step task agents tailored to students and young professionals. The system's core differentiator is User-Verified Autonomy: agents propose plans and sources and require explicit user approval before execution, increasing trust and reducing verification overhead.

## Features

- **Organized Task Lifecycle:** Each task is recorded with history, approvals, and outputs for reuse
- **Agent Templates:** Research brief, summarization, study plan
- **User-Verified Autonomy:** Agents propose plans and cite sources; users must Approve & Run or Cancel
- **Integrations:** Google Docs, Telegram bot
- **Template Marketplace:** Shared, verified templates and plans (community-driven)
- **Auditability & Safety:** Logging, approval workflow and policy constraints for sensitive tasks

## Prototype

**Live Demo:** [https://techent.streamlit.app/](https://techent.streamlit.app/)  
**Repository:** [https://github.com/W0nderful11/tech-](https://github.com/W0nderful11/tech-)

## Tech Stack (MVP)

- **Frontend:** Streamlit
- **AI:** Google Gemini API (gemini-2.5-flash model)
- **Backend:** Python
- **Integrations:** Google Docs, Telegram
- **Deployment:** Streamlit Cloud

## Setup & Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/W0nderful11/tech-.git
   cd tech-
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Create `.env` file
   - Add your Google Gemini API key: `GOOGLE_API_KEY=your_api_key_here`

4. Run locally:
   ```bash
   streamlit run agentic_ai_assist.py
   ```

## Files

- `agentic_ai_assist.py`: Main application with task management and AI chat
- `research_agent.py`: Research-focused agent application
- `requirements.txt`: Python dependencies
- `.env`: Environment variables (API keys)

## Business Model

- **Freemium:** Core features free for students (basic summarization, one agent template)
- **Premium:** Monthly/annual subscription for professionals (advanced integrations, priority processing)
- **Enterprise:** University partnerships and group licensing

## Team Responsibilities

- **Azamat Ubaidullauly:** Technical lead, prototype development, backend, integration
- **Nikita Verbakhovskiy:** Product design, UX, customer interviews
- **Atembek Shaimerden:** Business model, market research, slides and documentation

## Next Steps

1. Finalize prototype and deploy pilot with 20–50 university users
2. Collect metrics: activation rate, retention, conversion to paid
3. Iterate UX and connectors based on feedback
4. Prepare seed pitch and 12–18 month hiring plan

## License

This project is developed as part of a course assignment and is confidential.