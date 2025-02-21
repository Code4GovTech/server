import logging
from shared_migrations.db.server import ServerQueries

class UserActivity:

    async def log_user_activity(self, data, activity):
        try:
            postgres_client = ServerQueries()
            issue = data["issue"]
            print('inside user activity', issue)
            issue = await postgres_client.get_data('issue_id', 'issues', issue["id"])

            user_id = data['issue']['user']['id']
            
            contributor = await postgres_client.get_data('github_id', 'contributors_registration', user_id, '*')
            contributor_id = contributor[0]["id"]
            mentor = await postgres_client.get_data('issue_id', 'issue_mentors',issue[0]["id"])
            activity_data = {
                "issue_id": issue[0]["id"],
                "activity": f"{activity}_{data['action']}",
                "created_at": issue[0]['created_at'],
                "updated_at": issue[0]['updated_at'],
                "contributor_id": contributor_id,
                "mentor_id": mentor[0]["angel_mentor_id"] if mentor else None
            }
            saved_activity_data = await postgres_client.add_data(activity_data,"user_activity")
            return saved_activity_data
        
        except Exception as e:
            logging.info(e)
            print(f'{e.__traceback__.tb_lineno} - {str(e)}')
            raise Exception