from docx import Document as DocumentFunction
from docx.document import Document as DocumentClass
from docx.text.paragraph import Paragraph
from docx.table import Table
from docx.oxml.ns import qn
import re
import os

def iter_block_items(parent):
    """
    Generate a reference to each paragraph and table child within *parent*, in document order.
    Each returned value is an instance of either Table or Paragraph.
    """
    if isinstance(parent, DocumentClass):
        parent_elm = parent.element.body
    else:
        parent_elm = parent._element
    for child in parent_elm.iterchildren():
        if child.tag.endswith('}p'):
            yield Paragraph(child, parent)
        elif child.tag.endswith('}tbl'):
            yield Table(child, parent)

def process_runs(runs):
    md_runs = []
    for run in runs:
        text = run.text or ''
        # Check for images
        image_md = process_run_image(run)
        if image_md:
            md_runs.append(image_md)
            continue
        # Apply formatting
        if run.bold and run.italic:
            text = f'<b><i>{text}</i></b>'  # Bold and Italic in HTML
        else:
            if run.bold:
                text = f'<b>{text}</b>'
            if run.italic:
                text = f'<i>{text}</i>'
        if run.underline:
            text = f'<u>{text}</u>'
        if run.font.strike:
            text = f'<s>{text}</s>'
        md_runs.append(text)
    return ''.join(md_runs)

def process_run_image(run):
    # Namespaces
    NS_W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    NS_A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
    NS_R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'

    # Access the drawing elements in the run
    drawing_elements = run.element.findall('.//{' + NS_W + '}drawing')
    for drawing in drawing_elements:
        blip_elements = drawing.findall('.//{' + NS_A + '}blip')
        for blip in blip_elements:
            embed = blip.get('{' + NS_R + '}embed')
            if embed:
                image_part = run.part.related_parts[embed]
                image_bytes = image_part.blob
                image_filename = os.path.basename(image_part.partname)
                image_filepath = os.path.join(image_dir, image_filename)
                # Save image
                with open(image_filepath, 'wb') as img_file:
                    img_file.write(image_bytes)
                # Return HTML image tag
                return f'<img src="{image_filepath}" alt="{image_filename}">'
    return None

def process_paragraph(paragraph):
    style = paragraph.style.name
    text = process_runs(paragraph.runs)

    # Headings
    if 'Heading' in style:
        level = re.search(r'(\d+)', style)
        level = int(level.group(1)) if level else 1
        return f'<h{level}>{text}</h{level}>'
    # Lists
    elif 'List Bullet' in style or 'List Number' in style:
        # For simplicity, treat all lists as unordered lists
        return f'<li>{text}</li>'
    # Regular paragraph
    else:
        return f'<p>{text}</p>'

def process_table(table):
    # Build a grid to represent the table
    grid, max_cols = build_table_grid(table)

    # Generate HTML
    html = '<table border="1">\n'
    for row in grid:
        html += '  <tr>\n'
        for cell_info in row:
            if cell_info is None:
                continue  # Skip placeholders
            attributes = ''
            if cell_info['colspan'] > 1:
                attributes += f' colspan="{cell_info["colspan"]}"'
            if cell_info['rowspan'] > 1:
                attributes += f' rowspan="{cell_info["rowspan"]}"'
            html += f'    <td{attributes}>{cell_info["text"]}</td>\n'
        html += '  </tr>\n'
    html += '</table>\n'
    return html

def build_table_grid(table):
    grid = []
    max_cols = 0
    row_spans = {}

    for row_idx, row in enumerate(table.rows):
        grid_row = []
        col_idx = 0
        while col_idx < len(row.cells):
            cell = row.cells[col_idx]
            key = (row_idx, col_idx)
            # Handle cells that are spanned from previous rows
            while row_spans.get((row_idx, col_idx), 0):
                grid_row.append(None)
                row_spans[(row_idx, col_idx)] -= 1
                col_idx += 1

            cell_text = ''
            for paragraph in cell.paragraphs:
                cell_text += process_runs(paragraph.runs).strip() + '<br>'
            cell_text = cell_text.rstrip('<br>')

            colspan = get_colspan(cell)
            rowspan = get_rowspan(cell)

            # Record row spans
            for i in range(1, rowspan):
                row_spans[(row_idx + i, col_idx)] = colspan

            cell_info = {
                'text': cell_text,
                'colspan': colspan,
                'rowspan': rowspan
            }
            grid_row.append(cell_info)
            # Move to next cell position
            col_idx += colspan
        max_cols = max(max_cols, len(grid_row))
        grid.append(grid_row)
    return grid, max_cols

def get_colspan(cell):
    grid_span_elem = cell._tc.find('.//w:gridSpan', cell._tc.nsmap)
    if grid_span_elem is not None:
        return int(grid_span_elem.get(qn('w:val')))
    return 1

def get_rowspan(cell):
    v_merge_elem = cell._tc.find('.//w:vMerge', cell._tc.nsmap)
    if v_merge_elem is not None:
        v_merge_val = v_merge_elem.get(qn('w:val'))
        if v_merge_val == 'restart':
            rowspan = 1
            next_row = cell._tc.getparent().getnext()
            while next_row is not None:
                cell_index = cell._tc.getparent().index(cell._tc)
                next_cell_elements = [tc for tc in next_row if tc.tag.endswith('}tc')]
                if cell_index >= len(next_cell_elements):
                    break
                next_cell_element = next_cell_elements[cell_index]
                next_v_merge_elem = next_cell_element.find('.//w:vMerge', cell._tc.nsmap)
                if next_v_merge_elem is not None and next_v_merge_elem.get(qn('w:val')) is None:
                    rowspan += 1
                    next_row = next_row.getnext()
                else:
                    break
            return rowspan
    return 1

# Main code
input_file = 'complex_10_pages.docx'
output_file = 'output_4.md'
image_dir = 'images_3'

# Create images directory
os.makedirs(image_dir, exist_ok=True)

# Read the Word document
doc = DocumentFunction(input_file)

# Open output Markdown file
with open(output_file, 'w', encoding='utf-8') as f:
    for block in iter_block_items(doc):
        if isinstance(block, Paragraph):
            md = process_paragraph(block)
            f.write(md + '\n\n')
        elif isinstance(block, Table):
            md = process_table(block)
            f.write(md + '\n\n')
