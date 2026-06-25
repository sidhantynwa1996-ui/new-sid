#!/usr/bin/env python3
"""
Generate two print-ready PDFs for CFA Level I Quantitative Methods:
  1. Quant_Practice_Questions.pdf  - 220 CFA-style MCQs (no answers shown)
  2. Quant_Answer_Key.pdf          - answer key with explanations
"""

from fpdf import FPDF
from quant_question_bank import QUESTION_BANK

LETTERS = ['A', 'B', 'C']


def san(text):
    """Make text latin-1 safe for the core PDF fonts."""
    repl = {
        '’': "'", '‘': "'", '“': '"', '”': '"',
        '—': ' - ', '–': '-', '…': '...',
        '•': '-', '■': '-', '−': '-',
        '©': '(c)', '®': '(R)', '™': '(TM)',
        'θ': 'theta', 'ρ': 'rho', 'μ': 'mu',
        'σ': 'sigma', 'χ': 'chi', '√': 'sqrt',
        '≠': '!=', '≤': '<=', '≥': '>=',
        '×': 'x', '→': '->', '∞': 'infinity',
    }
    for k, v in repl.items():
        text = text.replace(k, v)
    return text.encode('latin-1', 'replace').decode('latin-1')


class QuizPDF(FPDF):
    def __init__(self, title, subtitle):
        super().__init__()
        self.doc_title = title
        self.doc_subtitle = subtitle
        self.set_auto_page_break(auto=True, margin=18)

    def header(self):
        if self.page_no() == 1:
            return
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(110, 110, 110)
        self.cell(0, 5, san(self.doc_title), 0, 0, 'L')
        self.cell(0, 5, 'CFA Level I - Quantitative Methods', 0, 1, 'R')
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)

    def footer(self):
        self.set_y(-14)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(130, 130, 130)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')

    def cover(self):
        self.add_page()
        self.ln(55)
        self.set_font('Helvetica', 'B', 30)
        self.set_text_color(0, 51, 102)
        self.cell(0, 16, 'CFA Level I', 0, 1, 'C')
        self.ln(2)
        self.set_font('Helvetica', 'B', 22)
        self.cell(0, 12, 'Quantitative Methods', 0, 1, 'C')
        self.ln(8)
        self.set_font('Helvetica', 'B', 18)
        self.set_text_color(60, 60, 60)
        self.multi_cell(0, 10, san(self.doc_title), 0, 'C')
        self.ln(6)
        self.set_font('Helvetica', '', 13)
        self.set_text_color(90, 90, 90)
        self.multi_cell(0, 7, san(self.doc_subtitle), 0, 'C')
        self.ln(20)
        self.set_draw_color(0, 51, 102)
        self.set_line_width(0.5)
        self.line(55, self.get_y(), 155, self.get_y())
        self.ln(10)
        self.set_font('Helvetica', '', 11)
        self.set_text_color(80, 80, 80)
        self.cell(0, 7, '220 CFA-style multiple-choice questions', 0, 1, 'C')
        self.cell(0, 7, '20 questions across each of the 11 learning modules', 0, 1, 'C')
        self.ln(15)
        self.set_font('Helvetica', 'I', 9)
        self.set_text_color(120, 120, 120)
        self.multi_cell(0, 5,
            'Grounded in the 2025 CFA Program Curriculum, Level I, Volume 1 - '
            'Quantitative Methods. For personal exam preparation and practice.',
            0, 'C')

    def topic_banner(self, topic, count):
        self.add_page()
        self.ln(4)
        self.set_fill_color(0, 51, 102)
        self.set_text_color(255, 255, 255)
        self.set_font('Helvetica', 'B', 13)
        self.multi_cell(0, 9, '  ' + san(topic), 0, 'L', fill=True)
        self.ln(2)
        self.set_font('Helvetica', 'I', 9)
        self.set_text_color(90, 90, 90)
        self.cell(0, 6, f'{count} questions', 0, 1, 'L')
        self.ln(2)

    def question(self, number, qtext):
        # keep question + options together where possible
        self.ln(2)
        self.set_font('Helvetica', 'B', 10.5)
        self.set_text_color(0, 51, 102)
        self.multi_cell(0, 5.6, f'Q{number}.', 0, 'L')
        y = self.get_y()
        self.set_xy(self.l_margin, y - 5.6)
        self.set_x(self.l_margin + 12)
        self.set_font('Helvetica', '', 10.5)
        self.set_text_color(20, 20, 20)
        self.multi_cell(0, 5.6, san(qtext))
        self.ln(1)

    def option(self, letter, text):
        self.set_x(self.l_margin + 12)
        self.set_font('Helvetica', '', 10)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 5.2, san(f'{letter}.  {text}'))

    def answer_line(self, number, letter, opttext, explanation):
        self.ln(1.5)
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(0, 102, 51)
        self.multi_cell(0, 5.4, san(f'Q{number}.  Answer: {letter}  -  {opttext}'))
        self.set_x(self.l_margin + 6)
        self.set_font('Helvetica', '', 9)
        self.set_text_color(60, 60, 60)
        self.multi_cell(0, 4.8, san('Rationale: ' + explanation))


def build_questions_pdf(path):
    pdf = QuizPDF('Practice Questions', 'Practice Question Book')
    pdf.alias_nb_pages()
    pdf.cover()
    n = 0
    for topic, qs in QUESTION_BANK.items():
        pdf.topic_banner(topic, len(qs))
        for (qtext, opts, _correct, _expl) in qs:
            n += 1
            pdf.question(n, qtext)
            for i, opt in enumerate(opts):
                pdf.option(LETTERS[i], opt)
    pdf.output(path)
    print(f'Questions PDF: {path}  ({n} questions)')


def build_answer_key_pdf(path):
    pdf = QuizPDF('Answer Key', 'Answer Key with Explanations')
    pdf.alias_nb_pages()
    pdf.cover()

    # Quick-reference answer grid first
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 9, 'Quick Answer Grid', 0, 1, 'L')
    pdf.set_draw_color(0, 51, 102)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)
    n = 0
    grid = []
    for topic, qs in QUESTION_BANK.items():
        for (_q, _o, correct, _e) in qs:
            n += 1
            grid.append((n, LETTERS[correct]))
    # render grid in columns
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(30, 30, 30)
    col_w = 31
    per_row = 6
    for idx in range(0, len(grid), per_row):
        row = grid[idx:idx + per_row]
        for (qn, ans) in row:
            pdf.cell(col_w, 5.5, f'Q{qn}: {ans}', 0, 0, 'L')
        pdf.ln(5.5)
    pdf.ln(4)

    # Detailed explanations by topic
    n = 0
    for topic, qs in QUESTION_BANK.items():
        pdf.topic_banner(topic, len(qs))
        for (qtext, opts, correct, expl) in qs:
            n += 1
            pdf.answer_line(n, LETTERS[correct], opts[correct], expl)
    pdf.output(path)
    print(f'Answer Key PDF: {path}  ({n} answers)')


if __name__ == '__main__':
    build_questions_pdf('/home/user/new-sid/CFA_L1_Quant_Practice_Questions.pdf')
    build_answer_key_pdf('/home/user/new-sid/CFA_L1_Quant_Answer_Key.pdf')
