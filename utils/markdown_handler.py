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
        # print("\n----------header\n",matched_header)
        if level == 2:
            self.current_heading = matched_header
            self.data[self.current_heading] = {"text": ""}
            self.current_subheading = None
        elif level == 3 and self.current_heading:
            self.current_subheading = matched_header
            self.data[self.current_heading][self.current_subheading] = {"text": ""}
        # print("\n--------DATA\n",self.data)
        return ""

    def match_header(self, text):
      for header in self.first_class_headers:
          if fuzz.ratio(header.lower(), text.lower()) > 81:
            #   print(header.lower(),text.lower())
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
                    # print(1, self.current_heading, '|', self.current_subheading, '|', text)
                else:
                    self.data[self.current_heading][self.current_subheading]["text"] = text
                    # print(2, self.current_heading, '|', self.current_subheading, '|', text)
            else:
                if self.data[self.current_heading]["text"]:
                    self.data[self.current_heading]["text"] += "\n" + text
                    # print(3, self.current_heading, '|', self.current_subheading, '|', text)
                else:
                    self.data[self.current_heading]["text"] = text
                    # print(4, self.current_heading, '|', self.current_subheading, '|', text)
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
        # print(markdownDict)
        flatDict = flatdict.FlatDict(markdownDict, delimiter=".")
        print(flatDict)
        dataDict = {}
        for header in self.headers:
            pattern = fr"(?:^{header}\.text$)|(?:\.{header}\.text$)"
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
# test2 = '''## Description:\r\nIn order to enhance the maintainability and scalability of the passbook project, it is necessary to refactor the existing [components](https://github.com/Family-ID/passbook/tree/development/apps/passbook/src/components). This issue outlines the tasks involved in refactoring the components and improving the overall codebase.\r\n\r\n## Goals:\r\n\r\n- [ ] Improve code maintainability and readability.\r\n- [ ] Enhance component reusability and modularity.\r\n- [ ] Optimize component performance.\r\n- [ ] Publishing the package of `packages/ui`\r\n- [ ] Implement best practices and coding standards.\r\n- [ ] Ensure reusability.\r\n\r\n \r\n## Expected Outcome:\r\n\r\n- [ ] Simplified and more organized component structure into `packages/ui`.\r\n- [ ] Removal of all the assets and components from the `apps/passbook`.\r\n- [ ] Publishing the package of `packages/ui`\r\n- [ ] Cleaner and more concise codebase.\r\n- [ ] Improved performance and efficiency.\r\n- [ ] Reduced duplication and increased reusability.\r\n- [ ] Adherence to coding standards and best practices.\r\n\r\n\r\n## Acceptance Criteria:\r\n\r\n- [ ] Existing [components](https://github.com/Family-ID/passbook/tree/development/apps/passbook/src/components) are thoroughly reviewed and analyzed.\r\n- [ ] Redundant or unnecessary code is identified and removed.\r\n- [ ] Code is refactored to improve readability and maintainability.\r\n- [ ] Component dependencies are minimized and isolated.\r\n- [ ] Performance optimizations are implemented where applicable.\r\n- [ ] Updated components pass all relevant unit tests.\r\n- [ ] The refactored code is merged into the main branch without breaking existing functionality.\r\n\r\n## Implementation Details:\r\n\r\nThe refactoring process will involve the following tasks:\r\n- [ ] Analyze the existing component structure and identify areas for improvement.\r\n- [ ] Create a detailed plan for refactoring, outlining specific changes and strategies.\r\n- [ ] Refactor individual components, ensuring that the changes do not introduce regressions.\r\n- [ ] Update documentation and comments to reflect the revised component structure.\r\n- [ ] Perform thorough testing to validate the refactored code and ensure its compatibility.\r\n\r\n## Mockups / Wireframes:\r\nhttp://passbook-web.vercel.app/\r\n\r\n## Project\r\nPassbok\r\n\r\n## Domain\r\nSocial Welfare\r\n\r\n## Tech Skills Needed:\r\nNext.js\r\n\r\n## Mentor(s):\r\n@Shruti3004 \r\n\r\n## Complexity\r\nMedium\r\n\r\n## Category\r\nUI/UX\r\n\r\n## Sub Category\r\nRefactoring'''
# print(MarkdownHeaders().flattenAndParse(test2))
# print(fuzz.ratio('Category', 'Sub Category'))