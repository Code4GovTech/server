from events.ticketEventHandler import TicketEventHandler
import logging
from handlers.EventHandler import EventHandler

class InstallationHandler(EventHandler):
    async def handle_event(self, data, supabase_client):
        # Implement your logic for handling issue events here
        try:            
            if data.get("installation") and data["installation"].get("account"):
                # if data["action"] not in ["deleted", "suspend"]:
                await TicketEventHandler().updateInstallation(data.get("installation"))
            

        except Exception as e:        
            logging.info(e)
            raise Exception
    
