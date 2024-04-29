import logging
from events.ticketEventHandler import TicketEventHandler
from handlers.EventHandler import EventHandler

class IssuesHandler(EventHandler):
    async def handle_event(self, data, supabase_client):
        # Implement your logic for handling issue events here
        try:        
            if data.get("issue"):
                issue = data["issue"]
                if supabase_client.checkUnlisted(issue["id"]):
                    supabase_client.deleteUnlistedTicket(issue["id"])
                await TicketEventHandler().onTicketCreate(data)
                if supabase_client.checkIsTicket(issue["id"]):
                    await TicketEventHandler().onTicketEdit(data)
                    if data["action"] == "closed":
                        await TicketEventHandler().onTicketClose(data)
            pass
        except Exception as e:
            logging.info(e)
            pass
