import re

def parse_pull_request(pull_request_body):
    issue_numbers = []
    for match in re.finditer(r"#(\d+)", pull_request_body):
        if match.group(1) not in issue_numbers:
            issue_numbers.append(match.group(1))
    return issue_numbers


class PrProcessor:
    def __init__(self):
        return
    
    def getLinkedIssues(self, pullRequest):
        linkedIssues = []
        linkedIssues+= parse_pull_request(pullRequest["body"])
        return linkedIssues
