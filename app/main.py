from fastapi import FastAPI, Request, Form
from twilio.twiml.messaging_response import MessagingResponse
from app.modules.executor import executor
from app.schemas.job import JobEvaluation
import asyncio
import json
import redis
from app.core.config import settings

app = FastAPI(title="Upwork Proposal Agent")

# Connect to Redis to store pending job evaluations
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(Body: str = Form(...), From: str = Form(...)):
    """
    Webhook to handle incoming WhatsApp messages from Twilio.
    User replies format: 
    - "YES [job_id]"
    - "NO [job_id]"
    - "AMEND [job_id] [new text]"
    """
    message_body = Body.strip()
    sender = From

    # Ensure it's from the registered number
    if sender != f"whatsapp:{settings.MY_WHATSAPP_NUMBER}":
        return {"status": "unauthorized"}

    parts = message_body.split(maxsplit=2)
    command = parts[0].upper()
    job_id = parts[1] if len(parts) > 1 else None

    response = MessagingResponse()
    msg = response.message()

    if not job_id:
        msg.body("Invalid format. Reply with YES [job_id], NO [job_id], or AMEND [job_id] [text].")
        return str(response)

    # Fetch evaluation from Redis
    eval_json = redis_client.get(f"job_eval:{job_id}")
    
    if not eval_json:
        msg.body(f"Job {job_id} not found or expired.")
        return str(response)

    evaluation = JobEvaluation.model_validate_json(eval_json)

    if command == "YES":
        msg.body(f"Applying to job {job_id}...")
        asyncio.create_task(executor.submit_proposal(evaluation))
    elif command == "NO":
        msg.body(f"Skipping job {job_id}.")
        redis_client.delete(f"job_eval:{job_id}")
    elif command == "AMEND":
        if len(parts) < 3:
            msg.body("Please provide the amended proposal text.")
            return str(response)
        
        amended_text = parts[2]
        msg.body(f"Applying to job {job_id} with amended proposal...")
        asyncio.create_task(executor.submit_proposal(evaluation, modified_proposal=amended_text))
    else:
        msg.body("Unknown command. Reply with YES, NO, or AMEND.")

    return str(response)

@app.get("/")
def health_check():
    return {"status": "ok", "service": "Upwork Proposal Agent"}
