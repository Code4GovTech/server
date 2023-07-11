import aiohttp, os
headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': f'Bearer {os.getenv("GithubPAT")}'
        }
async def get_pull_requests(self, status, page):
    """Gets pull requests from GitHub.

    Args:
        status: The status of the pull requests to get.
        page: The page of pull requests to get.

    Returns:
        The JSON response from GitHub.
    """

    params = {
        "state": status,
        "per_page": 100,
        "page": page,
        "created": "2023-07-01T01:01:01Z"
    }
    url = f"https://api.github.com/repos/{self.owner}/{self.repo}/pulls"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as resp:
            return await resp.json()

async def get_pull_request(self, number):
    """Gets a pull request from GitHub.

    Args:
        number: The number of the pull request to get.

    Returns:
        The JSON response from GitHub.
    """

    url = f"https://api.github.com/repos/{self.owner}/{self.repo}/pulls/{number}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            return await resp.json()

mentorship_repos = [
    "https://github.com/kiranma72/loinc-india",
    "https://github.com/atulai-sg/abdm-sdk",
    "https://github.com/atulai-sg/abdm-sdk",
    "https://github.com/atulai-sg/abdm-sdk",
    "https://github.com/atulai-sg/abdm-sdk",
    "https://github.com/Samagra-Development/ai-tools",
    "https://github.com/Samagra-Development/ai-tools",
    "https://github.com/Samagra-Development/ai-tools",
    "https://github.com/Samagra-Development/ai-tools",
    "https://github.com/avniproject/avni-product",
    "https://github.com/Bahmni/connect2Bahmni",
    "https://github.com/Bahmni/openmrs-module-bahmniapps",
    "https://github.com/Bahmni/openmrs-module-bahmniapps",
    "https://github.com/beckn/mobility",
    "https://github.com/beckn/energy",
    "https://github.com/beckn/online-dispute-resolution",
    "https://github.com/dhp-project/DHP-Specs",
    "https://github.com/beckn/synapse",
    "https://github.com/beckn/policy-admin-api",
    "https://github.com/beckn/reputation-infra",
    "https://github.com/beckn/beckn-qr-code-generator",
    "https://github.com/beckn/beckn-in-a-box",
    "https://github.com/beckn/certification-suite",
    "https://github.com/beckn/BAP-Boilerplate-SDK",
    "https://github.com/beckn/BPP-Boilerplate-SDK",
    "https://github.com/ELEVATE-Project/mentoring-bap-service",
    "https://github.com/coronasafe/care_fe",
    "https://github.com/coronasafe/care_fe",
    "https://github.com/coronasafe/care_fe",
    "https://github.com/coronasafe/care_fe",
    "https://github.com/coronasafe/care_fe",
    "https://github.com/dhiway/cord",
    "https://github.com/Sunbird-cQube/cQubeChat",
    "https://github.com/ChakshuGautam/cQube-POCs",
    "https://github.com/Sunbird-cQube/InputFileValidator",
    "https://github.com/DevDataPlatform/platform_infra",
    "https://github.com/DevDataPlatform/airbyte",
    "https://github.com/Samagra-Development/samagra-devops",
    "https://github.com/egovernments/Digit-Core",
    "https://github.com/egovernments/Digit-Core",
    "https://github.com/egovernments/Digit-Core",
    "https://github.com/egovernments/Digit-Core",
    "https://github.com/project-anuvaad/anuvaad",
    "https://github.com/Samagra-Development/Doc-Generator",
    "https://github.com/Samagra-Development/Doc-Generator",
    "https://github.com/Samagra-Development/Doc-Generator",
    "https://github.com/digitalgreenorg/farmstack-c4gt",
    "https://github.com/digitalgreenorg/farmstack-c4gt",
    "https://github.com/glific/mobile",
    "https://github.com/glific/glific",
    "https://github.com/glific/glific",
    "https://github.com/Swasth-Digital-Health-Foundation/integration-sdks",
    "https://github.com/Swasth-Digital-Health-Foundation/integration-sdks",
    "https://github.com/Samagra-Development/odk-collect-extension",
    "https://github.com/Samagra-Development/odk-collect-extension",
    "https://github.com/avantifellows/quiz-creator",
    "https://github.com/Sunbird-inQuiry/player",
    "https://github.com/reapbenefit/voice_to_text",
    "https://github.com/project-sunbird/sunbird-devops",
    "https://github.com/Sunbird-Ed/SunbirdEd-portal",
    "https://github.com/Sunbird-Ed/SunbirdEd-portal",
    "https://github.com/Sunbird-Ed/SunbirdEd-portal",
    "https://github.com/Sunbird-Ed/SunbirdEd-portal",
    "https://github.com/Sunbird-Ed/SunbirdEd-portal",
    "https://github.com/Sunbird-Ed/SunbirdEd-portal",
    "https://github.com/Sunbird-inQuiry/player",
    "https://github.com/Sunbird-inQuiry/editor",
    "https://github.com/Sunbird-inQuiry/editor",
    "https://github.com/Sunbird-inQuiry/editor",
    "https://github.com/Sunbird-Knowlg/knowledge-platform",
    "https://github.com/Sunbird-Knowlg/knowledge-platform",
    "https://github.com/Sunbird-Knowlg/knowledge-platform",
    "https://github.com/Sunbird-Lern/sunbird-course-service",
    "https://github.com/Sunbird-Lern/sunbird-lms-service",
    "https://github.com/Sunbird-Lern/sunbird-lms-service",
    "https://github.com/Sunbird-Obsrv/obsrv-core",
    "https://github.com/Sunbird-Obsrv/obsrv-core",
    "https://github.com/Sunbird-Obsrv/obsrv-core",
    "https://github.com/Sunbird-RC/community",
    "https://github.com/Sunbird-RC/community",
    "https://github.com/Sunbird-Saral/Project-Saral",
    "https://github.com/samagra-comms/inbound",
    "https://github.com/samagra-comms/uci-apis",
    "https://github.com/samagra-comms/uci-web-channel",
    "https://github.com/samagra-comms/uci-web-channel",
    "https://github.com/ELEVATE-Project/template-validation-portal",
    "https://github.com/Samagra-Development/Text2SQL",
    "https://github.com/nachiketa07/C4GT2023-project-setup",
    "https://github.com/nachiketa07/C4GT2023-project-setup",
    "https://github.com/ELEVATE-Project/project-frontend",
    "https://github.com/Samagra-Development/WarpSQL",
    "https://github.com/Samagra-Development/workflow",
    "https://github.com/Samagra-Development/yaus"
]


