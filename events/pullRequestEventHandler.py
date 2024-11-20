class PrEventHandler:
    def __init__(self) -> None:
        pass
    
    def handleEvent(self, eventData):
        # Check if the action is one of the events to be ignored
        if eventData["action"] in ['assigned', 'edited', 'labeled', 'opened', 'ready_for_review', 'reopened', 'review_requested', 'unlocked']:
            return

        # If the action is 'closed'
        if eventData["action"] == 'closed':
            if eventData["merged"]:
                # Action for merged PRs
                self.handleMerged(eventData)
            else:
                # Action for closed but not merged (abandoned) PRs
                self.handleAbandoned(eventData)

    def handleMerged(self, eventData):
        # Action for merged PRs
        print("PR Merged:", eventData["pull_request"]["title"])

    def handleAbandoned(self, eventData):
        # Action for abandoned PRs (closed but not merged)
        print("PR Abandoned:", eventData["pull_request"]["title"])
