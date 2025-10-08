import logging
from handlers.EventHandler import EventHandler

class LabelHandler(EventHandler):
    async def handle_event(self, data, postgres_client):
        # Implement your logic for handling issue events here
        try:
            if data.get("action") == 'edited' and 'name' in data.get("changes"):
                label_name = data["label"]["name"].lower()
                if 'c4gt' in label_name and label_name not in ['c4gt community', 'dmp 2024','c4gt bounty','c4gt coding']:
                    tickets = await postgres_client.readAll("ccbp_tickets")
                    for ticket in tickets:
                        ticket_url_elements = ticket["url"].split('/')
                        repository_url_elements = ticket_url_elements[:-2]
                        repository_url = '/'.join(repository_url_elements)
                        if repository_url == data["repository"]["html_url"]:
                            await postgres_client.delete("ccbp_tickets","issue_id",ticket["issue_id"])
                            await postgres_client.delete("dmp_tickets","issue_id",ticket["issue_id"])

            

        except Exception as e:
            logging.info(e)
            raise Exception
