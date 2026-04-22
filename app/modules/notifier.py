from twilio.rest import Client
from app.core.config import settings
from app.schemas.job import Job, JobEvaluation

class Notifier:
    def __init__(self):
        self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        self.from_whatsapp_number = f"whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}"
        self.to_whatsapp_number = f"whatsapp:{settings.MY_WHATSAPP_NUMBER}"

    def send_proposal_notification(self, job: Job, evaluation: JobEvaluation):
        """
        Sends a WhatsApp notification to the user about a matched job.
        """
        message_body = (
            f"🚀 *New Upwork Job Match!*\n\n"
            f"*Title:* {job.title}\n"
            f"*Score:* {evaluation.match_score}/100\n"
            f"*Budget:* ${job.budget if job.budget else 'N/A'}\n"
            f"*Proposals:* {job.proposal_count}\n\n"
            f"*Why:* {evaluation.reason}\n\n"
            f"*Draft Proposal:*\n{evaluation.proposal_draft}\n\n"
            f"🔗 {job.url}\n\n"
            f"Reply *YES {job.id}* to apply automatically, or *AMEND {job.id} [your changes]* to modify."
        )

        try:
            message = self.client.messages.create(
                body=message_body,
                from_=self.from_whatsapp_number,
                to=self.to_whatsapp_number
            )
            print(f"Notification sent for job {job.id}. Message SID: {message.sid}")
        except Exception as e:
            print(f"Failed to send WhatsApp notification: {e}")

notifier = Notifier()
