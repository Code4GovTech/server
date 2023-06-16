import markdown, re

test_md = """
## Description
[Provide a brief description of the feature, including why it is needed and what it will accomplish. You can skip any of Goals, Expected Outcome, Implementation Details, Mockups / Wireframes if they are irrelevant]

## Goals
- [ ] [Goal 1]
- [ ] [Goal 2]
- [ ] [Goal 3]
- [ ] [Goal 4]
- [ ] [Goal 5]

## Expected Outcome
[Describe in detail what the final product or result should look like and how it should behave.]

## Acceptance Criteria
- [ ] [Criteria 1]
- [ ] [Criteria 2]
- [ ] [Criteria 3]
- [ ] [Criteria 4]
- [ ] [Criteria 5]

## Implementation Details
[List any technical details about the proposed implementation, including any specific technologies that will be used.]

## Mockups / Wireframes
[Include links to any visual aids, mockups, wireframes, or diagrams that help illustrate what the final product should look like. This is not always necessary, but can be very helpful in many cases.]

---

### Project
[Project Name]

### Organization Name:
[Organization Name]

### Domain
[Area of governance]

### Tech Skills Needed:
[Required technical skills for the project]

### Mentor(s)
[@Mentor1] [@Mentor2] [@Mentor3]

### Complexity
Pick one of [High]/[Medium]/[Low]

### Category
Pick one or more of [CI/CD], [Integrations], [Performance Improvement], [Security], [UI/UX/Design], [Bug], [Feature], [Documentation], [Deployment], [Test], [PoC]

### Sub Category
Pick one or more of [API], [Database], [Analytics], [Refactoring], [Data Science], [Machine Learning], [Accessibility], [Internationalization], [Localization], [Frontend], [Backend], [Mobile], [SEO], [Configuration], [Deprecation], [Breaking Change], [Maintenance], [Support], [Question], [Technical Debt], [Beginner friendly], [Research], [Reproducible], [Needs Reproduction].


"""

class MarkdownHandler:
    def __init__(self) -> None:
        return
    
    def markdownParser(self, markdown_content):

        #Taking metadata
        markdown_metadata = markdown_content.split('---')[1]

        # Parse Markdown to HTML
        html = markdown.markdown(markdown_metadata)
        # print("-------METADATA----------")

        # Split HTML into sections using heading tags as delimiters
        sections = re.split("</h3>|<h3>", html)
        while '' in sections:
            sections.remove('')
        # print("------SECTIONS---------")
        for section in sections:
            # print(sections, section)
            section.strip()
            section = re.split("<p>|</p>", section)
        # Define regex pattern to match '\n', ':', and any html tags'<>'
            pattern = re.compile(r'[\n]|[:]|<(.*?)>')

        # Remove matching substrings from each string
        clean_sections = [re.sub(pattern, '', s) for s in sections]

        # Initialize dictionary
        markdown_dict = {}
        for i in range(0,len(clean_sections), 2):
            markdown_dict[clean_sections[i]] = clean_sections[i+1]
        return markdown_dict
    
    def markdownMetadataValidator(self, markdown_dict):
        required_headings = ["Project", "Organization Name", "Domain", "Tech Skills Needed", "Mentor(s)", "Complexity", "Category", "Sub Category"]
        missing_headings=[]
        for heading in required_headings:
            if heading not in markdown_dict.keys():
                missing_headings.append(heading)

        print(missing_headings)

        return missing_headings
        

