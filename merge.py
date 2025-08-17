"""Functions to merge text and templates."""


import sys
from abc import ABC
from columns import find_columns, get_column, paste_columns


class MergedLine():
    """Holds a single line of template and text. If they are mergable,
    status is set to True and merged contains the results, else error
    gives a diagnostic."""
    def __init__(self, template, text):
        """Create the object from a text string and a template string."""
        self.template = template
        self.text = text
        self.template_nonws = self.template.replace(' ', '')
        self.text_nonws = self.text.replace(' ', '')
        self.status = False
        self.merged = ""
        self.error = ""
        self.merge()

    def merge(self):
        """If the two lines are merge-able (they have the same number
        of non-white space characters), create merged, else create error."""
        if self.can_merge():
            self.merged = self.merge_line()
            self.status = True
        else:
            self.error += f"<{self.template}"
            self.error += f">{self.text}"
            self.status = False

    def can_merge(self):
        """Return true if the two lines can be merged."""
        return len(self.template_nonws) == len(self.text_nonws)

    def merge_line(self):
        """Merge two lines with same number of characters together."""
        line = ""
        text_index = 0
        for template_char in self.template:
            if template_char.isspace():
                line += template_char
            else:
                line += self.text_nonws[text_index]
                text_index += 1
        return line


class MergedPage(ABC):
    """Base class for merge implementations."""
    def __init__(self, template, text):
        """Common base class init function."""
        self.text = MergedPage.load(text)
        self.template = MergedPage.load(template)
        self.merged_rows = []
        self.status = False

    @staticmethod
    def load(list_or_file):
        """If param is a filename, load a list of strings from it,
            else treat as a list. Remove trailing blank lines"""
        if isinstance(list_or_file, list):
            lines = list_or_file
        else:
            try:
                with open(list_or_file, 'r', encoding='utf8') as f:
                    lines = list(f)
            except FileNotFoundError as e:
                print(f"File not found - {e.filename}")
                sys.exit(1)
        # Remove trailing blank lines
        while lines and lines[-1].strip() == "":
            lines.pop()
        return lines

    def report(self, debug):
        """For row merge, Return a list of either merged text or error
        messages."""
        report = []
        for line in self.merged_rows:
            if line.status:
                report.append(line.merged)
            elif debug:
                report.append(line.error)
        return report


class MergedPageRows(MergedPage):
    """Treat the page as a collection of rows."""
    def __init__(self, template, text):
        super().__init__(template, text)
        self.check_lengths()
        self.status = self.merge_by_row()

    def check_lengths(self):
        """Ideally text and template should be the same length. If
        not, pad them to the same lengthe."""
        diff = len(self.text) - len(self.template)
        if diff > 0:
            self.template += ['\n'] * diff
        elif diff < 0:
            self.text += ['\n'] * -diff

    def merge_by_row(self):
        """Merge each horizontal line."""
        status = True
        for index, template_line in enumerate(self.template):
            text_line = self.text[index]
            merged = MergedLine(template_line, text_line)
            status = status and merged.status
            self.merged_rows.append(merged)
        return status


class MergedPageColumns(MergedPage):
    """Treat the page as a column."""
    def __init__(self, template, text):
        super().__init__(template, text)
        self.status = self.merge_column()

    def merge_column(self):
        """Treat this page as a column, and merge vertically."""
        status = True
        text_index = 0
        for template_line in self.template:
            if template_line.isspace():
                merged = MergedLine(template_line, template_line)
            else:
                text_line = ' ' * len(template_line)
                while text_index < len(self.text) and text_line.isspace():
                    text_line = self.text[text_index]
                    text_index += 1
                merged = MergedLine(template_line, text_line)
            status = status and merged.status
            self.merged_rows.append(merged)
        # Add any text that remains
        while text_index < len(self.text):
            text_line = self.text[text_index]
            text_index += 1
            if text_line.isspace():
                continue
            template_line = ' ' * len(text_line)
            merged = MergedLine(template_line, text_line)
            status = status and merged.status
            self.merged_rows.append(merged)
        return status


def merge(template, text, margin=2, debug=False):
    """Factory function to create a MergedPage object."""
    by_rows = MergedPageRows(template, text)
    if not by_rows.status:
        by_cols_status, by_cols_report = try_merge_by_columns(by_rows,
                                                              margin, debug)
        if by_cols_report:
            return by_cols_status, by_cols_report
    report = by_rows.report(debug)
    if debug:
        report = box_it(report)
    return by_rows.status, report


def box_it(report):
    """Add a box for the by-rows diff"""
    expanded = []
    for line in report:
        expanded += line[:-1].split('\n')
    report = expanded
    line_len = + max((len(line) for line in report))
    top_bot = '+' + '-' * (line_len - 1) + '+\n'
    out = top_bot
    for line in report:
        if line[0] not in {'<', '>'}:
            out += '|' + line.ljust(line_len - 1)
        else:
            out += line.ljust(line_len)
        out += "|\n"
    out += top_bot
    return out


def try_merge_by_columns(rows, margin, debug):
    """Try the column merge approach."""
    text_cols_extents = find_columns(rows.text, margin)
    template_cols_extents = find_columns(rows.template, margin)
    if len(text_cols_extents) != len(template_cols_extents):
        report = column_merge_diagnostic(text_cols_extents,
                                         rows.text,
                                         template_cols_extents,
                                         rows.template)
        return False, report
    status = True
    merged_columns = []
    for index, text_extent in enumerate(text_cols_extents):
        text_col = get_column(rows.text, text_extent)
        template_extent = template_cols_extents[index]
        template_col = get_column(rows.template, template_extent)
        merged_col = MergedPageColumns(template_col, text_col)
        merged_columns.append(merged_col)
        status = status and merged_col.status
    report = paste_report(merged_columns, debug)
    return status, report


def column_merge_diagnostic(text_extents, text, template_extents, template):
    """Return a report when column merge failed."""
    report = "Column merge failed, template has "
    report += f"{len(template_extents)}, text has "
    report += f"{len(text_extents)}\n"
    report += "TEMPLATE\n" + diagnostic_sample(template_extents, template)
    report += "TEXT\n" + diagnostic_sample(text_extents, text)
    return report


def diagnostic_sample(extents, rows):
    """Show a sample of how the columns look."""
    report = ""
    for extent in extents:
        report += '+'
        report += '-' * (extent[1] - extent[0] - 1)
    report += '\n'
    for index in range(10):
        report += rows[index]
    return report


def paste_report(merged_columns, debug):
    """Produce a merge report from several columns."""
    report = []
    report_columns = [col.report(debug) for col in merged_columns]
    pasted = paste_columns(report_columns, boxed=debug)
    for paste in pasted:
        if debug:
            report += '!' if paste.find('|<') > 0 else ' '
        report += paste
    return report
