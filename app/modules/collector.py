import requests
from typing import List
from app.core.security import auth_service
from app.schemas.job import Job, ClientInfo

class UpworkCollector:
    def __init__(self):
        # We will use the REST API as fallback, but here is where you would put GraphQL URL
        # e.g., self.graphql_url = "https://api.upwork.com/graphql"
        self.search_url = "https://www.upwork.com/api/profiles/v2/search/jobs.json"
        
    def fetch_recent_jobs(self, query: str = "python") -> List[Job]:
        """
        Fetches recent jobs matching the query.
        """
        try:
            token = auth_service.get_valid_token()
        except Exception as e:
            print(f"Auth error (using mock data for now): {e}")
            return self._mock_jobs()

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Example using REST API for jobs
        params = {
            "q": query,
            "sort": "create_time desc",
            "paging": "0;10" # get top 10
        }
        
        try:
            # We would normally make this request:
            # response = requests.get(self.search_url, headers=headers, params=params)
            # response.raise_for_status()
            # data = response.json()
            # return self._parse_jobs(data)
            
            # Since we may not have a valid auth yet, return mock
            print("Simulating Upwork API call...")
            return self._mock_jobs()
            
        except Exception as e:
            print(f"Error fetching jobs: {e}")
            return []

    def _mock_jobs(self) -> List[Job]:
        return [
            Job(
                id="12345",
                title="Build a simple Python script for web scraping",
                description="Need a python script to scrape some data from a public website and output to CSV.",
                budget=50.0,
                skills=["python", "web-scraping"],
                client=ClientInfo(
                    payment_verified=True,
                    past_hires=10,
                    total_spent=500.0,
                    country="United States",
                    rating=4.8
                ),
                proposal_count="Less than 5",
                url="https://www.upwork.com/jobs/~12345"
            ),
            Job(
                id="67890",
                title="Complex enterprise system migration",
                description="Looking for an agency to migrate our entire infrastructure to AWS.",
                budget=5000.0,
                skills=["aws", "python", "kubernetes"],
                client=ClientInfo(
                    payment_verified=False,
                    past_hires=0,
                    total_spent=0.0,
                    country="Unknown",
                    rating=None
                ),
                proposal_count="20 to 50",
                url="https://www.upwork.com/jobs/~67890"
            )
        ]

collector = UpworkCollector()
