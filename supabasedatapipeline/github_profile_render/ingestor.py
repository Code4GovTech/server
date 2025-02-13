'''
EXPECTED WEBHOOK CONTENTS
    Insert Response: {'type': 'INSERT', 'table': 'github_profile_data', 'record': {'id': 1042682119035568178, 'rank': 1, 'points': 20, 'prs_merged': 0, 'prs_raised': 0, 'prs_reviewed': 1}, 'schema': 'public', 'old_record': None}
    Update Response: {'type': 'UPDATE', 'table': 'github_profile_data', 'record': {'id': 1042682119035568178, 'rank': 2, 'points': 20, 'prs_merged': 0, 'prs_raised': 0, 'prs_reviewed': 1}, 'schema': 'public', 'old_record': {'id': 1042682119035568178, 'rank': 1, 'points': 20, 'prs_merged': 0, 'prs_raised': 0, 'prs_reviewed': 1}}
    Delete Response {'type': 'DELETE', 'table': 'github_profile_data', 'record': None, 'schema': 'public', 'old_record': {'id': 1, 'rank': 2, 'points': 30, 'prs_merged': 1, 'prs_raised': 2, 'prs_reviewed': 1}}
'''
from utils.db import SupabaseInterface
import cv2 
import numpy as np
import segno,os
from io import BytesIO
from dotenv import load_dotenv