repositories = list(set(mentorship_repos))

for repo in repositories:
        pulls = []

        for i in range(1,10):
                page = await get_pull_requests('all', i)
                # print(page)
                if page == []:
                        break
                # print(page)
                for pull in page:
                        if pull not in pulls:
                                pulls.append(pull)
        count = 1
        for pr in pulls:
                # print(pr, pulls)
                if isinstance(pr, dict) and pr.get("number"):
                        pull = client.get_pull_request(pr["number"])
                else: 
                      continue
                print(count,'/',len(pulls))
                count+=1
                # break
                try:
                        p = {
                        "pr_url": pull["url"],
                        "pr_id": pull["id"],
                        "pr_node_id": pull["node_id"],
                        "html_url": pull["html_url"],
                        "status": pull["state"],
                        "title": pull["title"],
                        "raised_by_username": pull["user"]["login"],
                        "raised_by_id": pull["user"]["id"],
                        "body": pull["body"],
                        "created_at": pull["created_at"],
                        "updated_at": pull["updated_at"],
                        "closed_at": pull["closed_at"],
                        "merged_at": pull["merged_at"],
                        "assignees": pull["assignees"],
                        "requested_reviewers": pull["requested_reviewers"],
                        "labels": pull["labels"],
                        "review_comments_url": pull["review_comments_url"],
                        "comments_url": pull["comments_url"],
                        "repository_id": pull["base"]["repo"]["id"],
                        "repository_owner_name": pull["base"]["repo"]["owner"]["login"],
                        "repository_owner_id": pull["base"]["repo"]["owner"]["id"],
                        "repository_url": pull["base"]["repo"]["html_url"],
                        "merged_by_username":pull["merged_by"]["login"] if pull.get("merged_by") else None,
                        "merged_by_id":pull["merged_by"]["id"] if pull.get("merged_by") else None,
                        "merged": pull["merged"] if pull.get("merged") else None,
                        "number_of_commits": pull["commits"],
                        "number_of_comments": pull["comments"] ,
                        "lines_of_code_added": pull["additions"] ,
                        "lines_of_code_removed": pull["deletions"] ,
                        "number_of_files_changed": pull["changed_files"] 

                }
                        supa.table("community_program_pull_request").insert([p]).execute()
                except Exception as e:
                      print("Exception", e)
                      continue
