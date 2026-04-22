import time
import json
import redis
from app.modules.collector import collector
from app.modules.brain import brain
from app.modules.notifier import notifier
from app.core.config import settings

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

def main():
    print("Starting Upwork Job Poller...")
    
    while True:
        try:
            # Fetch recent jobs (in a real scenario, keep track of last seen job IDs)
            jobs = collector.fetch_recent_jobs(query="python")
            
            for job in jobs:
                # Check if we've already processed this job
                if redis_client.get(f"job_processed:{job.id}"):
                    continue
                
                print(f"Evaluating new job: {job.title}")
                evaluation = brain.evaluate_job(job)
                
                # Mark as processed so we don't re-evaluate
                redis_client.setex(f"job_processed:{job.id}", 86400 * 7, "1") # Expire in 7 days
                
                if evaluation.is_match and evaluation.match_score >= 70:
                    print(f"Match found! Score: {evaluation.match_score}. Sending notification...")
                    
                    # Store evaluation data in Redis so FastAPI can access it when user replies
                    redis_client.setex(
                        f"job_eval:{job.id}", 
                        86400, # 24 hours expiry for taking action
                        evaluation.model_dump_json()
                    )
                    
                    # Notify via WhatsApp
                    notifier.send_proposal_notification(job, evaluation)
                else:
                    print(f"Job {job.id} not a good match. Score: {evaluation.match_score}. Reason: {evaluation.reason}")
            
            # Poll every 10 minutes
            print("Sleeping for 10 minutes...")
            time.sleep(600)
            
        except Exception as e:
            print(f"Error in polling loop: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
