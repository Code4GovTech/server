'''
EXPECTED WEBHOOK CONTENTS
    Insert Response: {'type': 'INSERT', 'table': 'github_profile_data', 'record': {'id': 1042682119035568178, 'rank': 1, 'points': 20, 'prs_merged': 0, 'prs_raised': 0, 'prs_reviewed': 1}, 'schema': 'public', 'old_record': None}
    Update Response: {'type': 'UPDATE', 'table': 'github_profile_data', 'record': {'id': 1042682119035568178, 'rank': 2, 'points': 20, 'prs_merged': 0, 'prs_raised': 0, 'prs_reviewed': 1}, 'schema': 'public', 'old_record': {'id': 1042682119035568178, 'rank': 1, 'points': 20, 'prs_merged': 0, 'prs_raised': 0, 'prs_reviewed': 1}}
    Delete Response {'type': 'DELETE', 'table': 'github_profile_data', 'record': None, 'schema': 'public', 'old_record': {'id': 1, 'rank': 2, 'points': 30, 'prs_merged': 1, 'prs_raised': 2, 'prs_reviewed': 1}}
'''
from utils.db import SupabaseInterface
import cv2 
import numpy as np

class GithubProfileDisplay:
    def __init__(self):
        self.levelOneTemplate = "EnthusiastBadgeTemplate.jpg"
        self.levelTwoTemplate = "RisingStarBadgeTemplate.jpg"
        self.storageBucket = "c4gt-github-profile"
        self.supabase = SupabaseInterface()
    def getDisplayTemplate(self, level):
        template = None
        if level == 1:
            template = self.supabase.client.storage.from_(self.storageBucket).download(self.levelOneTemplate)
        elif level == 2:
            template = self.supabase.client.storage.from_(self.storageBucket).download(self.levelTwoTemplate)
        elif level == 3:
            template = self.supabase.client.storage.from_(self.storageBucket).download(self.levelTwoTemplate)
        else:
            raise Exception("Badge of this rank isn't currently available")
        return template

    def getDisplay(self, profile_data):
        templateAsBuffer = self.getDisplayTemplate(profile_data["rank"])
        templateAsNpArr = np.frombuffer(templateAsBuffer, np.uint8)
        image = cv2.imdecode(templateAsNpArr, cv2.IMREAD_COLOR)
        width, height = image.shape[:2]

        #text coordinates for the templates
        BADGE_RANK_COORDINATES = (1600, height - 1525)
        PRS_RAISED_COORDINATES = (1600, height - 1425)
        PRS_REVIEWED_COORDINATES = (1600, height - 1310)
        PRS_MERGED_COORDINATES = (1600, height - 1195)
        DPG_POINTS_COORDINATES = (1600, height - 1072)

        # Define the text to be added
        badgeRank = str(profile_data["rank"])
        prsRaised = str(profile_data["prs_raised"])
        prsReviewed = str(profile_data["prs_reviewed"])
        prsMerged = str(profile_data["prs_merged"])
        dpgPoints = str(profile_data["points"])

        font = cv2.FONT_HERSHEY_SIMPLEX
        font_size = 1.7
        color = (255, 255, 255) #White
        thickness = 2

        cv2.putText(image, badgeRank, BADGE_RANK_COORDINATES, font, font_size, color, thickness)
        cv2.putText(image, prsRaised, PRS_RAISED_COORDINATES, font, font_size, color, thickness)
        cv2.putText(image, prsReviewed, PRS_REVIEWED_COORDINATES, font, font_size, color, thickness)
        cv2.putText(image, prsMerged, PRS_MERGED_COORDINATES, font, font_size, color, thickness)
        cv2.putText(image, dpgPoints, DPG_POINTS_COORDINATES, font, font_size, color, thickness)

        image_bytes = cv2.imencode(".jpg", image)[1].tobytes()

        return image_bytes

    def update(self, data):
        for profileData in data:
            filename = f'{profileData["discord_id"]}githubdisplay.jpg'
            display = self.getDisplay(profileData)
            try:
                self.supabase.client.storage.from_(self.storageBucket).remove(filename)
            except Exception:
                pass
            self.supabase.client.storage.from_(self.storageBucket).upload(filename, display, {"content-type": "image/jpeg"})
        return True

