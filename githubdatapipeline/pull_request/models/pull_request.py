pullRequestSchema = {
    "url": "API endpoint url for the pull request",
    "id": "PR id",
    "node_id": "graphql object node id",
    "html_url": "url for the html webpage of the pull request",
    "diff_url": "API endpoint url for the diff json object",
    "user": {
        "login": "user profile name who raised pr",
        "id": "user id that raised PR",
        "node_id": "graphql node id for user object",
        "url": "API endpoint for user that raised PR"
    },
    "body": "contents of the pull request",
    "created_at": "date created",
    "updated_at": "date_updated",
    "closed_at": "date closed",
    "merged_at": "date merged",
    "assignees": "assigned github users if any",
    "requested_reviewers": "requested reviewers if any",
    "labels": "labels if any",
    "draft": "True if draft PR",
    "commits_url": "API endpoint url for commits",
    "review_comments_url": "API endpoint url for review comments",
    "comments_url": "API endpoint url for comments",
    "head": {
        "label": "branch name",
        "user": {
            "login": "user that created the branch",
            "id": "user id for user that created the branch",
            "node_id": ""
        },
        "repo": {
            "id": "repository id",
            "node_id": "repository graphql object node id",
            "name": "repo name",
            "full_name": "owner/repo",
            "owner": {
                "login": "repository owner",
                "id": "repo owner id",
                "node_id": "repo owner graphql node id"
            },
            "description": "repository description",
            "url": "api endpoint url for repo"
            
        },
        "base": "base branch info",
        "merged": "True if merged",
        "merged_by": "username if merged",
        "comments": "no. of comments",
        "review_comments": "no. of review comments",
        "commits": "no. of commits",
        "additions":"LoC added",
        "deletions":"LoC removed",
        "changed_files": "no. of files changed"
    }

}
def pullRequestDataValidator(data):
    if data.keys() == pullRequestSchema.keys():
        return True
    else:
        return False




class PullRequest:
    def __init__(self, data=None, url=None, nodeId = None):
        if data:
            self.data = data
    
    @classmethod
    def fromDict(cls, data):
        return cls(data=data)
                
                