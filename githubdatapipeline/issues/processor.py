import aiohttp, asyncio, sys, os, re, json
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
    pattern = r'^PR_'
    return bool(re.match(pattern, string))

async def get_connected_pr(github_token, owner, repo, issue_number):
    query = """
    {
      repository(owner: "%s", name: "%s") {
        issue(number: %d) {
          timelineItems(itemTypes: CONNECTED_EVENT, first: 10) {
            nodes {
              ... on ConnectedEvent {
                subject {
                  ... on PullRequest {
                    url
                    id
                    databaseId
                    createdAt
                    author {
                      login
                      ... on User {
                        id
                        databaseId
                      }
                    }
                    merged
                    mergedBy {
                      login
                      ... on User {
                        id
                        databaseId
                      }
                    }
                    mergedAt
                    state
                  }
                }
              }
            }
          }
        }
      }
    }
    """ % (owner, repo, issue_number)

    headers = {
        'Authorization': f'bearer {github_token}',
        'Content-Type': 'application/json'
    }

    async with aiohttp.ClientSession() as session:
        async with session.post('https://api.github.com/graphql', data=json.dumps({'query': query}), headers=headers) as response:
            if response.status != 200:
                print("Error:", response.status)
                return None

            data = await response.json()

            if 'errors' in data:
                print(data['errors'])
                return None

            connected_prs = [
                {
                    'html_url': item['subject']['url'],
                    'pr_id': item['subject']['databaseId'],
                    'raised_by_username': item['subject']['author']['login'],
                    'raised_at': item['subject']['createdAt'],
                    'is_merged': item['subject']['merged'],
                    'merged_by_username': item['subject']['mergedBy']['login'] if 'mergedBy' in item['subject'] else None,
                    'merged_at': item['subject']['mergedAt'],
                    'status': item['subject']['state']
                }
                for item in data['data']['repository']['issue']['timelineItems']['nodes']
            ]

            return connected_prs
        
async def returnConnectedPRs(issue):
    connectedEntityDetails = []
    timeline_url = issue["timeline_url"]
    timeline = await get_url(timeline_url)

    for timelineEvent in timeline:
        if timelineEvent["event"] == "cross-referenced":
            if "source" in timelineEvent:
                linkedEntity = timelineEvent["source"]
                if linkedEntity["type"] == "issue":
                    if starts_with_pr(linkedEntity["issue"]["node_id"]):
                        entityDeets = {
                            "html_url": linkedEntity["issue"]["html_url"],
                            "pr_id": linkedEntity["issue"]["id"],
                            "raised_by": linkedEntity["issue"]["user"]["id"],
                            "raised_by_username": linkedEntity["issue"]["user"]["login"],
                            'raised_at': linkedEntity["issue"]["created_at"],
                            "is_merged": True if linkedEntity["issue"]["pull_request"]["merged_at"] else False,
                            "merged_by": linkedEntity["issue"]["pull_request"]["merged_by"]["id"] if 'merged_by' in linkedEntity["issue"]["pull_request"] else None,
                            'merged_by_username': linkedEntity["issue"]["pull_request"]["merged_by"]["login"] if 'merged_by' in linkedEntity["issue"]["pull_request"] else None,
                            'merged_at': linkedEntity["issue"]["pull_request"]["merged_at"],
                            "status": linkedEntity["issue"]["state"]
                        }
                        if entityDeets not in connectedEntityDetails:
                            connectedEntityDetails.append(entityDeets)
        if timelineEvent["event"] == "connected":
            if "url" in timelineEvent:
                # eventUrl = timelineEvent["url"]
                # components = eventUrl.split('/')
                components = issue["html_url"].split('/')
                owner, repo, number = components[-4], components[-3], components[-1]
                github_token = os.getenv("GithubPAT")
                prs = get_connected_pr(github_token, owner, repo, int(number))
                if prs:
                  for pr in prs:
                      if pr not in connectedEntityDetails:
                          connectedEntityDetails.append(pr)

    return connectedEntityDetails