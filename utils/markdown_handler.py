import markdown, re
import sys


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
        print(markdown_dict,file=sys.stderr)
        for heading in required_headings:
            if heading not in markdown_dict.keys():
                missing_headings.append(heading)

        print(missing_headings,file=sys.stderr)

        return missing_headings
        

