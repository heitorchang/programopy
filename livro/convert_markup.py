# Convert files in raw/ to this directory

"""
The format is:
#tagname This entire line gets wrapped in a tag with the tagname

@py
Python code
More code
@endpy
"""
import time


def replace_html_special_chars(line):
    line = line.replace(">>>", "&gt;&gt;&gt;")
    line = line.replace(" < ", " &lt; ")
    line = line.replace(" > ", " &gt; ")
    line = line.replace(" & ", " &amp; ")

    return line


def tagify(line):
    """Wrap the line inside a tag with the given tagname.
    #tagname My content
    => <tagname>My content</tagname>
    """
    if line[0] == '#':
        tagname, *rest = line.split()
        tagname = tagname[1:]  # remove initial #
        return f"<{tagname}>{' '.join(rest)}</{tagname}>"
    raise ValueError("Line must start with # to tagify it.")


def generate_time_based_id():
    time.sleep(0.1)
    return str(time.time()).replace(".", "")


def wrap_py_block(lines):
    textarea_id = generate_time_based_id()
    textarea_contents = ''
    textarea_contents += f'''<p><textarea id="{textarea_id}">'''
    for line in lines:
        textarea_contents += line + '\n'
    textarea_contents = textarea_contents[:-1]  # remove final newline
    textarea_contents += f'''</textarea>\n<button onclick="sendTextarea('{textarea_id}')">Avalie</button></p>'''

    return textarea_contents
