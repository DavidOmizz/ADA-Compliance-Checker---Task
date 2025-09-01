from django.test import TestCase

# Create your tests here.
from .utils import check_document


# class UtilsTest(TestCase):
#     def test_basic(self):
#         # html = '<html><head><title></title></head><body><h1 style="color: #0f0; background-color: #0f0">Hi</h1></body></html>'
#         html = '''
#             <html>
#                 <head></head>
#                 <body>
#                     <h1 style="color: lightgreen; background-color: green;">Welcome</h1>
#                     <a href="/more">click here</a>
#                 </body>
#             </html>
#         '''
#         issues = check_document(html)
#         self.assertTrue(any(i['ruleId']=='DOC_TITLE_MISSING' for i in issues))


class UtilsTest(TestCase):
    def test_missing_lang(self):
        html = "<html><head><title>Test</title></head><body></body></html>"
        issues = check_document(html)
        self.assertTrue(any(i['ruleId']=='DOC_LANG_MISSING' for i in issues))

    def test_missing_img_alt(self):
        html = "<html><head><title>Test</title></head><body><img src='logo.png'></body></html>"
        issues = check_document(html)
        self.assertTrue(any(i['ruleId']=='IMG_ALT_MISSING' for i in issues))

    def test_generic_link(self):
        html = "<html><head><title>Test</title></head><body><a href='/'>click here</a></body></html>"
        issues = check_document(html)
        self.assertTrue(any(i['ruleId']=='LINK_GENERIC_TEXT' for i in issues))

    def test_contrast(self):
        # html ='''
        # <html><head><title>Test</title></head>
        #           <body><h1 style='color: lightgray; background-color: green;'>Hello</h1></body></html>
        # '''
        html = """
            <html>
            <head><title>Test</title></head>
            <body>
                <h1 style="color: orange; background-color: green;">Hello</h1>
            </body>
            </html>
            """
        issues = check_document(html)
        self.assertTrue(any(i['ruleId']=='COLOR_CONTRAST' for i in issues))
