import logging
import json
from handlers.EventHandler import EventHandler
from events.ticketEventHandler import TicketEventHandler
from utils.db import SupabaseInterface



def filter_points(data):
    try:
        result = {}
        for value in data:
            result.update({value['role']:value['points']})
        
        return result
    except Exception as e:
        print(e)
        return {}
    
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


    async def handle_issue_closed(self, data, supabase_client):
        try:
            issue = data["issue"]           
            issue_data = supabase_client.get_issue_from_issue_id(issue['id'])                
            contributors = supabase_client.get_contributors_from_issue_id(issue_data['id']) if issue else None
            mentors = supabase_client.get_mentors_from_issue_id(issue_data['id']) if issue else None
            
            # find points for the closed issue
            complexity = issue_data['complexity']
            point_matrix = supabase_client.get_default_points(complexity) if complexity else None
            points = filter_points(point_matrix) if point_matrix else 0
            
            # save record in point transactions
            user_point_status,ment_point_status = SupabaseInterface().get_instance().add_userpoints(contributors['contributor_id'],mentors['mentor_id'],issue_data['id'],points,"credit")
            
            # add an activity
            user_activity = SupabaseInterface().get_instance().manage_user_activity(contributors['contributor_id'],mentors['mentor_id'],issue_data['id'],"closed")
            
            # add overall points
            contributor_points = SupabaseInterface().get_instance().add_contributor_points(contributors['contributor_id'],"contributor",points['Contributor'],complexity) if user_point_status else None
            mentor_points = SupabaseInterface().get_instance().add_contributor_points(mentors['mentor_id'],"mentor",points['Mentor'],complexity) if ment_point_status else None
            
            #generate badges
            
            #generate certificates
            
            
            
            return "success"
        except Exception as e:
            logging.info(e)
            raise Exception



    