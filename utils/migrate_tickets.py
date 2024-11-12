import logging
from utils.db import PostgresORM
import aiohttp
from datetime import datetime

class MigrateTickets:
    def __init__(self):
        self.postgres_client = PostgresORM.get_instance()
        return
    

    def convert_to_datetime(self, date_str):
        return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')

    async def migrate_ccbp_tickets(self):
        try:
            
            ccbp_tickets = await self.postgres_client.readAll('ccbp_tickets')
            issues_to_insert = []

            for ticket in ccbp_tickets:
                # Create an Issues object with mapped fields from CcbpTickets
                print(ticket)
                org = ticket['organization']
                if org:
                    org_exist = await self.postgres_client.get_data("name", "community_orgs", org)
                    if org and (org_exist is None):
                        new_org = await self.postgres_client.add_data(data={"name":org}, table_name="community_orgs")
                        org_exist = await self.postgres_client.get_data("name", "community_orgs", org)
                else: 
                    org_exist = None

                created_at = ticket['created_at'].strftime('%Y-%m-%dT%H:%M:%SZ') if ticket['created_at'] else None
                if created_at:
                    created_at = self.convert_to_datetime(created_at)

                closed_at = ticket['closed_at'].strftime('%Y-%m-%dT%H:%M:%SZ') if ticket['closed_at'] else None
                if closed_at:
                    closed_at = self.convert_to_datetime(closed_at)

                new_issue = {
                    "link":ticket['url'],
                    "labels": ['C4GT Community'],  # Modify based on your requirement
                    "project_type":ticket['project_category'][0] if ticket['project_category'] else None,
                    "complexity":ticket['complexity'],
                    "skills":None,
                    "technology":", ".join(ticket['reqd_skills']) if ticket['reqd_skills'] else None,
                    "status":ticket['status'],
                    "created_at": created_at,
                    "updated_at": closed_at,  # Assume updated at current timestamp
                    "title":ticket['name'],
                    "domain":ticket['project_sub_category'],
                    "description":f"Ticket points: {ticket['ticket_points']}, Author: {ticket['issue_author']}",
                    "issue_id":ticket['issue_id'],
                    "org_id": org_exist[0]["id"] if org_exist else None
                }
                inserted_ticket = await self.postgres_client.record_created_ticket(data=new_issue,table_name="issues")
                if inserted_ticket:
                    print('inserted_ticket ', inserted_ticket)
                else:
                    continue

                data = {
                    "assignee": ticket['assignees'],
                    "mentor": ticket['mentors'],
                    "issue_id": ticket['issue_id']
                }
                await self.migrate_ticket_contributor(data)
                
            return 'success'
        except Exception as e:
            print('exception occured ', e)
            return 'failed'
    

    async def migrate_ticket_contributor(self, data):
        try:
            assignee = data["assignee"]
            mentor = data["mentor"][0]
            issue_id = data["issue_id"]


            issue = await self.postgres_client.get_data("issue_id","issues", issue_id)

            if assignee:
                url = f'https://api.github.com/users/{assignee}'
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        assignee_data = await response.json()
                if assignee_data:
                    user = await self.postgres_client.get_data("github_id","contributors_registration", assignee_data[0]["id"])
                    contributors_data = {
                                    "issue_id": issue[0]['id'],
                                    "role": 1,
                                    "contributor_id": user[0]["id"] if user else None,
                                    "created_at":str(datetime.now()),
                                    "updated_at":str(datetime.now())
                                }
                    inserted_data = await self.postgres_client.add_data(contributors_data, "issue_contributors")
                    print('inserted contributor is ', inserted_data)

            if mentor:
                url = f'https://api.github.com/users/{mentor}'
                angel_mentor_detials = []
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        angel_mentor_data = await response.json()
                if angel_mentor_data:
                    angel_mentor_id = angel_mentor_data["id"]
                    angel_mentor_detials = await self.postgres_client.get_data("github_id","contributors_registration", angel_mentor_id)
                    if not angel_mentor_detials:
                        #add the data in a seperate table
                        mentor_not_added = {
                            "mentor_github_id": angel_mentor_id,
                            "issue_id": issue[0]['id']
                        }
                        inserted_mentor_not_added_data = await self.postgres_client.add_data(mentor_not_added, "mentor_not_added") 
                        # print('mentor not added data ', inserted_mentor_not_added_data)       

                if angel_mentor_detials:
                    mentor_data = {
                        "issue_id": issue[0]['id'],
                        "org_mentor_id": None,
                        "angel_mentor_id":angel_mentor_detials[0]['id'] if angel_mentor_detials else None,
                        "created_at":str(datetime.now()),
                        "updated_at":str(datetime.now())
                    }
                    inserted_mentor = await self.postgres_client.add_data(mentor_data, "issue_mentors")
                    print('inserted mentor is ', inserted_mentor)
            
            return 'success'

        except Exception as e:
            print('exception occured ', e)
            return 'failed'