import logging
import json
from handlers.EventHandler import EventHandler
from events.ticketEventHandler import TicketEventHandler
from utils.db import PostgresORM

class IssuesHandler(EventHandler):
    async def handle_event(self, data, postgres_client):
        # Implement your logic for handling issue events here
        try:        
            module_name = data.get("action")
            print('inside handle events for ', module_name)
            issue = data["issue"]
            labels = issue["labels"]
            print(f'inside issue handler with issue data as {issue} and label as {labels}')
            if next((l for l in labels if l['name'].lower() == 'c4gt community'), None):
                handler_method = getattr(self, f'handle_issue_{module_name}', None)
                if handler_method:
                    await handler_method(data)
                    await self.log_user_activity(data)
                else:
                    logging.info(f"No handler found for module: {module_name}")
            elif module_name == 'unlabeled':
                handler_method = getattr(self, f'handle_issue_{module_name}', None)
                if handler_method:
                    await handler_method(data)
                    await self.log_user_activity(data)
            
            return 'success'

            
        except Exception as e:
            print('exception ',e)
            logging.info(e)
            raise Exception
        
    async def handle_issue_created(self, data):
        # Implement your logic for handling issue events here
        try:      
            postgres_client = PostgresORM.get_instance()  
            if data.get("issue"):
                issue = data["issue"]
                print('inside issue created with', issue)
                if await postgres_client.get_issue_from_issue_id(issue["id"]):
                    await postgres_client.delete("issues", "issue_id", issue["id"])
                await TicketEventHandler().onTicketCreate(data)
            
        except Exception as e:
            print('exception', e)
            logging.info(e)
            raise Exception
        
    async def handle_issue_opened(self, data):
        # Implement your logic for handling issue events here
        try:   
            postgres_client = PostgresORM.get_instance()     
            if data.get("issue"):
                issue = data["issue"]
                print('inside issue opened with', issue)
                await TicketEventHandler().onTicketCreate(data)
            
        except Exception as e:
            logging.info(e)
            raise Exception
        
    async def handle_issue_labeled(self, data):
        try:
            print(json.dumps(data, indent=4))
            postgres_client = PostgresORM.get_instance()
            issue = data["issue"]
            print('inside issue labeled with', issue)
            db_issue = await postgres_client.get_issue_from_issue_id(issue["id"])
            if not db_issue:
                await self.handle_issue_opened(data)
            labels = issue["labels"]
            print(labels)
            if labels:
                db_issue["labels"] = labels["name"]
                await postgres_client.update_data(db_issue, 'id', 'issues')
                
            return "success"
        except Exception as e:
            print('exception occured while handling labels ', e)
            logging.info(e)
            raise Exception
        
    async def handle_issue_unlabeled(self, data):
        try:
            postgres_client = PostgresORM.get_instance()
            if data["action"] == "unlabeled":
                issue = data["issue"]
                db_issue = await postgres_client.get_data('id', 'issues', issue["id"])
                print('db issue in unlabeled is ', db_issue)
                if db_issue:
                    print('inside of if for unlabeled ')
                    await postgres_client.delete("issue_contributors","issue_id",db_issue["id"])
                    await postgres_client.delete("issue_mentors","issue_id",db_issue["id"])
                    # Delete Ticket
                    await postgres_client.delete("issues","id",db_issue["id"])
                    print('issue removed')
                else:
                    print('issue could not be removed')
                return 'success'
        except Exception as e:
            print('exception occured while handling labels ', e)
            logging.info(e)
            raise Exception
        
    async def handle_issue_edited(self, data):
        try:
            postgres_client = PostgresORM.get_instance()
            print(json.dumps(data, indent=4))
            issue = data["issue"]
            print('inside issue edited with', issue)
            db_issue = await postgres_client.get_data('issue_id', 'issues', issue["id"], "*")
            if not db_issue:
                await self.handle_issue_opened(data, postgres_client)
            
            body = issue["body"]
            print(body)
            if body:
                await TicketEventHandler().onTicketEdit(data)
                
            return "success"
        except Exception as e:
            print(e)
            logging.info(e)
            raise Exception


    async def handle_issue_closed(self, data):
        try:
            postgres_client = PostgresORM.get_instance()
            issue = data["issue"]
            print('inside issue closed with', issue)
            issue_exist = await postgres_client.get_data('issue_id', 'issues', issue["id"])
            if issue_exist:
                await TicketEventHandler().onTicketClose(issue)
            return "success"
        except Exception as e:
            logging.info(e)
            raise Exception
        

    async def handle_issue_assigned(self, data):
        try:
            postgres_client = PostgresORM.get_instance()
            issue = data["issue"]
            print('inside issue closed with', issue)
           
            await TicketEventHandler().add_assignee(issue)
            return "success"
        except Exception as e:
            print('exception occured while assigning an assignee to a ticket ', e)
            raise Exception
        
    async def log_user_activity(self, data):
        try:
            postgres_client = PostgresORM.get_instance()
            issue = data["issue"]
            print('inside user activity', issue)
            issue = await postgres_client.get_data('issue_id', 'issues', issue["id"])

            user_id = data['issue']['user']['id']
            
            contributor = await self.postgres_client.get_data('github_id', 'contributors_registration', user_id, '*')
            contributor_id = contributor["id"]

            activity_data = {
                "issue_id": issue["id"],
                "activity": f"issue_{data['action']}",
                "created_at": issue['created_at'],
                "updated_at": issue['updated_at'],
                "contributor_id": contributor_id,
                "mentor_id": ""
            }
            saved_activity_data = await postgres_client.add_data(activity_data,"user_activity")
            return saved_activity_data
        
        except Exception as e:
            logging.info(e)
            raise Exception
        

    

