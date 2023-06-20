class PrEventHandler:
    def __init__(self) -> None:
        return
    
    def handleEvent(self, eventData):
        #pr Raised
        if eventData["action"] in ['assigned', 'edited', 'labeled', 'opened', 'ready_for_review', 'reopened', 'review_requested', 'unlocked']:
            return
        

        if eventData["action"] in ['closed']:
            #merged
            #abandoned
        #pr abandoned



        #prMerged corresponds to a close

        #pr Reviewed and accepted
        
        
        # assigned, closed, converted_to_draft, demilestoned, dequeued, edited, enqueued, labeled, locked, milestoned, opened, ready_for_review, reopened, request_review_removed, review_requested, unassigned, unlabeled, unlocked 
        
        return