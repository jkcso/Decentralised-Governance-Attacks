import pdfkit

s2 = """
a

b
c
"""

h1 = """<html>
<head></head>
<body><p>"""

h2 = """</p></body>
</html>"""

content = h1 + s2 + h2

f = open('out.html', 'w')
f.write(content)
f.close()

options = {
    'page-size': 'A4',
    'margin-top': '0.75in',
    'margin-right': '0.75in',
    'margin-bottom': '0.75in',
    'margin-left': '0.75in',
    'encoding': 'UTF-8',
    'quiet': ''
}

pdfkit.from_file('out.html', 'out.pdf')
