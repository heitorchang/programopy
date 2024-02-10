# Convert files in raw/ to this directory
# Run:
# python3 convert_markup.py

"""
The format is:
$tagname This entire line gets wrapped in a tag with the tagname

@py
Python code
More code
@endpy
"""
import time

from chapter_template import HEADER, FOOTER


def replace_html_special_chars(line):
    line = line.replace("<<<", "&lt;&lt;&lt;")
    line = line.replace(">>>", "&gt;&gt;&gt;")
    line = line.replace(" < ", " &lt; ")
    line = line.replace(" > ", " &gt; ")
    line = line.replace(" & ", " &amp; ")

    return line


def tagify(line):
    """Wrap the line inside a tag with the given tagname.
    $tagname My content
    => <tagname>My content</tagname>
    """
    if line[0] == '$':
        tagname, *rest = line.split()
        tagname = tagname[1:]  # remove initial $
        return f"<{tagname}>{' '.join(rest)}</{tagname}>"
    raise ValueError("Line must start with $ to tagify it.")


def generate_time_based_id():
    time.sleep(0.1)
    return str(time.time()).replace(".", "")


def wrap_py_block(lines):
    textarea_id = generate_time_based_id()
    textarea_contents = ''
    textarea_contents += f'''<p><textarea id="{textarea_id}">'''
    for line in lines:
        textarea_contents += line
    textarea_contents = textarea_contents[:-1]  # remove final newline
    textarea_contents += f'''</textarea>\n<button onclick="sendTextarea('{textarea_id}', true)">Avalie</button></p>'''

    return textarea_contents


def generate_chapter_links(current_chapter):
    prev_chapter = current_chapter - 1
    next_chapter = current_chapter + 1

    # get chapter titles
    prev_name = ''
    prev_link = ''
    try:
        with open(f"raw/cap{prev_chapter}.txt") as prev_f:
            for line in prev_f:
                prev_name = ' '.join(line.split()[1:])
                break
    except:
        pass

    next_name = ''
    next_link = ''
    try:
        with open(f"raw/cap{next_chapter}.txt") as next_f:
            for line in next_f:
                next_name = ' '.join(line.split()[1:])
                break
    except:
        pass

    if prev_name:
        prev_link = f'''
            <td class="prev-ch-link">
              <a href="cap{prev_chapter}.html"> &lt;&lt;&lt; {prev_name}</a>
            </td>
        '''

    if next_name:
        next_link = f'''
            <td class="next-ch-link">
              <a href="cap{next_chapter}.html">{next_name} &gt;&gt;&gt; </a>
            </td>
        '''

    return f'''
        <table class="ch-links">
          <tr>
            {prev_link}
            {next_link}
          </tr>
        </table>
    '''

def convert_raw(raw_filename):
    print("Converting raw file", raw_filename)
    filename_only = raw_filename.split('/')[-1].replace('.txt', '.html')
    chapter_number = int(filename_only[3:filename_only.find('.')])
    chapter_links = generate_chapter_links(chapter_number)
    in_py_block = False
    py_block = []
    with open(raw_filename) as raw_file, open(filename_only, 'w') as converted_file:
        print(HEADER, file=converted_file)
        print(chapter_links, file=converted_file)
        for raw_line in raw_file:
            if raw_line[0] == '$':
                print(tagify(raw_line), file=converted_file)
                print(file=converted_file)
            elif raw_line.startswith("@py"):
                in_py_block = True
            elif raw_line.startswith("@endpy"):
                print(wrap_py_block(py_block), file=converted_file)
                py_block = []
                in_py_block = False
            elif in_py_block:
                py_block.append(raw_line)
        print(chapter_links, file=converted_file)
        print(FOOTER, file=converted_file)

if __name__ == '__main__':
    convert_raw('raw/cap0.txt')
    convert_raw('raw/cap1.txt')
