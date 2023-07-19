import aiohttp, asyncio
from aiographql.client import GraphQLClient, GraphQLRequest
async def get_closing_pr(repo, owner, num):
    async with aiohttp.ClientSession() as session:
        client = GraphQLClient(
        endpoint="https://api.github.com/graphql",
        headers={"Authorization": f"Bearer {os.getenv('GithubPAT')}"},
        session=session
        )
        request = GraphQLRequest(
        query=f"""
    query {{
    repository(name: "{repo}", owner: "{owner}") {{
        issue(number: {num}) {{
        timelineItems(itemTypes: CLOSED_EVENT, last: 1) {{
            nodes {{
            ... on ClosedEvent {{
                createdAt
                closer {{
                __typename
                ... on PullRequest {{
                    baseRefName
                    url
                    baseRepository {{
                    nameWithOwner
                    }}
                    headRefName
                    headRepository {{
                    nameWithOwner
                    }}
                }}
                }}
            }}s
            }}
        }}
        }}
    }}
    }}
        """
        )
        response = await client.query(request=request)
        if response.status == 200:
            return response.json()
        else:
            return None
    
async def closing_pr():
    data = 
    if data["repository"]["issue"]["timelineItems"]["nodes"][0]["closer"]:
        if data["repository"]["issue"]["timelineItems"]["nodes"][0]["closer"]["__typename"] == "PullRequest":
            return data["repository"]["issue"]["timelineItems"]["nodes"][0]["closer"]["url"]
        else: 
            return None