class GithubProfileDisplay:
    def __init__(self):
        self.levelOneTemplate = "EnthusiastBadgeTemplate.jpg"
        self.levelTwoTemplate = "RisingStarBadgeTemplate.jpg"
        self.storageBucket = "c4gt-github-profile"
        self.supabase = SupabaseInterface.get_instance()
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
        dpgPoints = str(profile_data["dpg_points"])

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
            print(profileData["github_username"])
            filename = f'{profileData["discord_id"]}githubdisplay.jpg'
            verifiedFileName = f'{profileData["github_username"]}-c4gt-contributions.jpeg'
            display,verified = self.save_image(profileData)
            if display != None:
                try:
                    self.supabase.client.storage.from_(self.storageBucket).remove(filename)
                    self.supabase.client.storage.from_("c4gt-github-profile").remove(verifiedFileName)

                except Exception:
                    pass

                self.supabase.client.storage.from_(self.storageBucket).upload(filename, display, {"content-type": "image/jpeg"})
                self.supabase.client.storage.from_("c4gt-github-profile").upload(verifiedFileName, verified, {"content-type": "image/jpeg"})
        
        return True
    
    

    def generateQR(self,border_size=1, ghUsername=''):
        load_dotenv()
        qr = segno.make_qr(f"https://github-app.{os.getenv('HOST')}/verify/{ghUsername}")
        buffer = BytesIO()
        # Save the QR code to a buffer, adjusting the border size here
        qr.save(buffer, kind='png', scale=1, border=border_size)
        qrBytes = buffer.getvalue()
        return qrBytes

    
    def save_image(self,data):
        try:           
            if data["dpg_points"]+data["classroom_points"]<10:
                return None,None

            #SET DATA
            milestone = data["milestone"]
            prsRaised = data["prs_raised"]
            prsReviewed = data["prs_reviewed"]
            prsMerged = data["prs_merged"]
            dpgPoints = data["dpg_points"]+data["classroom_points"]
            githubUsername = data["github_username"]

            githubLogoBytes = self.supabase.client.storage.from_('github_profile_assets').download("GHLogoSS.png")
            githubLogo_np = np.frombuffer(githubLogoBytes, np.uint8)
            githubLogo = cv2.imdecode(githubLogo_np, cv2.IMREAD_COLOR)

            qrBytes = self.generateQR(1, githubUsername)
            qr_np = np.frombuffer(qrBytes, np.uint8)
            qr =  cv2.imdecode(qr_np, cv2.IMREAD_COLOR)

            textDimensions = cv2.getTextSize(githubUsername, cv2.FONT_HERSHEY_DUPLEX, 1.5, 2)
            usernameWidth = textDimensions[0][0]
            xCenter = 550

            if githubUsername == "Shruti3004":
                return None,None

            #GET TEMPLATES
            if milestone == 1:
                badgeName = 'Bronze'
            elif milestone == 2:
                badgeName = 'Silver'
            elif milestone == 3:
                badgeName = 'Gold'
            else:
                print("WEIRD MILESTONE",milestone)
                print(githubUsername)
                
            displayTemplateName = f'Github Profile Template {badgeName} Display.png'
            verifiedTemplateName = f'Github Profile Template {badgeName} Verified.png'


            displayTemplateBytes = self.supabase.client.storage.from_('github_profile_assets').download(displayTemplateName)
            displayTemplate_np = np.frombuffer(displayTemplateBytes, np.uint8)
            displayTemplate = cv2.imdecode(displayTemplate_np, cv2.IMREAD_COLOR)

            width, height = displayTemplate.shape[:2]

            MILESTONES_COUNT_COORDINATES = (800, height - 673)
            PRS_RAISED_COORDINATES = (800, height - 608)
            PRS_REVIEWED_COORDINATES = (800, height - 546)
            PRS_MERGED_COORDINATES = (800, height - 483)
            DPG_POINTS_COORDINATES = (800, height - 418)
            QR_COORDINATES = (855, height - 620)
            GITHUB_USERNAME = (xCenter - usernameWidth//2, height - 792)
            GITHUB_LOGO_COORDINATES = (GITHUB_USERNAME[0] - 90, height - 850)

            ghScaleFactor = 0.08
            newGHSize = (int(displayTemplate.shape[1] * ghScaleFactor), int(displayTemplate.shape[1] * ghScaleFactor))
            ghResized = cv2.resize(githubLogo, newGHSize, interpolation=cv2.INTER_AREA)
            displayTemplate[GITHUB_LOGO_COORDINATES[1]:GITHUB_LOGO_COORDINATES[1]+ghResized.shape[0], GITHUB_LOGO_COORDINATES[0]:GITHUB_LOGO_COORDINATES[0]+ghResized.shape[1]] = ghResized

            scaleFactor = 0.107
            newSize = (int(displayTemplate.shape[1] * scaleFactor), int(displayTemplate.shape[1] * scaleFactor))
            qrResized = cv2.resize(qr, newSize, interpolation=cv2.INTER_AREA)
            displayTemplate[QR_COORDINATES[1]:QR_COORDINATES[1]+qrResized.shape[0], QR_COORDINATES[0]:QR_COORDINATES[0]+qrResized.shape[1]] = qrResized



            font = cv2.FONT_HERSHEY_SIMPLEX
            font_size = 1.0
            color = (255, 255, 255)
            thickness = 2

            cv2.putText(displayTemplate, str(milestone), MILESTONES_COUNT_COORDINATES, font, font_size, color, thickness)
            cv2.putText(displayTemplate, str(prsRaised), PRS_RAISED_COORDINATES, font, font_size, color, thickness)
            cv2.putText(displayTemplate, str(prsReviewed), PRS_REVIEWED_COORDINATES, font, font_size, color, thickness)
            cv2.putText(displayTemplate, str(prsMerged), PRS_MERGED_COORDINATES, font, font_size, color, thickness)
            cv2.putText(displayTemplate, str(dpgPoints), DPG_POINTS_COORDINATES, font, font_size, color, thickness)
            cv2.putText(displayTemplate, f"@{githubUsername}", GITHUB_USERNAME, cv2.FONT_HERSHEY_DUPLEX, 1.5, (216,216,216), thickness)

            verifiedTemplateBytes = self.supabase.client.storage.from_('github_profile_assets').download(verifiedTemplateName)
            verifiedTemplate_np = np.frombuffer(verifiedTemplateBytes, np.uint8)
            verifiedTemplate = cv2.imdecode(verifiedTemplate_np, cv2.IMREAD_COLOR)

            width, height = verifiedTemplate.shape[:2]

            MILESTONES_COUNT_COORDINATES = (800, height - 673)
            PRS_RAISED_COORDINATES = (800, height - 608)
            PRS_REVIEWED_COORDINATES = (800, height - 546)
            PRS_MERGED_COORDINATES = (800, height - 483)
            DPG_POINTS_COORDINATES = (800, height - 418)
            QR_COORDINATES = (855, height - 620)
            GITHUB_USERNAME = (xCenter - usernameWidth//2, height - 792)
            GITHUB_LOGO_COORDINATES = (GITHUB_USERNAME[0] - 90, height - 850)

            ghScaleFactor = 0.08
            newGHSize = (int(verifiedTemplate.shape[1] * ghScaleFactor), int(verifiedTemplate.shape[1] * ghScaleFactor))
            ghResized = cv2.resize(githubLogo, newGHSize, interpolation=cv2.INTER_AREA)
            verifiedTemplate[GITHUB_LOGO_COORDINATES[1]:GITHUB_LOGO_COORDINATES[1]+ghResized.shape[0], GITHUB_LOGO_COORDINATES[0]:GITHUB_LOGO_COORDINATES[0]+ghResized.shape[1]] = ghResized

            scaleFactor = 0.107
            newSize = (int(verifiedTemplate.shape[1] * scaleFactor), int(verifiedTemplate.shape[1] * scaleFactor))
            qrResized = cv2.resize(qr, newSize, interpolation=cv2.INTER_AREA)
            verifiedTemplate[QR_COORDINATES[1]:QR_COORDINATES[1]+qrResized.shape[0], QR_COORDINATES[0]:QR_COORDINATES[0]+qrResized.shape[1]] = qrResized


            font = cv2.FONT_HERSHEY_SIMPLEX
            font_size = 1.0
            color = (255, 255, 255)
            thickness = 2

            cv2.putText(verifiedTemplate, str(milestone), MILESTONES_COUNT_COORDINATES, font, font_size, color, thickness)
            cv2.putText(verifiedTemplate, str(prsRaised), PRS_RAISED_COORDINATES, font, font_size, color, thickness)
            cv2.putText(verifiedTemplate, str(prsReviewed), PRS_REVIEWED_COORDINATES, font, font_size, color, thickness)
            cv2.putText(verifiedTemplate, str(prsMerged), PRS_MERGED_COORDINATES, font, font_size, color, thickness)
            cv2.putText(verifiedTemplate, str(dpgPoints), DPG_POINTS_COORDINATES, font, font_size, color, thickness)
            cv2.putText(verifiedTemplate, f"@{githubUsername}", GITHUB_USERNAME, cv2.FONT_HERSHEY_DUPLEX, 1.5, (216,216,216), thickness)

            display = cv2.imencode(".jpg", displayTemplate)[1].tobytes()
            verified = cv2.imencode(".jpg", verifiedTemplate)[1].tobytes()
            displayFilename = f'{data["discord_id"]}-c4gt-contributions.jpeg'
            verifiedFileName = f'{githubUsername}-c4gt-contributions.jpeg'
            try:
                self.supabase.client.storage.from_("c4gt-github-profile").remove(displayFilename)
                self.supabase.client.storage.from_("c4gt-github-profile").remove(verifiedFileName)
            except Exception:
                pass
            
            return display,verified
        
        except Exception as e:
            return None,None
        
        

