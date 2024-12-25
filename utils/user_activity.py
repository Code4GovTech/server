import logging
from utils.db import PostgresORM
from shared_migrations.db.server import ServerQueries

class UserActivity:
    def __init__(self):
        self.postgres_client = ServerQueries()
        return
    
    async def log_user_activity(self, data, activity):
        try:
            
            issue = data["issue"]
            print('inside user activity', issue)
            issue = await self.postgres_client.get_data('issue_id', 'issues', issue["id"])

            user_id = data['issue']['user']['id']
            
            contributor = await self.postgres_client.get_data('github_id', 'contributors_registration', user_id, '*')
            contributor_id = contributor[0]["id"]
            mentor = await self.postgres_client.get_data('issue_id', 'issue_mentors',issue[0]["id"])
            activity_data = {
                "issue_id": issue[0]["id"],
                "activity": f"{activity}_{data['action']}",
                "created_at": issue[0]['created_at'],
                "updated_at": issue[0]['updated_at'],
                "contributor_id": contributor_id,
                "mentor_id": mentor[0]["angel_mentor_id"] if mentor else None
            }
            saved_activity_data = await self.postgres_client.add_data(activity_data,"user_activity")
            return saved_activity_data
        
        except Exception as e:
            logging.info(e)
            raise Exception