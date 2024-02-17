"""
Description:

Place contents of a single line in a specified HTML tag. Without a tag, <p> is assumed:

$h1 My Cool Page

Contents here.

Text inside backticks `some expression` are converted to <code>some expression</code>.

Blocks can be placed in editors, so they can be evaluated:

@
def my_function(x):
    return x * 100
/

A raw HTML block is marked with %

%
<table>
  <tr><td>A</td><td>B</td></tr>
  <tr><td>10</td><td>20</td></tr>
</table>
/
"""

import re


HEADER = '''<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="../css/jquery.terminal.css">
    <link rel="stylesheet" href="../css/codemirror.css">
    <link rel="stylesheet" href="../css/codemirror_ambiance.css">
    <link rel="stylesheet" href="../css/livro.css">
    <link rel="shortcut icon" type="image/x-icon" href="favicon.ico">
    <title>Programo Python</title>
  </head>
  <body>
    <div id="loading">&nbsp;</div>

    <div id="content">
      <div id="chapter">
<p>
  <a href="index.html" class="home-link">Índice</a>
</p>
'''

FOOTER = '''
  <p>
    <a href="index.html" class="home-link">Índice</a>
  </p>
  </div>

  <div id="bottom-padding">&nbsp;</div>

</div>

    <div id="terminal-control" onclick="toggleTerminal()"></div>

    <script src="../js/jquery.min.js"></script>
    <script src="../js/jquery.terminal.js"></script>
    <script src="../js/unix_formatting.js"></script>
    <script src="../js/codemirror.js"></script>
    <script src="../js/codemirror_python.js"></script>
    <script src="../js/matchbrackets.js"></script>

    <script src="../js/init_codemirror.js"></script>
    <script src="../js/init_pyodide.js"></script>
  </body>
</html>
'''


INDEX_TEMPLATE_HEADER = '''
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="../css/livro.css">
    <link rel="shortcut icon" type="image/x-icon" href="/favicon.ico">
    <title>Programo Python</title>
  </head>
  <body>
    <div style="text-align: center;">
    <div style="max-width: 60rem; margin: auto; text-align: left;">

<h1>Programo Python</h1>
<p>
por Heitor Chang
</p>
'''


INDEX_TEMPLATE_FOOTER = '''
<p>
<a href="creditos.html">Créditos</a>
</p>
    </div>
    </div>
  </body>
</html>
'''


def generate_index_chapter_link(n, idx):
    with open(f"raw/{n}.txt") as f:
        for line in f:
            header = line
            break
    n_name = ' '.join(header.split()[1:])

    return f'''
    <p>
      <a href="{n}.html" class="home-chapter-link">{idx}. {n_name}</a>
    </p>
    '''


def generate_index(chapters):
    print(f"Generating index")
    with open(f"index.html", 'w') as index_f:
        print(INDEX_TEMPLATE_HEADER, file=index_f)
        for i, n in enumerate(chapters, 1):
            print(n)
            print(generate_index_chapter_link(n, i), file=index_f)
        print(INDEX_TEMPLATE_FOOTER, file=index_f)


def replace_html_special_chars(line):
    line = line.replace(" <<< ", "&lt;&lt;&lt;")
    line = line.replace(" >>> ", "&gt;&gt;&gt;")
    line = line.replace(" < ", " &lt; ")
    line = line.replace(" > ", " &gt; ")
    line = line.replace(" & ", " &amp; ")
    return line


def convert_line(line, chapter_number):
    if line[0] != '$':
        line = '$p ' + line
    tagname, *rest = line.split()
    tagname = tagname[1:]  # remove initial $
    chapter_label = ""
    if tagname == 'h1':
        chapter_label = str(chapter_number) + '. '
    backtick_template = re.compile(r'`([^`]*?)`')
    contents = replace_html_special_chars(' '.join(rest))
    contents = re.sub(backtick_template, r'<code>\1</code>', contents)
    return f"<{tagname}>{chapter_label}{contents}</{tagname}>"


BLOCK_ID = 0
def generate_incrementing_id():
    global BLOCK_ID
    BLOCK_ID += 1
    return f'block{BLOCK_ID}'


def wrap_py_block(lines):
    textarea_id = generate_incrementing_id()
    textarea_contents = ''
    textarea_contents += f'''<p><textarea id="{textarea_id}">'''
    for line in lines:
        textarea_contents += line
    textarea_contents = textarea_contents[:-1]  # remove final newline
    textarea_contents += f'''</textarea>\n<button onclick="sendTextarea('{textarea_id}', false)">Avalie</button></p>'''

    return textarea_contents


def generate_chapter_links(prev, nxt, idx):
    # get chapter titles
    prev_name = ''
    prev_link = ''
    try:
        with open(f"raw/{prev}.txt") as prev_f:
            for line in prev_f:
                prev_name = ' '.join(line.split()[1:])
                break
    except:
        pass

    next_name = ''
    next_link = ''
    try:
        with open(f"raw/{nxt}.txt") as next_f:
            for line in next_f:
                next_name = ' '.join(line.split()[1:])
                break
    except:
        pass

    if prev_name:
        prev_link = f'''
            <td class="prev-ch-link">
              <a href="{prev}.html"> &lt;&lt;&lt; {idx-1}. {prev_name}</a>
            </td>
        '''

    if next_name:
        next_link = f'''
            <td class="next-ch-link">
              <a href="{nxt}.html">{idx+1}. {next_name} &gt;&gt;&gt; </a>
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


def convert_raw(cur, prev, nxt, idx):
    raw_filename = f'raw/{cur}.txt'
    print("Converting raw file", raw_filename)
    destination_filename = raw_filename.replace('raw/', '').replace('.txt', '.html')
    filename_only = raw_filename.split('/')[-1].replace('.txt', '.html')
    chapter_links = generate_chapter_links(prev, nxt, idx)
    in_py_block = False
    py_block = []

    in_html_block = False
    html_block = []
    with open(raw_filename) as raw_file, open(destination_filename, 'w') as converted_file:
        print(HEADER, file=converted_file)
        for raw_line in raw_file:
            if raw_line.strip() == "" and not in_py_block and not in_html_block:
                continue
            if raw_line[0] not in "$@%/" and not in_py_block and not in_html_block:
                raw_line = "$p " + raw_line
            if raw_line[0] == '$':
                print(convert_line(raw_line, idx), file=converted_file)
                print(file=converted_file)
            elif raw_line.startswith("@"):
                in_py_block = True
            elif raw_line.startswith("/"):
                if in_py_block:
                    print(wrap_py_block(py_block), file=converted_file)
                    py_block = []
                    in_py_block = False
                elif in_html_block:
                    print(''.join(html_block), file=converted_file)
                    html_block = []
                    in_html_block = False
            elif in_py_block:
                py_block.append(raw_line)
            elif raw_line.startswith("%"):
                in_html_block = True
            elif in_html_block:
                html_block.append(replace_html_special_chars(raw_line))
        print(chapter_links, file=converted_file)
        print(FOOTER, file=converted_file)


if __name__ == '__main__':
    chapters = [
        'cap_programe_agora',
        'cap_variaveis',
        'cap_texto',
        'cap_funcoes',
        'cap_ambiente_de_desenvolvimento',
    ]

    print()
    print(f"Converting {len(chapters)} chapters.")
    print()

    generate_index(chapters)

    idx = 1
    for cur, prev, nxt in zip(
        chapters, [None] + chapters[:-1], chapters[1:] + [None]
    ):
        convert_raw(cur, prev, nxt, idx)
        idx += 1
