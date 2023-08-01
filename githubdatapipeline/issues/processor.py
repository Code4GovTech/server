import aiohttp, asyncio, sys, os, re
from utils.db import SupabaseInterface

async def get_url(url):
    headers = {
            'Authorization': f'Bearer {os.getenv("GithubPAT")}',
            'Accept': 'application/vnd.github.machine-man-preview+json'  # Required for accessing GitHub app APIs
            }
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url) as response:
                response.raise_for_status()  # Raise an exception if the response status is not 2xx (successful)
                return await response.json()
    except aiohttp.ClientError as e:
        print(f"An error occurred while fetching the URL: {e}")
        return None
# tickets = SupabaseInterface().readAll("ccbp_tickets")
# closedTickets =

def starts_with_pr(string):
    pattern = r'^PR_'  # r indicates a raw string
    return bool(re.match(pattern, string))

async def get_closing_pr(issue):
    api_url = issue["url"]
    fullIssue = await get_url(api_url)
    # print(fullIssue, file = sys.stderr)
    timeline_url = fullIssue["timeline_url"]
    timeline = await get_url(timeline_url)
    print(f"There are {len(timeline)} events", file=sys.stderr)
    prs = []
    for timelineEvent in timeline:
        # print(timelineEvent["event"], sys.stderr)
        if timelineEvent["event"]=="cross-referenced":
            # print(timelineEvent, file=sys.stderr)
            if "source" in timelineEvent:
                linkedEntity = timelineEvent["source"]
                if linkedEntity["type"]=="issue":
                    if starts_with_pr(linkedEntity["issue"]["node_id"]):
                        prs.append(linkedEntity["issue"]["url"])
    return prs

        
