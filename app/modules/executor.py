import asyncio
from playwright.async_api import async_playwright
from app.schemas.job import JobEvaluation

class Executor:
    def __init__(self):
        pass

    async def submit_proposal(self, evaluation: JobEvaluation, modified_proposal: str = None):
        """
        Submits the proposal to Upwork. 
        Since Upwork's API restricts automated proposal submissions for regular users, 
        we use Playwright to automate the UI submission.
        """
        final_proposal = modified_proposal if modified_proposal else evaluation.proposal_draft
        print(f"Submitting proposal for Job ID: {evaluation.job_id}")
        
        # NOTE: This requires a pre-authenticated session state (cookies.json) to bypass login.
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=False) # Keep False for debugging
                
                # Load auth state if exists
                try:
                    context = await browser.new_context(storage_state="upwork_state.json")
                except Exception:
                    print("No saved Upwork session. Will need manual login first.")
                    context = await browser.new_context()

                page = await context.new_page()
                
                # Navigate to job proposal page
                await page.goto(f"https://www.upwork.com/ab/proposals/job/~{evaluation.job_id}/apply")
                
                # Wait for the page to load
                await page.wait_for_load_state("networkidle")

                # The following selectors are examples and may need to be updated based on Upwork's current DOM
                
                # Select a profile if prompted
                # await page.click('input[name="profileDropdown"]')
                
                # Enter the proposal text
                # await page.fill('textarea[aria-labelledby="cover_letter_label"]', final_proposal)
                
                # Set bid amount
                # await page.fill('input[name="chargeRate"]', "25")
                
                # Submit
                # await page.click('button:has-text("Submit a Proposal")')
                
                print(f"Successfully simulated applying to job: {evaluation.job_id}")
                print(f"Proposal Used:\n{final_proposal}")
                
                await browser.close()
                return True

        except Exception as e:
            print(f"Failed to submit proposal via Playwright: {e}")
            return False

executor = Executor()
