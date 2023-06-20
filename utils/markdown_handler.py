import mistune
import re
import pprint
from fuzzywuzzy import fuzz
import flatdict

class HeadingRenderer(mistune.Renderer):
    def __init__(self):
        super().__init__()
        self.current_heading = None
        self.current_subheading = None
        self.data = {}
        self.first_class_headers = [
            'Project',
            'Organization Name',
            'Domain',
            'Tech Skills Needed',
            'Mentor(s)',
            'Complexity',
            'Category',
            'Sub Category'
        ]

    def header(self, text, level, raw=None):
        matched_header = self.match_header(text)
        if level == 2:
            self.current_heading = matched_header
            self.data[self.current_heading] = {"text": ""}
            self.current_subheading = None
        elif level == 3 and self.current_heading:
            self.current_subheading = matched_header
            self.data[self.current_heading][self.current_subheading] = {"text": ""}
        return ""

    def match_header(self, text):
      for header in self.first_class_headers:
          if fuzz.token_set_ratio(header.lower(), text.lower()) > 80:
              return header
      return text

    def list_item(self, text):
        if self.current_subheading:
            if not self.data[self.current_heading][self.current_subheading].get('items'):
                self.data[self.current_heading][self.current_subheading]['items'] = []
            self.data[self.current_heading][self.current_subheading]['items'].append(text)
        return ""

    def paragraph(self, text):
        if self.current_heading:
            if self.current_subheading:
                if self.data[self.current_heading][self.current_subheading]["text"]:
                    self.data[self.current_heading][self.current_subheading]["text"] += "\n" + text
                else:
                    self.data[self.current_heading][self.current_subheading]["text"] = text
            else:
                if self.data[self.current_heading]["text"]:
                    self.data[self.current_heading]["text"] += "\n" + text
                else:
                    self.data[self.current_heading]["text"] = text
        return ""

class MarkdownHeaders:
    def __init__(self) -> None:
        self.headers = [
            'Project',
            'Organization Name',
            'Domain',
            'Tech Skills Needed',
            'Mentor(s)',
            'Complexity',
            'Category',
            'Sub Category'
        ]

        return
    
    def flattenAndParse(self, rawMarkdown):
        markdown = mistune.Markdown(renderer=HeadingRenderer())
        markdown(rawMarkdown)
        markdownDict = markdown.renderer.data
        flatDict = flatdict.FlatDict(markdownDict, delimiter=".")
        dataDict = {}
        for header in self.headers:
            pattern = fr".*{header}\.text"
            for key in flatDict.keys():
                if re.match(pattern, key):
                    dataDict[header] = flatDict[key]
        return dataDict

# test = """## Description
# [Provide a brief description of the feature, including why it is needed and what it will accomplish. You can skip any of Goals, Expected Outcome, Implementation Details, Mockups / Wireframes if they are irrelevant]

# ## Goals
# - [ ] [Goal 1]
# - [ ] [Goal 2]
# - [ ] [Goal 3]
# - [ ] [Goal 4]
# - [ ] [Goal 5]

# ## Expected Outcome
# [Describe in detail what the final product or result should look like and how it should behave.]

# ## Acceptance Criteria
# - [ ] [Criteria 1]
# - [ ] [Criteria 2]
# - [ ] [Criteria 3]
# - [ ] [Criteria 4]
# - [ ] [Criteria 5]

# ## Implementation Details
# [List any technical details about the proposed implementation, including any specific technologies that will be used.]

# ## Mockups / Wireframes
# [Include links to any visual aids, mockups, wireframes, or diagrams that help illustrate what the final product should look like. This is not always necessary, but can be very helpful in many cases.]

# ----------------------

# ### Projects
# Test

# ### Organisation Name:
# Samagra

# ### Domains
# Impacct

# ### Tech Skillts Needed:
# React

# ### Mentor(s
# @KDwevedi 

# ### Complexitie
# High

# ### Category
# Security, Deployment

# ### Sub Category
# Database, Support
# """
# print(MarkdownHeaders().flattenAndParse(test))