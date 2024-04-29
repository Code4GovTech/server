import logging
from handlers.EventHandler import EventHandler


class Pull_requestHandler(EventHandler):
    async def handle_event(self, data, supabase_client):
        # Implement your logic for handling issue events here
        try:
           
            pass
        except Exception as e:
            logging.info(e)
            pass
        
        

