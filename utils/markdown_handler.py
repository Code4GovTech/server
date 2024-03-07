import mistune
import re, sys
import pprint
from fuzzywuzzy import fuzz
import flatdict

#CONSTS
from utils.runtime_vars import MARKDOWN_TEMPLATE_HEADERS
def remove_special_characters(string):
    #ignores '-' and ',' because '-' can be used in github usernames and ',' is needed for comma separated values
    special_characters = re.compile(r"[^a-zA-Z0-9\s,-]")
    return re.sub(special_characters, "", string)


class HeadingRenderer(mistune.Renderer):
    def __init__(self):
        super().__init__()
        self.current_heading = None
        self.current_subheading = None
        self.data = {}
        self.first_class_headers = MARKDOWN_TEMPLATE_HEADERS

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
        #   print(header)
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
        self.headers = MARKDOWN_TEMPLATE_HEADERS
        return
    
    def flattenAndParse(self, rawMarkdown):
        markdown = mistune.Markdown(renderer=HeadingRenderer())
        dummyHeader = "## Header\n\n"
        markdown(dummyHeader+rawMarkdown)
        markdownDict = markdown.renderer.data
        print(markdownDict, file=sys.stderr)
        flatDict = flatdict.FlatDict(markdownDict, delimiter=".")
        # print(flatDict)
        dataDict = {}
        for header in self.headers:
            pattern = fr"(?:^{re.escape(header)}\.text$)|(?:\.{re.escape(header)}\.text$)"
            for key in flatDict.keys():
                if re.search(pattern, key):
                    dataDict[header] = remove_special_characters(flatDict[key])
            if f'{header}.text' in flatDict.keys():
                dataDict[header] = remove_special_characters(flatDict[f'{header}.text'])
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
# test4 ="There are places where a proper code paradigm is not followed, such as dependency injection, and certain places where the components are strongly coupled, making testing them difficult. This ticket tracks all these code changes that are required, individual tickets should be filed for each of these issues. This issue will be a long running thread and will be updated as and when we find code that needs to be cleaned up.\n\n- [x] NewNetcoreService needs to be fetched using dependency injection instead of using getInstance and actually creating an instance using the `new` keyword.\n- [ ] All the services using NetcoreWhatsapp currently manually set some of the fields like FileCdn etc. We need to autoconfigure those.\n- [ ] Currently, the RedisCache change to remove @AllArgsConstructor was rolled back due to null pointer exceptions. We need to pinpoint the point of failure and fix this.\n\n\n### Project\nUCI\n\n\n### Organization Name:\nSamagra\n\n### Domain\nBackend\n\n### Area of governance                          \nCommunications\n\n\n### Tech Skills Needed:\nJava, SpringBoot\n\n### Mentor(s)\n@chinmoy12c \n\n### Complexity\nMedium\n\n### Category\nCode Cleanup\n\n### Sub Category\nAPI, Backend, Technical Debt."
# test2 = '''## Description:\r\nIn order to enhance the maintainability and scalability of the passbook project, it is necessary to refactor the existing [components](https://github.com/Family-ID/passbook/tree/development/apps/passbook/src/components). This issue outlines the tasks involved in refactoring the components and improving the overall codebase.\r\n\r\n## Goals:\r\n\r\n- [ ] Improve code maintainability and readability.\r\n- [ ] Enhance component reusability and modularity.\r\n- [ ] Optimize component performance.\r\n- [ ] Publishing the package of `packages/ui`\r\n- [ ] Implement best practices and coding standards.\r\n- [ ] Ensure reusability.\r\n\r\n \r\n## Expected Outcome:\r\n\r\n- [ ] Simplified and more organized component structure into `packages/ui`.\r\n- [ ] Removal of all the assets and components from the `apps/passbook`.\r\n- [ ] Publishing the package of `packages/ui`\r\n- [ ] Cleaner and more concise codebase.\r\n- [ ] Improved performance and efficiency.\r\n- [ ] Reduced duplication and increased reusability.\r\n- [ ] Adherence to coding standards and best practices.\r\n\r\n\r\n## Acceptance Criteria:\r\n\r\n- [ ] Existing [components](https://github.com/Family-ID/passbook/tree/development/apps/passbook/src/components) are thoroughly reviewed and analyzed.\r\n- [ ] Redundant or unnecessary code is identified and removed.\r\n- [ ] Code is refactored to improve readability and maintainability.\r\n- [ ] Component dependencies are minimized and isolated.\r\n- [ ] Performance optimizations are implemented where applicable.\r\n- [ ] Updated components pass all relevant unit tests.\r\n- [ ] The refactored code is merged into the main branch without breaking existing functionality.\r\n\r\n## Implementation Details:\r\n\r\nThe refactoring process will involve the following tasks:\r\n- [ ] Analyze the existing component structure and identify areas for improvement.\r\n- [ ] Create a detailed plan for refactoring, outlining specific changes and strategies.\r\n- [ ] Refactor individual components, ensuring that the changes do not introduce regressions.\r\n- [ ] Update documentation and comments to reflect the revised component structure.\r\n- [ ] Perform thorough testing to validate the refactored code and ensure its compatibility.\r\n\r\n## Mockups / Wireframes:\r\nhttp://passbook-web.vercel.app/\r\n\r\n## Project\r\nPassbok\r\n\r\n## Domain\r\nSocial Welfare\r\n\r\n## Tech Skills Needed:\r\nNext.js\r\n\r\n## Mentor(s):\r\n@Shruti3004 \r\n\r\n## Complexity\r\nMedium\r\n\r\n## Category\r\nUI/UX\r\n\r\n## Sub Category\r\nRefactoring'''
# test3 = "## Description\r\nDesc\r\n\r\n## Goals\r\n- [ ] [Goal 1]\r\n- [ ] [Goal 2]\r\n- [ ] [Goal 3]\r\n- [ ] [Goal 4]\r\n- [ ] [Goal 5]\r\n\r\n## Expected Outcome\r\n[Describe in detail what the final product or result should look like and how it should behave.]\r\n\r\n## Acceptance Criteria\r\n- [ ] [Criteria 1]\r\n- [ ] [Criteria 2]\r\n- [ ] [Criteria 3]\r\n- [ ] [Criteria 4]\r\n- [ ] [Criteria 5]\r\n\r\n## Implementation Details\r\n[List any technical details about the proposed implementation, including any specific technologies that will be used.]\r\n\r\n## Mockups / Wireframes\r\n[Include links to any visual aids, mockups, wireframes, or diagrams that help illustrate what the final product should look like. This is not always necessary, but can be very helpful in many cases.]\r\n\r\n---\r\n\r\n### Project\r\nProject\r\n\r\n### Organization Name:\r\nOrganisation\r\n\r\n### Domain\r\nE-Governance\r\n\r\n### Tech Skills Needed:\r\nReactJS\r\n\r\n### Mentor(s)\r\n@KDwevedi \r\n\r\n### Complexity\r\nMedium\r\n\r\n### Category\r\nPerformance Improvement\r\n\r\n### Sub Category\r\nAnalytics\r\n"
# print(MarkdownHeaders().flattenAndParse(test4))
# print(fuzz.ratio('Product', 'Product Name'))
# header = "Mentor(s)"
# pattern = fr"(?:^{header}\.text$)|(?:\.{header}\.text$)"
# print(re.match(pattern, 'Mentor(s).text'))