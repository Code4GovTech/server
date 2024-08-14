import logging
from events.ticketEventHandler import TicketEventHandler
from handlers.EventHandler import EventHandler

class IssuesHandler(EventHandler):
    async def handle_event(self, data, postgres_client):
        # Implement your logic for handling issue events here
        try:        
            if data.get("issue"):
                issue = data["issue"]
                if await postgres_client.check_record_exists("unlisted_tickets","issue_id",issue["id"]):
                    await postgres_client.delete("unlisted_tickets","issue_id",issue["id"])
                await TicketEventHandler().onTicketCreate(data)
                if await postgres_client.checkIsTicket("unlisted_tickets","issue_id",issue["id"]):
                    await TicketEventHandler().onTicketEdit(data)
                    if data["action"] == "closed":
                        await TicketEventHandler().onTicketClose(data)
            
        except Exception as e:
            logging.info(e)
            raise Exception
