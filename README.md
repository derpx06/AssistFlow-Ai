# Assistflow
An integrated support platform that combines AI chat, human support, ticketing, and a website-aware knowledge base.

## What This Is
Ticket Classifier is a full-stack helpdesk system with:
- An embeddable chat widget for AI + human support
- A ticketing and agent dashboard
- Website-specific knowledge base crawling and indexing
- Vector search to ground answers in your content




## Screenshots
| Dashboard | Tickets |
| --- | --- |
| <img width="800" alt="dashboard" src="https://github.com/user-attachments/assets/6dc0c52d-a7f4-4102-95b9-553e390ba8d9" /> | <img width="800" alt="tickets" src="https://github.com/user-attachments/assets/185014f8-3d83-4872-960f-407276e683fa" /> |
| Knowledge Base | Chat Widget |
| --- | --- |
| <img width="800" alt="knowledge-base" src="https://github.com/user-attachments/assets/8eb25a42-4f68-4c1e-a998-dbf6f28a2b8f" /> | <img width="800" alt="chat-widget" src="https://github.com/user-attachments/assets/8a66f3aa-04ca-4192-99c1-8ef9873d9644" /> |
| Demo Site | Analytics |
| --- | --- |
| <img width="800" alt="demo-site" src="https://github.com/user-attachments/assets/dd333895-bd8a-4e4d-bf3c-e1a3f1e0befe" /> | <img width="800" alt="analytics" src="https://github.com/user-attachments/assets/058df3b6-29bb-4a21-9a3c-88e5e203a934" /> |

## Repository Map
- `backend/` API, crawling, and vector indexing
- `frontend/` agent dashboard (React)
- `dashboard-demo/` demo site that embeds the widget
- `chatbot-package/` embeddable widget package (builds to `dist/`)

## Requirements
- Node.js + npm
- MongoDB (for tickets, users, and config)

## Quick Start
1. **Backend**
   - `cd backend`
   - `npm install`
   - `cp .env.example .env`
   - Set `MONGODB_URI` in `.env` (required)
   - `npm run db:setup`
   - `npm run dev`

2. **Frontend**
   - `cd frontend`
   - `npm install`
   - `npm run dev`

3. **Widget package**
   - `cd chatbot-package`
   - `npm install`
   - `npm run build`

Backend API base URL (default): `http://127.0.0.1:5000/api`

## Core Concepts
**Knowledge Base (per website)**
- Each website has its own vector collection and stats.
- Crawls add pages to the same website knowledge base (they do not replace it).

**API Key vs Widget Key**
- **API Key** is used for AI chat and selects which website knowledge base to query.
- **Widget Key** is used for human support sessions.
- The widget package can auto-fetch a widget key from the backend using your API key.

## Demo Setup
In the `dashboard-demo/` UI:
- Use **API Base URL** (example: `http://127.0.0.1:5001/api`)
- Paste the **API key** from **Knowledge Base → Deployment**

## References In AI Answers
AI replies append a **References** section when sources are returned from the backend.

