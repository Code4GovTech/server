import logging
import json
from handlers.EventHandler import EventHandler
from events.ticketEventHandler import TicketEventHandler
from utils.db import SupabaseInterface

class IssuesHandler(EventHandler):
    async def handle_event(self, data, supabase_client):
        # Implement your logic for handling issue events here
        try:        
            module_name = data.get("action")
            print('inside handle events')
            handler_method = getattr(self, f'handle_issue_{module_name}', None)
            if handler_method:
                await handler_method(data, supabase_client)
            else:
                logging.info(f"No handler found for module: {module_name}")

            
        except Exception as e:
            logging.info(e)
            raise Exception
        
    async def handle_issue_opened(self, data, supabase_client):
        # Implement your logic for handling issue events here
        try:        
            if data.get("issue"):
                issue = data["issue"]
                if supabase_client.checkUnlisted(issue["id"]):
                    supabase_client.deleteUnlistedTicket(issue["id"])
                await TicketEventHandler().onTicketOpened(data)
                if supabase_client.checkIsTicket(issue["id"]):
                    await TicketEventHandler().onTicketEdit(data)
                    if data["action"] == "closed":
                        await TicketEventHandler().onTicketClose(data)
            
        except Exception as e:
            logging.info(e)
            raise Exception
        
    async def handle_issue_labeled(self, data, supabase_client):
        try:
            print(json.dumps(data, indent=4))
            issue = data["issue"]
            db_issue = SupabaseInterface.get_data('id', 'issues', issue["id"])
            if not db_issue:
                await self.handle_issue_opened(data, supabase_client)
            labels = issue["labels"]
            print(labels)
            if labels:
                db_issue["labels"] = labels
                SupabaseInterface.update_data(db_issue, 'id', 'issues')
                
            return "success"
        except Exception as e:
            logging.info(e)
            raise Exception
        
    async def handle_issue_edited(self, data, supabase_client):
        try:
            print(json.dumps(data, indent=4))
            issue = data["issue"]
            db_issue = SupabaseInterface.get_data('id', 'issues', issue["id"])
            if not db_issue:
                await self.handle_issue_opened(data, supabase_client)
            
            body = issue["body"]
            print(body)
            if body:
                db_issue["body"]
                SupabaseInterface.update_data(db_issue, 'id', 'issues')
                
            return "success"
        except Exception as e:
            logging.info(e)
            raise Exception
