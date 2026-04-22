import json
from google import genai
from pydantic import ValidationError
from app.core.config import settings
from app.schemas.job import Job, JobEvaluation

class Brain:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        self.model = "gemini-2.5-flash"
        
    def evaluate_job(self, job: Job) -> JobEvaluation:
        """
        Uses Gemini to evaluate if a job is a good match based on user's profile
        and Upwork job criteria (client history, proposal count, project size).
        """
        system_instruction = (
            "You are an AI assistant helping a freelance software engineer win bids on Upwork.\n"
            "The user is starting out, so they prefer:\n"
            "- Small to medium sized projects\n"
            "- Low competition (less than 15 proposals)\n"
            "- Reliable clients (payment verified, good ratings, previous hires)\n\n"
            "Evaluate the provided job details. Output JSON matching the following schema:\n"
            "{\n"
            '  "job_id": "string",\n'
            '  "is_match": boolean,\n'
            '  "match_score": integer (0-100),\n'
            '  "reason": "string (Why it is a match or not)",\n'
            '  "proposal_draft": "string (Draft a professional and concise proposal if it is a match, else null)"\n'
            "}"
        )
        
        prompt = (
            f"Job Details:\n"
            f"Title: {job.title}\n"
            f"Description: {job.description}\n"
            f"Budget: {job.budget}\n"
            f"Skills: {', '.join(job.skills)}\n"
            f"Proposals so far: {job.proposal_count}\n"
            f"Client Payment Verified: {job.client.payment_verified}\n"
            f"Client Past Hires: {job.client.past_hires}\n"
            f"Client Rating: {job.client.rating}\n"
            f"Please evaluate and output strictly in JSON format."
        )

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    temperature=0.2
                )
            )
            
            result_dict = json.loads(response.text)
            # Ensure job_id is correctly set
            result_dict["job_id"] = job.id
            return JobEvaluation(**result_dict)
            
        except Exception as e:
            print(f"Error evaluating job {job.id}: {e}")
            return JobEvaluation(
                job_id=job.id,
                is_match=False,
                match_score=0,
                reason=f"Failed to evaluate: {e}",
                proposal_draft=None
            )

brain = Brain()
