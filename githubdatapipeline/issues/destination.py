from utils.db import SupabaseInterface, PostgresORM
import sys
def hasCommunityLabel(labels):
    if any([label["name"].lower() == "c4gt community" for label in labels]):
        return True
    return False

async def recordIssue(issue):
    # currentTickets = SupabaseInterface.get_instance().readAll(table="community_program_tickets")
    currentTickets = await PostgresORM().readAll(table="community_program_tickets")
    iss = {
            "url": issue["url"] if issue.get("url") else None,
            "repository_url": issue["repository_url"] if issue.get("repository_url") else None,
            "comments_url": issue["comments_url"]  if issue.get("comments_url") else None,
            "events_url":issue["events_url"] if issue.get("events_url") else None,
            "html_url": issue["html_url"] if issue.get("html_url") else None,
            "id": issue["id"] if issue.get("id") else None,
            "node_id": issue["node_id"] if issue.get("node_id") else None,
            "title": issue["title"] if issue.get("title") else None,
            "raised_by_username": issue["user"]["login"] if issue.get("user") else None,
            "raised_by_id": issue["user"]["id"] if issue.get("user") else None,
            "labels": issue["labels"] if issue.get("labels") else None,
            "status": issue["state"] if issue.get("state") else None,
            "assignees": issue["assignees"] if issue.get("assignees") else None,
            "number_of_comments": issue["comments"] if issue.get("comments") else None,
            "created_at": issue["created_at"] if issue.get("created_at") else None,
            "updated_at": issue["updated_at"] if issue.get("updated_at") else None,
            "closed_at":issue["closed_at"] if issue.get("closed_at") else None,
            "community_label": hasCommunityLabel(issue["labels"])

            }
    
    if iss["id"] in [ticket["id"] for ticket in currentTickets]:
        # SupabaseInterface.get_instance().update(table="community_program_tickets", update=iss, query_key="id", query_value=iss["id"])
        await PostgresORM().update_data(data=iss, col_name="id", table="community_program_tickets")
        print("updated", file = sys.stderr)
    else:
        # SupabaseInterface.get_instance().insert(table="community_program_tickets", data=iss)
        await PostgresORM().add_data(data=iss, table="community_program_tickets")
        print("created", file = sys.stderr)
    
    
    
