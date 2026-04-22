# Upwork Proposal Agent

This is an automated agent built to monitor Upwork job feeds, evaluate if the jobs are a good match for a starting freelancer (few proposals, small scope, reliable client), and prepare professional proposals using Gemini. 

It then notifies the freelancer via WhatsApp (Twilio) and awaits a decision (YES / NO / AMEND). Once approved, it uses Playwright to automatically apply on Upwork.

## Architecture

1. **Collector (`app/modules/collector.py`)**: Polls Upwork via the REST/GraphQL Job Search API.
2. **Brain (`app/modules/brain.py`)**: Uses Google Gemini to score the job, check criteria (low competition, good client history), and draft a proposal.
3. **Notifier (`app/modules/notifier.py`)**: Sends a WhatsApp message via Twilio.
4. **FastAPI Webhook (`app/main.py`)**: Receives the WhatsApp reply from the user.
5. **Executor (`app/modules/executor.py`)**: Submits the proposal using an automated Playwright browser session.

## Setup Instructions

### 1. Environment Variables

Create a `.env` file in the root directory (matching `app/core/config.py`):
```env
# Upwork
UPWORK_CLIENT_ID=your_upwork_client_id
UPWORK_CLIENT_SECRET=your_upwork_client_secret
UPWORK_REDIRECT_URI=http://localhost:8080

# AI
GOOGLE_API_KEY=your_gemini_api_key

# Twilio (WhatsApp)
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_NUMBER=your_twilio_whatsapp_number (e.g., +14155238886)
MY_WHATSAPP_NUMBER=your_personal_whatsapp_number (e.g., +1234567890)

# Local State
REDIS_URL=redis://localhost:6379/0
```

### 2. Upwork Authentication
Run the auth setup script:
```bash
python scripts/setup_auth.py
```
This generates `tokens.json` to be used for the Upwork API.

### 3. Playwright Setup (Executor)
Since Upwork API does not natively allow submitting proposals for regular freelancers, we use Playwright.
```bash
uv run playwright install chromium
```
You need to authenticate manually once and save your session state into `upwork_state.json`. You can create a small script to launch Playwright, log in manually to Upwork, and save the context state.

### 4. Running the Application

Start Redis (required for state management):
```bash
redis-server
```

Start the Webhook Server (receives WhatsApp replies):
```bash
uvicorn app.main:app --reload --port 8000
```
*(You will need ngrok or similar to expose port 8000 to the public internet so Twilio can reach your webhook).*

Start the Job Poller (in a separate terminal):
```bash
python scripts/poll_jobs.py
```

## How it works

1. `poll_jobs.py` fetches the latest jobs matching your criteria (e.g., "python").
2. `brain.py` evaluates it. If the score >= 70, it sends a WhatsApp message.
3. You receive a message:
   ```
   🚀 New Upwork Job Match!
   Title: Build a simple Python script
   Score: 85/100
   ...
   Draft Proposal: ...
   Reply YES 12345 to apply, or AMEND 12345 [text]
   ```
4. If you reply `YES 12345`, Twilio hits your FastAPI webhook, and the `executor.py` spins up a Playwright browser to apply.
