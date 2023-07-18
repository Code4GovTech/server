import aiohttp, os, sys
from utils.db import SupabaseInterface
from aiographql.client import GraphQLClient, GraphQLRequest

headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': f'Bearer {os.getenv("GithubPAT")}'
        }

async def get_closing_pr(repo, owner, num):
    client = GraphQLClient(
    endpoint="https://api.github.com/graphql",
    headers={"Authorization": f"Bearer {os.getenv('GithubPAT')}"},
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
          }}
        }}
      }}
    }}
  }}
}}
    """
    )
    return await client.query(request=request)
    # response = 
    # data = response.data
    # if data["repository"]["issue"]["timelineItems"]["nodes"][0]["closer"]:
    #     if data["repository"]["issue"]["timelineItems"]["nodes"][0]["closer"]["__typename"] == "PullRequest":
    #         return data["repository"]["issue"]["timelineItems"]["nodes"][0]["closer"]["url"]
    #     else: 
    #         return None
    # await client.session.close()

async def get_pull_requests(owner, repo,status, page):
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
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as resp:
            return await resp.json()

async def get_pull_request(owner, repo, number):
    """Gets a pull request from GitHub.

    Args:
        number: The number of the pull request to get.

    Returns:
        The JSON response from GitHub.
    """

    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{number}"
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

# arya-vats/arya-vats
# c4gt-server-c4gt-server-1  | arya-vats/bootstrap-npm-starter
# c4gt-server-c4gt-server-1  | arya-vats/CustomShellScript
# c4gt-server-c4gt-server-1  | arya-vats/DS
# c4gt-server-c4gt-server-1  | arya-vats/Dynamic-Weather-App
# c4gt-server-c4gt-server-1  | arya-vats/ecommerce
# c4gt-server-c4gt-server-1  | arya-vats/electron-quick-start
# c4gt-server-c4gt-server-1  | arya-vats/FileSharing
# c4gt-server-c4gt-server-1  | arya-vats/flutterIntro-myapp
# c4gt-server-c4gt-server-1  | arya-vats/Home-Automation
# c4gt-server-c4gt-server-1  | arya-vats/html
# c4gt-server-c4gt-server-1  | arya-vats/icons
# c4gt-server-c4gt-server-1  | arya-vats/LeetCode-Feedback
# c4gt-server-c4gt-server-1  | arya-vats/news_today
# c4gt-server-c4gt-server-1  | arya-vats/Not-so-complex-react-app
# c4gt-server-c4gt-server-1  | arya-vats/PokeList
# c4gt-server-c4gt-server-1  | arya-vats/ProductHunt
# c4gt-server-c4gt-server-1  | arya-vats/Review-website
# c4gt-server-c4gt-server-1  | arya-vats/sc
# c4gt-server-c4gt-server-1  | arya-vats/Scripts
# c4gt-server-c4gt-server-1  | arya-vats/Smart-India-Hackathon
# c4gt-server-c4gt-server-1  | arya-vats/STC-LANDING
# c4gt-server-c4gt-server-1  | arya-vats/supply-chain-truffle-react
# c4gt-server-c4gt-server-1  | arya-vats/team_phoenix
# c4gt-server-c4gt-server-1  | arya-vats/TwitterClone
# c4gt-server-c4gt-server-1  | arya-vats/UserAuth-Permissions
# c4gt-server-c4gt-server-1  | arya-vats/UserAuthentication
# c4gt-server-c4gt-server-1  | ----RePO-----
# c4gt-server-c4gt-server-1  | dhiway/cord
# c4gt-server-c4gt-server-1  | dhiway/cord.js
# c4gt-server-c4gt-server-1  | ----RePO-----
# c4gt-server-c4gt-server-1  | DevDataPlatform/DDP_backend
# c4gt-server-c4gt-server-1  | DevDataPlatform/prefect-proxy
# c4gt-server-c4gt-server-1  | DevDataPlatform/webapp
# c4gt-server-c4gt-server-1  | ----RePO-----
# c4gt-server-c4gt-server-1  | shikshalokam/Test-Automation-Mobile-app
# c4gt-server-c4gt-server-1  | shikshalokam/Test-Automation-Portal
# c4gt-server-c4gt-server-1  | ----RePO-----
# c4gt-server-c4gt-server-1  | glific/.github
# c4gt-server-c4gt-server-1  | glific/cypress-testing
# c4gt-server-c4gt-server-1  | glific/design-marketing
# c4gt-server-c4gt-server-1  | glific/dg-weather
# c4gt-server-c4gt-server-1  | glific/docs
# c4gt-server-c4gt-server-1  | glific/floweditor
# c4gt-server-c4gt-server-1  | glific/glific
# c4gt-server-c4gt-server-1  | glific/glific-frontend
# c4gt-server-c4gt-server-1  | glific/glific-project
# c4gt-server-c4gt-server-1  | glific/glific-website
# c4gt-server-c4gt-server-1  | glific/k6io
# c4gt-server-c4gt-server-1  | glific/link_preview
# c4gt-server-c4gt-server-1  | glific/mobile
# c4gt-server-c4gt-server-1  | glific/passwordless_auth
# c4gt-server-c4gt-server-1  | glific/phil_columns-ex
# c4gt-server-c4gt-server-1  | glific/pow
# c4gt-server-c4gt-server-1  | glific/recipes
# c4gt-server-c4gt-server-1  | glific/Rmapping
# c4gt-server-c4gt-server-1  | glific/slate
# c4gt-server-c4gt-server-1  | glific/waffle_gcs
# c4gt-server-c4gt-server-1  | [2023-07-17 12:09:04 +0000] [1] [INFO] 140.82.115.95:56553 POST /github/events 1.1 200 25950 768287
# c4gt-server-c4gt-server-1  | ----RePO-----
# c4gt-server-c4gt-server-1  | komalm/advanced-search
# c4gt-server-c4gt-server-1  | komalm/bootstrap-timepicker
# c4gt-server-c4gt-server-1  | komalm/common-consumption-v9-event
# c4gt-server-c4gt-server-1  | komalm/com_activitystream
# c4gt-server-c4gt-server-1  | komalm/com_tjfields
# c4gt-server-c4gt-server-1  | komalm/com_tjqueue
# c4gt-server-c4gt-server-1  | komalm/com_tjreports
# c4gt-server-c4gt-server-1  | komalm/com_tjucm
# c4gt-server-c4gt-server-1  | komalm/emc
# c4gt-server-c4gt-server-1  | komalm/joomla-3x-to-4x-migration-tools
# c4gt-server-c4gt-server-1  | komalm/joomla-cms
# c4gt-server-c4gt-server-1  | komalm/joomla-extensions-generator
# c4gt-server-c4gt-server-1  | komalm/joomla-payments
# c4gt-server-c4gt-server-1  | komalm/knowledge-mw-service
# c4gt-server-c4gt-server-1  | komalm/limo-cloud
# c4gt-server-c4gt-server-1  | komalm/ngx-event-library
# c4gt-server-c4gt-server-1  | komalm/nsdl-event-library
# c4gt-server-c4gt-server-1  | komalm/nulp-portal
# c4gt-server-c4gt-server-1  | komalm/nulp-portal-1
# c4gt-server-c4gt-server-1  | komalm/nulp-tenant
# c4gt-server-c4gt-server-1  | komalm/plg_api_tjreports
# c4gt-server-c4gt-server-1  | komalm/plg_system_sendemail
# c4gt-server-c4gt-server-1  | komalm/sb-events-module
# c4gt-server-c4gt-server-1  | komalm/sunbird-cb-adminportal
# c4gt-server-c4gt-server-1  | komalm/sunbird-cb-orgportal
# c4gt-server-c4gt-server-1  | komalm/sunbird-course-service
# c4gt-server-c4gt-server-1  | komalm/Sunbird-ED-Admin
# c4gt-server-c4gt-server-1  | komalm/sunbird-quml-player
# c4gt-server-c4gt-server-1  | komalm/Sunbird-SaaS-AdminModule
# c4gt-server-c4gt-server-1  | komalm/SunbirdEd-consumption-ngcomponents
# c4gt-server-c4gt-server-1  | ----RePO-----
# c4gt-server-c4gt-server-1  | ChakshuGautam/cQube-ingestion
# c4gt-server-c4gt-server-1  | ----RePO-----
# c4gt-server-c4gt-server-1  | samagra-comms/.github
# c4gt-server-c4gt-server-1  | samagra-comms/adapter
# c4gt-server-c4gt-server-1  | samagra-comms/admin
# c4gt-server-c4gt-server-1  | samagra-comms/api-cache
# c4gt-server-c4gt-server-1  | samagra-comms/benchmark
# c4gt-server-c4gt-server-1  | samagra-comms/broadcast-transformer
# c4gt-server-c4gt-server-1  | samagra-comms/cassandra-docker
# c4gt-server-c4gt-server-1  | samagra-comms/ChatUI
# c4gt-server-c4gt-server-1  | samagra-comms/community
# c4gt-server-c4gt-server-1  | samagra-comms/conf
# c4gt-server-c4gt-server-1  | samagra-comms/dao
# c4gt-server-c4gt-server-1  | samagra-comms/deploy
# c4gt-server-c4gt-server-1  | samagra-comms/diksha-data-export
# c4gt-server-c4gt-server-1  | samagra-comms/docker-deploy
# c4gt-server-c4gt-server-1  | samagra-comms/event-pusher
# c4gt-server-c4gt-server-1  | samagra-comms/fusionauth-gql-service
# c4gt-server-c4gt-server-1  | samagra-comms/generic-transformer
# c4gt-server-c4gt-server-1  | samagra-comms/inbound
# c4gt-server-c4gt-server-1  | samagra-comms/inbound-benchmark
# c4gt-server-c4gt-server-1  | samagra-comms/load-testing
# c4gt-server-c4gt-server-1  | samagra-comms/message-rosa
# c4gt-server-c4gt-server-1  | samagra-comms/odk
# c4gt-server-c4gt-server-1  | samagra-comms/orchestrator
# c4gt-server-c4gt-server-1  | samagra-comms/outbound
# c4gt-server-c4gt-server-1  | samagra-comms/scripts
# c4gt-server-c4gt-server-1  | samagra-comms/signal
# c4gt-server-c4gt-server-1  | samagra-comms/sunbird-analytics-core
# c4gt-server-c4gt-server-1  | samagra-comms/sunbird-bot
# c4gt-server-c4gt-server-1  | samagra-comms/sunbird-core-dataproducts
# c4gt-server-c4gt-server-1  | samagra-comms/sunbird-data-products
# c4gt-server-c4gt-server-1  | ----RePO-----
# c4gt-server-c4gt-server-1  | beckn/agent-tracking-view-app
# c4gt-server-c4gt-server-1  | beckn/BAP-Boilerplate-SDK
# c4gt-server-c4gt-server-1  | beckn/bap-reference-app
# c4gt-server-c4gt-server-1  | beckn/beckn-exp-apis
# c4gt-server-c4gt-server-1  | beckn/beckn-exp-event-collector-apis
# c4gt-server-c4gt-server-1  | beckn/beckn-exp-guide-ui
# c4gt-server-c4gt-server-1  | beckn/beckn-exp-ui
# c4gt-server-c4gt-server-1  | beckn/beckn-in-a-box
# c4gt-server-c4gt-server-1  | beckn/beckn-one
# c4gt-server-c4gt-server-1  | beckn/beckn-one-cms
# c4gt-server-c4gt-server-1  | beckn/beckn-one-community-management-service
# c4gt-server-c4gt-server-1  | beckn/beckn-one-sanbox-service
# c4gt-server-c4gt-server-1  | beckn/beckn-one-sandbox-bpp
# c4gt-server-c4gt-server-1  | beckn/beckn-one-spec-management-service
# c4gt-server-c4gt-server-1  | beckn/beckn-protocol-dtos
# c4gt-server-c4gt-server-1  | beckn/beckn-qr-code-generator
# c4gt-server-c4gt-server-1  | beckn/beckn-sandbox
# c4gt-server-c4gt-server-1  | beckn/beckn-sandbox-webhook
# c4gt-server-c4gt-server-1  | beckn/becknfoundation.org
# c4gt-server-c4gt-server-1  | beckn/becknprotocol.io
# c4gt-server-c4gt-server-1  | beckn/biab-api-gateway
# c4gt-server-c4gt-server-1  | beckn/biab-bap-client
# c4gt-server-c4gt-server-1  | beckn/biab-bap-protocol
# c4gt-server-c4gt-server-1  | beckn/biab-config-engine
# c4gt-server-c4gt-server-1  | beckn/biab-infra
# c4gt-server-c4gt-server-1  | beckn/biab-mongodb
# c4gt-server-c4gt-server-1  | beckn/biab-storefront-ui
# c4gt-server-c4gt-server-1  | beckn/BPP-Boilerplate-SDK
# c4gt-server-c4gt-server-1  | beckn/bpp-mobility
# c4gt-server-c4gt-server-1  | beckn/bpp-retail
# c4gt-server-c4gt-server-1  | ----RePO-----
# c4gt-server-c4gt-server-1  | digilocker-tools/.github
# c4gt-server-c4gt-server-1  | digilocker-tools/docs
# c4gt-server-c4gt-server-1  | digilocker-tools/mock
# c4gt-server-c4gt-server-1  | digilocker-tools/ts-sdk
# c4gt-server-c4gt-server-1  | ----RePO-----
# c4gt-server-c4gt-server-1  | Family-ID/.github
# c4gt-server-c4gt-server-1  | Family-ID/admin
# c4gt-server-c4gt-server-1  | Family-ID/core-service-mock
# c4gt-server-c4gt-server-1  | Family-ID/dashboard-compose-files
# c4gt-server-c4gt-server-1  | Family-ID/deploy
# c4gt-server-c4gt-server-1  | Family-ID/familyid-dashboard
# c4gt-server-c4gt-server-1  | Family-ID/fid-bff
# c4gt-server-c4gt-server-1  | Family-ID/issues
# c4gt-server-c4gt-server-1  | Family-ID/mock-familyid-server
# c4gt-server-c4gt-server-1  | Family-ID/mock-meri-pehchaan
# c4gt-server-c4gt-server-1  | Family-ID/mock-slc-server
# c4gt-server-c4gt-server-1  | Family-ID/passbook-frontend
# c4gt-server-c4gt-server-1  | Family-ID/rcw-bff
# c4gt-server-c4gt-server-1  | Family-ID/superset
# c4gt-server-c4gt-server-1  | Family-ID/tasks
# c4gt-server-c4gt-server-1  | Family-ID/user-service
# c4gt-server-c4gt-server-1  | ----RePO-----
# c4gt-server-c4gt-server-1  | Unified-Learner-Passbook/Credential-MS
# c4gt-server-c4gt-server-1  | ----RePO-----
# c4gt-server-c4gt-server-1  | Code4GovTech/C4GT
# c4gt-server-c4gt-server-1  | Code4GovTech/c4gt-milestones
# c4gt-server-c4gt-server-1  | Code4GovTech/C4GT_22
# c4gt-server-c4gt-server-1  | Code4GovTech/ccbp_projects
# c4gt-server-c4gt-server-1  | Code4GovTech/curtain-raiser
# c4gt-server-c4gt-server-1  | Code4GovTech/devops
# c4gt-server-c4gt-server-1  | Code4GovTech/discord-bot
# c4gt-server-c4gt-server-1  | Code4GovTech/server
# c4gt-server-c4gt-server-1  | Code4GovTech/Test_Repo
# c4gt-server-c4gt-server-1  | Code4GovTech/website
# c4gt-server-c4gt-server-1  | ----RePO-----
# c4gt-server-c4gt-server-1  | ELEVATE-Project/mentorED-Portal
# c4gt-server-c4gt-server-1  | ELEVATE-Project/mentoring-bap-app
# c4gt-server-c4gt-server-1  | ELEVATE-Project/mentoring-bap-catalog-service
# c4gt-server-c4gt-server-1  | ELEVATE-Project/mentoring-bap-service
# c4gt-server-c4gt-server-1  | ELEVATE-Project/mentoring-bpp-app
# c4gt-server-c4gt-server-1  | ELEVATE-Project/mentoring-bpp-catalog-service
# c4gt-server-c4gt-server-1  | ELEVATE-Project/mentoring-mobile-app
# c4gt-server-c4gt-server-1  | ELEVATE-Project/project-frontend
# c4gt-server-c4gt-server-1  | ELEVATE-Project/project-service
# c4gt-server-c4gt-server-1  | ELEVATE-Project/QuML-player
# c4gt-server-c4gt-server-1  | ELEVATE-Project/samiksha-frontend
# c4gt-server-c4gt-server-1  | ELEVATE-Project/samiksha-service
# c4gt-server-c4gt-server-1  | ELEVATE-Project/template-validation-portal
# c4gt-server-c4gt-server-1  | ELEVATE-Project/template-validation-portal-service
# c4gt-server-c4gt-server-1  | ELEVATE-Project/unnati-service
# c4gt-server-c4gt-server-1  | ----RePO-----
# c4gt-server-c4gt-server-1  | vijiurs/ml-projects-service
# c4gt-server-c4gt-server-1  | vijiurs/ml-survey-service
# c4gt-server-c4gt-server-1  | vijiurs/Spoon-Knife


repositories = list(set(mentorship_repos))

tickets = SupabaseInterface().readAll("ccbp_tickets")
closedTickets = []
for ticket in tickets:
      if ticket["status"] == "closed":
            closedTickets.append(ticket)
            
        

async def getNewPRs():
    for ticket in closedTickets:
        components = ticket["url"].split('/')
        print(await get_closing_pr(repo= components[-3], owner=components[-4], num=components[-1]), file=sys.stderr)
    # for repo in repositories:
    #         components = repo.split('/')
    #         owner, repository = components[-2], components[-1]
    #         pulls = []

    #         for i in range(1,10):
    #                 page = await get_pull_requests(owner, repository, 'all', i)
    #                 # print(page)
    #                 if page == []:
    #                         break
    #                 # print(page)
    #                 for pull in page:
    #                         if pull not in pulls:
    #                                 pulls.append(pull)
    #         count = 1
    #         for pr in pulls:
    #                 # print(pr, pulls)
    #                 if isinstance(pr, dict) and pr.get("number"):
    #                         pull = await get_pull_request(owner, repository, pr["number"])
    #                 else: 
    #                     continue
    #                 print(count,'/',len(pulls))
    #                 count+=1
    #                 # break
    #                 try:
    #                         p = {
    #                         "pr_url": pull["url"],
    #                         "pr_id": pull["id"],
    #                         "pr_node_id": pull["node_id"],
    #                         "html_url": pull["html_url"],
    #                         "status": pull["state"],
    #                         "title": pull["title"],
    #                         "raised_by_username": pull["user"]["login"],
    #                         "raised_by_id": pull["user"]["id"],
    #                         "body": pull["body"],
    #                         "created_at": pull["created_at"],
    #                         "updated_at": pull["updated_at"],
    #                         "closed_at": pull["closed_at"],
    #                         "merged_at": pull["merged_at"],
    #                         "assignees": pull["assignees"],
    #                         "requested_reviewers": pull["requested_reviewers"],
    #                         "labels": pull["labels"],
    #                         "review_comments_url": pull["review_comments_url"],
    #                         "comments_url": pull["comments_url"],
    #                         "repository_id": pull["base"]["repo"]["id"],
    #                         "repository_owner_name": pull["base"]["repo"]["owner"]["login"],
    #                         "repository_owner_id": pull["base"]["repo"]["owner"]["id"],
    #                         "repository_url": pull["base"]["repo"]["html_url"],
    #                         "merged_by_username":pull["merged_by"]["login"] if pull.get("merged_by") else None,
    #                         "merged_by_id":pull["merged_by"]["id"] if pull.get("merged_by") else None,
    #                         "merged": pull["merged"] if pull.get("merged") else None,
    #                         "number_of_commits": pull["commits"],
    #                         "number_of_comments": pull["comments"] ,
    #                         "lines_of_code_added": pull["additions"] ,
    #                         "lines_of_code_removed": pull["deletions"] ,
    #                         "number_of_files_changed": pull["changed_files"] 

    #                 }
    #                         SupabaseInterface().insert("mentorship_program_pull_request", p)
    #                 except Exception as e:
    #                     print("Exception", e, file=sys.stderr)
    #                     break
