"""Functions for finding columns in pages.

 Definitions:
'pole' is one character column,
'column' is a # multi-character column
'page' is a list of strings representing a 2D array of text
"""


def is_pole_whitespace(page, index):
    """Is the pole identified by index all whitespace on the page?"""
    for row in page:
        if index >= len(row):
            continue
        if not row[index].isspace():
            return False
    return True


def find_columns(page, margin=2):
    """See if page can be divided into columns of text. margin is the
    vertical spacing between columns to look for. Return a list of
    [col_start, col_end] extents.    """
    extents = []
    # Don't process an empty page
    if len(page) < 1:
        return extents
    num_poles = max((len(row) for row in page))
    # We look for columns separated by margin's worth of whitespace
    # for example:
    # 01234567890
    # a aa  bb  \n
    #           \n
    #  aa   b   \n
    #  a     b  \n
    # Columns are [0, 5], [5, 9], [9, 11]
    # Define state machine variables
    start_col = 0               # start of current column
    start_text = -1             # start of text in current column
    end_text = -1               # end of text if current column
    for pole in range(num_poles):
        if is_pole_whitespace(page, pole):
            if start_text < 0:
                # We are still in whitespace at the start of the column
                continue
            # We may be coming to the end of a column
            if end_text < 0:
                # Text has just finished, set end, wait for margin
                end_text = pole
            if pole - end_text + 1 == margin:
                # Margin reached, we have a column
                extents.append([start_col, end_text])
                start_col = end_text
                start_text = -1
                end_text = -1
        else:
            if start_text < 0:
                # In a column, just started text
                start_text = pole
            # Reset end_text if we had whitespace but did not make margin
            end_text = -1
    # End of line reacged
    last_pole = num_poles - 1   # excluding new line
    if start_text == -1:
        if len(extents) == 0:
            # We never started any columns
            return []
        # All whitespace past the last column. Merge it in
        extents[-1][1] = last_pole
    else:
        # Last column
        extents.append([start_col, last_pole])
    return extents


def get_column(page, extent):
    """Extract the column in page using extent [start, end] poles."""
    start, end = extent
    length = end - start
    column = []
    for row in page:
        text = row[start:end]
        text = text.replace('\n', '')
        text = text.ljust(length)
        column.append(text)
    return column


def paste_columns(columns, boxed=False):
    """Paste a list of columns back together."""
    page = []
    num_rows = max((len(col) for col in columns))
    if num_rows == 0:
        return ""
    col_pad = []
    for col in columns:
        if len(col) == 0:
            col_pad.append(0)
        else:
            lengths = (len(row) for row in col)
            col_pad.append(max(lengths))
    if boxed:
        box_top_bot = ''
        for col_len in col_pad:
            box_top_bot += '+'
            box_top_bot += '-' * col_len
        box_top_bot += '+\n'
        page.append(box_top_bot)
    for row_index in range(num_rows):
        row = '|' if boxed else ''
        for col_index, col in enumerate(columns):
            field = ''
            if row_index < len(col):
                field = col[row_index]
            field = field.ljust(col_pad[col_index])
            field += '|' if boxed else ''
            row += field
        row += '\n'
        page.append(row)
    if boxed:
        page.append(box_top_bot)
    return page
