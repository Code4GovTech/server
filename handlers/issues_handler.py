import logging
import json
from handlers.EventHandler import EventHandler
from events.ticketEventHandler import TicketEventHandler
from shared_migrations.db.server import ServerQueries
from utils.user_activity import UserActivity

class IssuesHandler(EventHandler):
    def __init__(self):
        self.postgres_client = ServerQueries()
        self.user_activity = UserActivity()

    async def handle_event(self, data, postgres_client, **kwargs):
        # Implement your logic for handling issue events here
        try:
            token =kwargs.get("token", None)
            module_name = data.get("action")
            module_name = module_name.replace('eded', 'ed')
            print('inside handle events for ', module_name)
            issue = data["issue"]
            labels = issue["labels"]
            print(f'inside issue handler with issue data as {issue} '
                  f'\n label as {labels}')
            if next((l for l in labels if l['name'].lower() in ['c4gt community', 'c4gt bounty','c4gt coding','dmp 2026']), None):
                handler_method = getattr(self, f'handle_issue_{module_name}', None)
                print(handler_method)
                if handler_method:
                    if token is not None:
                        await handler_method(data,
                                             token=token)
                    else:
                        await handler_method(data)
                    # await self.log_user_activity(data)
                    await self.user_activity.log_user_activity(data, 'issue')
                else:
                    logging.info(f"No handler found for module: {module_name}")
            elif module_name == 'unlabeled':
                handler_method = getattr(self, f'handle_issue_{module_name}', None)
                if handler_method:
                    await handler_method(data)
                    # await self.log_user_activity(data)
                    await self.user_activity.log_user_activity(data, 'issue')
            
            return 'success'

            
        except Exception as e:
            print(f'{e.__traceback__.tb_lineno} - {str(e)}')
            print('exception ',e)
            logging.info(e)
            raise Exception
        
    async def handle_issue_created(self, data, **kwargs):
        # Implement your logic for handling issue events here
        try:
            token = kwargs.get("token", None)
            
            if data.get("issue"):
                issue = data["issue"]
                print('inside issue created with', issue)
                if await self.postgres_client.get_issue_from_issue_id(issue["id"]):
                    await self.postgres_client.delete("issues", "issue_id", issue["id"])
                if token is not None:
                    await TicketEventHandler().onTicketCreate(data,
                                                              token=token)
                else:
                    await TicketEventHandler().onTicketCreate(data)

        except Exception as e:
            print('exception', e)
            logging.info(e)
            raise Exception
        
    async def handle_issue_opened(self, data, **kwargs):
        # Implement your logic for handling issue events here
        try:
            token = kwargs.get("token", None)
            if data.get("issue"):
                issue = data["issue"]
                print('inside issue opened with', issue)
                if token is not None:
                    await TicketEventHandler().onTicketCreate(data,
                                                              token=token)
                else:
                    await TicketEventHandler().onTicketCreate(data)
            
        except Exception as e:
            logging.info(e)
            raise Exception
        
    # async def handle_issue_labeled(self, data, **kwargs):
    #     try:
    #         token = kwargs.get("token", None)
    #         print(json.dumps(data, indent=4))
            
    #         issue = data["issue"]
    #         print('inside issue labeled with', issue)
    #         db_issue = await self.postgres_client.get_data('id', 'issues', issue["id"])
    #         if not db_issue:
    #             if token is not None:
    #                 await self.handle_issue_opened(data,
    #                                                token=token)
    #             else:
    #                 await self.handle_issue_opened(data)
    #         labels = issue["labels"]
    #         print(labels)
    #         if labels:
    #             label_names = [l['name'] for l in labels]
    #             db_issue["labels"] = label_names
    #             await self.postgres_client.update_data(db_issue, 'id', 'issues')
                
    #         return "success"
    #     except Exception as e:
    #         print('exception occured while handling labels ', e)
    #         logging.info(e)
    #         raise Exception
    async def handle_issue_labeled(self, data, token=None):
        try:
            issue = data.get("issue")
            if not issue:
                print("No issue data found in payload")
                return "failed"

            print("inside issue labeled with", issue)

            # Extract label names from GitHub payload
            labels = issue.get("labels", [])
            label_names = [l.get("name") for l in labels if l.get("name")]

            # Allowed labels (normalize everything)
            allowed_labels = [
                "c4gt community",
                "c4gt bounty",
                "c4gt coding",
                "dmp 2026"
            ]

            # Check if any allowed label exists
            if not any(l.strip().lower() in allowed_labels for l in label_names):
                print("No allowed labels found, skipping issue.")
                return "skipped"

            github_issue_id = issue.get("id")

            #  Correct lookup using issue_id column (NOT id)
            db_issue = await self.postgres_client.get_issue_from_issue_id(github_issue_id)

            # If issue not found, create it first (race condition handling)
            if not db_issue:
                print("Issue not found in DB. Creating issue first...")

                if token is not None:
                    await self.handle_issue_opened(data, token=token)
                else:
                    await self.handle_issue_opened(data)

                # Refetch after creation
                db_issue = await self.postgres_client.get_issue_from_issue_id(github_issue_id)

            if not db_issue:
                print("Issue still not found after creation attempt.")
                return "failed"

            # get_issue_from_issue_id returns list
            db_issue = db_issue[0]

            # Update labels safely
            db_issue["labels"] = label_names

            await self.postgres_client.update_data(
                db_issue,
                "id",   # primary key column
                "issues"
            )

            print("Labels updated successfully:", label_names)
            return "success"

        except Exception as e:
            print("Exception occurred while handling labels:", str(e))
            return "failed"
    async def handle_issue_unlabeled(self, data):
        try:
            
            if data["action"] == "unlabeled":
                issue = data["issue"]
                db_issue = await self.postgres_client.get_issue_from_issue_id(issue["id"])
                print('db issue in unlabeled is ', db_issue)
                if db_issue:
                    print('inside of if for unlabeled ')
                    await self.postgres_client.delete("issue_contributors","issue_id",db_issue[0]["id"])
                    await self.postgres_client.delete("issue_mentors","issue_id",db_issue[0]["id"])
                    # Delete Ticket
                    await self.postgres_client.delete("issues","id",db_issue[0]["id"])
                    print('issue removed')
                else:
                    print('issue could not be removed')
                return 'success'
        except Exception as e:
            print('exception occured while handling labels ', e)
            logging.info(e)
            raise Exception
        
    async def handle_issue_edited(self, data, **kwargs):
        try:
            token = kwargs.get("token", None)
            print(json.dumps(data, indent=4))
            issue = data["issue"]
            print('inside issue edited with', issue)
            db_issue = await self.postgres_client.get_data('issue_id', 'issues', issue["id"], "*")
            if not db_issue:
                if token is not None:
                    await self.handle_issue_opened(data, self.postgres_client,
                                                   token=token)
                else:
                    await self.handle_issue_opened(data, self.postgres_client)

            body = issue["body"]
            print(body)
            if body:
                if token is not None:
                    await TicketEventHandler().onTicketEdit(data,
                                                            token=token)
                else:
                    await TicketEventHandler().onTicketEdit(data)

            return "success"
        except Exception as e:
            print(e)
            logging.info(e)
            raise Exception


    async def handle_issue_closed(self, data, **kwargs):
        try:
            token = kwargs.get("token", None)
            
            issue = data["issue"]
            print('inside issue closed with', issue)
            issue_exist = await self.postgres_client.get_data('issue_id', 'issues', issue["id"], "*")
            print(issue_exist)
            if not issue_exist:
                await self.handle_issue_created(data,
                                                token=token)
            issue_exist = await self.postgres_client.get_data('issue_id', 'issues', issue["id"], "*")
            print(issue_exist)
            if issue_exist:
                if token is not None:
                    await TicketEventHandler().onTicketClose(issue,
                                                             token=token)
                else:
                    await TicketEventHandler().onTicketClose(issue)
                print("handle_issue_closed - Success")

            return "success"
        except Exception as e:
            print("handle_issue_closed", e)
            logging.info(e)
            raise Exception
        

    async def handle_issue_assigned(self, data):
        try:
            
            issue = data["issue"]
            print('inside issue closed with', issue)
           
            await TicketEventHandler().add_assignee(issue)
            return "success"
        except Exception as e:
            print('exception occured while assigning an assignee to a ticket ', e)
            raise Exception

    async def handle_issue_unassigned(self, data):
        try:
            
            issue = data["issue"]
            db_issue = await self.postgres_client.get_issue_from_issue_id(issue["id"])
            print('db issue in unlabeled is ', db_issue)
            if db_issue:
                await self.postgres_client.delete("issue_contributors","issue_id",db_issue[0]["id"])
            return "success"
        except Exception as e:
            print('exception occured while removing an assignee to a ticket ', e)
            raise Exception

    # async def log_user_activity(self, data):
    #     try:
            
    #         issue = data["issue"]
    #         print('inside user activity', issue)
    #         issue = await self.postgres_client.get_data('issue_id', 'issues', issue["id"])

    #         user_id = data['issue']['user']['id']
            
    #         contributor = await self.postgres_client.get_data('github_id', 'contributors_registration', user_id, '*')
    #         contributor_id = contributor[0]["id"]
    #         mentor = await self.postgres_client.get_data('issue_id', 'issue_mentors',issue[0]["id"])
    #         activity_data = {
    #             "issue_id": issue[0]["id"],
    #             "activity": f"issue_{data['action']}",
    #             "created_at": issue[0]['created_at'],
    #             "updated_at": issue[0]['updated_at'],
    #             "contributor_id": contributor_id,
    #             "mentor_id": mentor[0]["angel_mentor_id"] if mentor else None
    #         }
    #         saved_activity_data = await self.postgres_client.add_data(activity_data,"user_activity")
    #         return saved_activity_data
        
    #     except Exception as e:
    #         logging.info(e)
    #         raise Exception
        

    

