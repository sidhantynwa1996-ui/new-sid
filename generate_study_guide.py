#!/usr/bin/env python3
"""
Generate a comprehensive CFA Level 1 Ethics Study Guide PDF
from the extracted textbook content.
"""

import fitz  # PyMuPDF
from fpdf import FPDF
import re
import textwrap


class StudyGuidePDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        if self.page_no() > 1:
            self.set_font('Helvetica', 'I', 8)
            self.set_text_color(100, 100, 100)
            self.cell(0, 5, 'CFA Level I - Ethical and Professional Standards - Comprehensive Study Guide', 0, 0, 'C')
            self.ln(8)
            self.set_draw_color(200, 200, 200)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(3)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')

    def title_page(self):
        self.add_page()
        self.ln(60)
        self.set_font('Helvetica', 'B', 28)
        self.set_text_color(0, 51, 102)
        self.cell(0, 15, 'CFA Level I', 0, 1, 'C')
        self.ln(5)
        self.set_font('Helvetica', 'B', 24)
        self.cell(0, 12, 'Ethical and Professional', 0, 1, 'C')
        self.cell(0, 12, 'Standards', 0, 1, 'C')
        self.ln(10)
        self.set_font('Helvetica', '', 16)
        self.set_text_color(80, 80, 80)
        self.cell(0, 10, 'Comprehensive Study Guide', 0, 1, 'C')
        self.ln(5)
        self.set_font('Helvetica', '', 14)
        self.cell(0, 10, '2025 Curriculum - Volume 10', 0, 1, 'C')
        self.ln(30)
        self.set_draw_color(0, 51, 102)
        self.set_line_width(0.5)
        self.line(60, self.get_y(), 150, self.get_y())
        self.ln(10)
        self.set_font('Helvetica', 'I', 11)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, 'Covers all 5 Learning Modules:', 0, 1, 'C')
        self.set_font('Helvetica', '', 10)
        modules = [
            '1. Ethics and Trust in the Investment Profession',
            '2. Code of Ethics and Standards of Professional Conduct',
            '3. Guidance for Standards I-VII',
            '4. Introduction to GIPS',
            '5. Ethics Application',
        ]
        for m in modules:
            self.cell(0, 7, m, 0, 1, 'C')

    def toc_page(self):
        self.add_page()
        self.set_font('Helvetica', 'B', 18)
        self.set_text_color(0, 51, 102)
        self.cell(0, 12, 'TABLE OF CONTENTS', 0, 1, 'L')
        self.ln(5)
        self.set_draw_color(0, 51, 102)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(8)

    def module_title(self, number, title):
        self.add_page()
        self.ln(10)
        self.set_fill_color(0, 51, 102)
        self.rect(10, self.get_y(), 190, 18, 'F')
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(255, 255, 255)
        self.set_y(self.get_y() + 3)
        self.cell(0, 12, f'  LEARNING MODULE {number}', 0, 1, 'L')
        self.ln(5)
        self.set_font('Helvetica', 'B', 20)
        self.set_text_color(0, 51, 102)
        self.multi_cell(0, 10, title)
        self.ln(8)
        self.set_draw_color(0, 51, 102)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(8)

    def section_heading(self, text, level=1):
        self.ln(3)
        if level == 1:
            self.set_font('Helvetica', 'B', 14)
            self.set_text_color(0, 51, 102)
            self.multi_cell(0, 8, text)
            self.set_draw_color(0, 51, 102)
            self.line(10, self.get_y() + 1, 120, self.get_y() + 1)
            self.ln(4)
        elif level == 2:
            self.set_font('Helvetica', 'B', 12)
            self.set_text_color(51, 51, 51)
            self.multi_cell(0, 7, text)
            self.ln(2)
        elif level == 3:
            self.set_font('Helvetica', 'BI', 11)
            self.set_text_color(80, 80, 80)
            self.multi_cell(0, 7, text)
            self.ln(2)

    def body_text(self, text):
        self.set_font('Helvetica', '', 10)
        self.set_text_color(30, 30, 30)
        text = text.replace('’', "'").replace('‘', "'")
        text = text.replace('“', '"').replace('”', '"')
        text = text.replace('—', ' - ').replace('–', '-')
        text = text.replace('•', '-').replace('■', '-')
        text = text.replace('©', '(c)').replace('®', '(R)')
        text = text.replace('…', '...')
        text = text.encode('latin-1', 'replace').decode('latin-1')
        self.multi_cell(0, 5.5, text)
        self.ln(2)

    def bullet_point(self, text):
        self.set_font('Helvetica', '', 10)
        self.set_text_color(30, 30, 30)
        text = text.encode('latin-1', 'replace').decode('latin-1')
        x = self.get_x()
        self.cell(8, 5.5, '  -', 0, 0)
        self.multi_cell(0, 5.5, text)
        self.ln(1)

    def key_concept_box(self, title, text):
        self.ln(3)
        self.set_fill_color(240, 245, 255)
        self.set_draw_color(0, 51, 102)
        y_start = self.get_y()

        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(0, 51, 102)
        text_clean = text.encode('latin-1', 'replace').decode('latin-1')
        title_clean = title.encode('latin-1', 'replace').decode('latin-1')

        self.set_x(15)
        self.cell(180, 7, f'KEY CONCEPT: {title_clean}', 0, 1)
        self.set_x(15)
        self.set_font('Helvetica', '', 9.5)
        self.set_text_color(30, 30, 30)
        self.multi_cell(175, 5, text_clean)
        y_end = self.get_y()

        self.set_fill_color(240, 245, 255)
        self.rect(12, y_start - 2, 186, y_end - y_start + 6, 'D')
        self.ln(5)

    def example_box(self, title, text):
        self.ln(2)
        self.set_fill_color(255, 248, 240)
        self.set_draw_color(200, 150, 50)

        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(150, 100, 0)
        title_clean = title.encode('latin-1', 'replace').decode('latin-1')
        text_clean = text.encode('latin-1', 'replace').decode('latin-1')
        self.set_x(15)
        self.cell(180, 6, title_clean, 0, 1)
        self.set_font('Helvetica', '', 9)
        self.set_text_color(60, 60, 60)
        self.set_x(15)
        self.multi_cell(175, 5, text_clean)
        self.ln(3)


def clean_text(text):
    text = re.sub(r'© CFA Institute\. For candidate use only\. Not for distribution\.', '', text)
    text = re.sub(r'Learning Module \d+\s+.*?\n', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def extract_module_text(doc, start_page, end_page):
    text = ''
    for i in range(start_page - 1, end_page):
        text += doc[i].get_text()
    return clean_text(text)


def build_study_guide():
    pdf = StudyGuidePDF()
    pdf.alias_nb_pages()

    doc = fitz.open('/home/user/new-sid/CFA Institute - 2025 CFA© Program Curriculum Level I Volume 10 - ETHICS-CFA Institute (2025).pdf')

    # Title Page
    pdf.title_page()

    # =========================================================================
    # MODULE 1: Ethics and Trust in the Investment Profession
    # =========================================================================
    pdf.module_title(1, 'Ethics and Trust in the Investment Profession')

    pdf.section_heading('Learning Outcomes')
    pdf.body_text('After completing this module, you should be able to:')
    for lo in [
        'Explain ethics',
        'Describe the role of a code of ethics in defining a profession',
        'Describe professions and how they establish trust',
        'Describe the need for high ethical standards in investment management',
        'Explain professionalism in investment management',
        'Identify challenges to ethical behavior',
        'Compare and contrast ethical standards with legal standards',
        'Describe a framework for ethical decision making',
    ]:
        pdf.bullet_point(lo)
    pdf.ln(5)

    # Introduction
    pdf.section_heading('Introduction')
    pdf.body_text(
        'As a candidate in the CFA Program, you are both expected and required to meet high ethical standards. '
        'This learning module introduces ideas and concepts that will help you understand the importance of ethical '
        'behavior in the investment industry. You will be introduced to various types of ethical issues within the '
        'investment profession and learn about the CFA Institute Code of Ethics.'
    )
    pdf.body_text(
        'The readings covering ethics and professional standards demonstrate that ethical behavior is central to '
        'creating trust. Professional behavior is equally important. Professions help maintain trust in an industry '
        'by establishing codes and setting standards that put a framework around ethical behavior and technical '
        'competence. Professions also set the wider goal of gaining and maintaining the trust of society as a whole, '
        'not just the trust of those who directly use their services.'
    )
    pdf.body_text(
        'In the investment profession, trust is paramount. Clients entrust their savings and financial future to '
        'investment professionals. A breach of this trust can have devastating consequences for individuals, '
        'institutions, and markets. Ethical conduct is not just a set of rules to follow but a fundamental '
        'requirement for the proper functioning of capital markets.'
    )

    # Ethics
    pdf.section_heading('Ethics')
    pdf.body_text(
        'Ethics can be described as a set of moral principles and rules of conduct that provide guidance for our '
        'behavior. Ethics encompasses a shared set of values including honesty, trust, fairness, and a broad '
        'concept of respect and responsibility for others. These are not unique to any particular culture or '
        'society; rather, they are universal concepts that apply across all borders.'
    )
    pdf.body_text(
        'Ethical conduct is behavior that follows moral principles. Ethical behavior involves making choices that '
        'are consistent with our values and beliefs about what is right and wrong. It requires not only knowing '
        'what is right but having the courage and commitment to act accordingly, even when doing so is difficult '
        'or personally costly.'
    )
    pdf.body_text(
        'There are several approaches to studying ethics:'
    )
    pdf.bullet_point('Virtue ethics focuses on the character of the individual and asks what kind of person one should be. It emphasizes character traits such as honesty, integrity, courage, and fairness.')
    pdf.bullet_point('Deontological ethics focuses on duties and obligations. It emphasizes rules and principles that govern behavior regardless of the consequences.')
    pdf.bullet_point('Teleological ethics (consequentialism) focuses on the consequences or outcomes of actions. An action is considered ethical if it produces good outcomes and unethical if it produces bad outcomes.')
    pdf.bullet_point('Situational ethics holds that ethical behavior depends on the specific situation and context. What is ethical in one situation may not be ethical in another.')

    pdf.body_text(
        'While these various ethical frameworks may lead to different conclusions in certain situations, they share '
        'common ground in valuing honesty, fairness, and the well-being of others. In the investment profession, '
        'these principles translate into specific requirements for professional conduct.'
    )

    pdf.body_text(
        'Not all unethical behavior involves making a conscious decision to do wrong. Sometimes people act unethically '
        'because they fail to consider the ethical dimensions of their decisions. They may focus narrowly on financial '
        'outcomes or regulatory compliance without considering the broader ethical implications of their actions. '
        'Ethical awareness - the ability to recognize when a situation has ethical dimensions - is a critical skill '
        'for investment professionals.'
    )

    # Ethics and Professionalism
    pdf.section_heading('Ethics and Professionalism')
    pdf.body_text(
        'A profession is an occupational group that has specific expert knowledge and skills recognized by society. '
        'Professions serve society by providing services that require specialized knowledge. In return, society grants '
        'professions certain privileges, such as the right to self-regulate and to set standards for membership and '
        'practice.'
    )

    pdf.section_heading('How Professions Establish Trust', level=2)
    pdf.body_text(
        'Professions establish trust through several mechanisms:'
    )
    pdf.bullet_point('Normalization of practitioner behavior: Professions establish codes of conduct and ethical standards that members are expected to follow. These norms set minimum standards of behavior and create expectations for how professionals will act.')
    pdf.bullet_point('Barrier to entry through education and examination: Professions require members to demonstrate a certain level of knowledge and competence through education and examination before they can practice. This ensures that only qualified individuals can provide professional services.')
    pdf.bullet_point('Ongoing oversight of members: Professions monitor the behavior of their members through continuing education requirements, periodic reviews, and disciplinary processes. This ongoing oversight helps ensure that members continue to meet the standards expected of them.')
    pdf.bullet_point('Enforcement and disciplinary actions: Professions have the authority to discipline members who violate professional standards. Sanctions can range from reprimands and fines to suspension or expulsion from the profession.')

    pdf.body_text(
        'These mechanisms work together to create a system of trust. Clients and the public can rely on the fact '
        'that members of a profession have met certain standards of competence, will adhere to established codes '
        'of conduct, and will be held accountable if they fall short of these expectations.'
    )

    pdf.section_heading('Professions Are Evolving', level=2)
    pdf.body_text(
        'Professions are not static; they evolve over time in response to changes in society, technology, and the '
        'markets they serve. The investment profession has undergone significant changes in recent decades, driven '
        'by factors such as globalization, technological innovation, the development of complex financial instruments, '
        'and increasing regulation. These changes have created new ethical challenges and have required the profession '
        'to adapt its standards and practices accordingly.'
    )

    pdf.section_heading('Professionalism in Investment Management', level=2)
    pdf.body_text(
        'The investment management industry possesses many of the characteristics of a profession. It requires '
        'specialized knowledge and skills, it serves important social functions (helping individuals and institutions '
        'allocate capital and manage risk), and it has established organizations and standards that promote ethical '
        'behavior and competence.'
    )
    pdf.body_text(
        'However, the investment management industry also faces challenges in fully achieving professional status. '
        'Unlike traditional professions such as medicine and law, entry into the investment management field is not '
        'strictly regulated in most jurisdictions. There is no single licensing requirement, and the industry is '
        'fragmented across different types of firms and roles.'
    )

    pdf.section_heading('Trust in Investment Management', level=2)
    pdf.body_text(
        'Trust is the foundation of the investment management profession. Clients entrust their assets and financial '
        'well-being to investment professionals. This trust is based on the expectation that investment professionals '
        'will act with integrity, competence, and in the best interests of their clients.'
    )
    pdf.body_text(
        'When trust is violated, the consequences can be severe - not only for the individuals directly affected but '
        'for the industry as a whole. Scandals and ethical failures in the investment industry can erode public '
        'confidence in financial markets and institutions, leading to reduced participation, increased regulation, '
        'and diminished effectiveness of capital allocation.'
    )

    pdf.section_heading('CFA Institute as an Investment Management Professional Body', level=2)
    pdf.body_text(
        'CFA Institute is a global association of investment professionals that sets the standard for professional '
        'excellence and credentials. It administers the CFA Program, which is widely recognized as the gold standard '
        'for investment management education and professional development.'
    )
    pdf.body_text(
        'CFA Institute plays a key role in promoting ethical behavior in the investment profession through:'
    )
    pdf.bullet_point('The CFA Program curriculum, which includes a significant emphasis on ethics and professional standards')
    pdf.bullet_point('The Code of Ethics and Standards of Professional Conduct, which all members and candidates must follow')
    pdf.bullet_point('The Professional Conduct Program, which enforces the Code and Standards')
    pdf.bullet_point('Research and advocacy on ethical issues in the investment industry')
    pdf.bullet_point('The Global Investment Performance Standards (GIPS), which promote fair representation of investment performance')

    # Challenges to Ethical Conduct
    pdf.section_heading('Challenges to Ethical Conduct')
    pdf.body_text(
        'Even well-intentioned investment professionals can face significant challenges to ethical conduct. '
        'Understanding these challenges is the first step toward overcoming them. Key challenges include:'
    )

    pdf.section_heading('Overconfidence Bias', level=2)
    pdf.body_text(
        'Overconfidence bias leads individuals to overestimate their own abilities, knowledge, and the precision '
        'of their predictions. In the investment profession, overconfidence can lead professionals to take excessive '
        'risks, ignore contrary evidence, or fail to adequately consider the limitations of their analysis. '
        'Overconfident professionals may also believe that ethical rules do not apply to them or that they can '
        'handle conflicts of interest without being influenced.'
    )

    pdf.section_heading('Situational Influences', level=2)
    pdf.body_text(
        'Research has shown that people\'s behavior is heavily influenced by the situations they find themselves in. '
        'Even people with strong ethical values can behave unethically when placed in certain situations. '
        'Situational factors that can undermine ethical behavior include:'
    )
    pdf.bullet_point('Pressure from supervisors or peers to meet performance targets or deadlines')
    pdf.bullet_point('Financial incentives that reward short-term results or excessive risk-taking')
    pdf.bullet_point('Organizational cultures that prioritize profits over ethics')
    pdf.bullet_point('Gradual escalation of unethical behavior (the "slippery slope")')
    pdf.bullet_point('Diffusion of responsibility, where individuals feel less personally responsible for ethical outcomes because others are also involved')

    pdf.section_heading('Loyalty and Authority', level=2)
    pdf.body_text(
        'Loyalty to colleagues, clients, or the organization can create ethical conflicts. Professionals may feel '
        'pressure to act in ways that serve the interests of those to whom they feel loyal, even when doing so '
        'conflicts with their ethical obligations. Similarly, deference to authority can lead professionals to '
        'follow instructions from superiors without questioning whether those instructions are ethical.'
    )

    pdf.section_heading('Short-Term Focus', level=2)
    pdf.body_text(
        'The investment industry often emphasizes short-term performance, which can create incentives for unethical '
        'behavior. Professionals may be tempted to take shortcuts, manipulate results, or engage in other unethical '
        'practices to achieve short-term goals, even when doing so is detrimental to long-term outcomes and '
        'relationships.'
    )

    # Ethical vs. Legal Standards
    pdf.section_heading('Ethical vs. Legal Standards')
    pdf.body_text(
        'It is important to distinguish between ethical standards and legal standards. While the two overlap in many '
        'areas, they are not identical:'
    )
    pdf.bullet_point('Laws are rules established by governments and enforced through the legal system. They set minimum standards of behavior that are required of all members of society.')
    pdf.bullet_point('Ethical standards typically set higher expectations than legal standards. Behavior that is legal may not be ethical, and ethical obligations may go beyond what the law requires.')
    pdf.bullet_point('Laws tend to be more specific and prescriptive, while ethical standards are often more general and principled. Laws tell you what you must or must not do; ethics guides you in determining what you should do.')
    pdf.bullet_point('Ethical standards can fill gaps in the law. In rapidly evolving fields like finance, new products and practices may emerge before laws and regulations are developed to address them. Ethical principles can provide guidance in these uncharted areas.')

    pdf.body_text(
        'For CFA Institute members and candidates, the Code and Standards set ethical requirements that often exceed '
        'legal requirements. Members and candidates are expected to comply with the stricter of applicable law or the '
        'Code and Standards. When the Code and Standards impose a higher standard than local law, members and '
        'candidates must follow the Code and Standards.'
    )

    pdf.body_text(
        'Key distinctions between ethical and legal standards:'
    )
    pdf.bullet_point('Not all unethical conduct is illegal. A professional might exploit a client\'s trust in ways that are legal but clearly unethical.')
    pdf.bullet_point('Not all illegal conduct is necessarily unethical in all moral frameworks, though CFA members should always comply with applicable law.')
    pdf.bullet_point('Ethical conduct requires going beyond mere legal compliance to consider the spirit of the law and the interests of all stakeholders.')
    pdf.bullet_point('When ethical and legal standards conflict, CFA members should follow the stricter standard (typically the Code and Standards).')

    # Ethical Decision-Making Frameworks
    pdf.section_heading('Ethical Decision-Making Frameworks')
    pdf.body_text(
        'Having a systematic framework for ethical decision-making helps professionals navigate complex ethical '
        'situations consistently and thoughtfully. CFA Institute recommends a structured approach to ethical '
        'decision-making that involves several steps.'
    )

    pdf.section_heading('The Framework for Ethical Decision-Making', level=2)
    pdf.body_text(
        'The CFA Institute Framework for Ethical Decision-Making is a structured process that helps '
        'investment professionals analyze and resolve ethical dilemmas. The framework consists of the following steps:'
    )
    pdf.bullet_point('IDENTIFY: Identify the relevant facts, stakeholders, duties owed, ethical principles at stake, and any conflicts of interest.')
    pdf.bullet_point('CONSIDER: Consider the situational influences that may affect your judgment. Are there pressures, biases, or other factors that might lead you to rationalize unethical behavior?')
    pdf.bullet_point('DECIDE AND ACT: Decide on a course of action that is consistent with your ethical obligations. Consider multiple alternatives and their potential consequences for all stakeholders.')
    pdf.bullet_point('REFLECT: After acting, reflect on the outcome. Did your decision achieve the intended result? Would you make the same decision again? What did you learn from the experience?')

    pdf.body_text(
        'The framework emphasizes the importance of considering all stakeholders, not just the most immediate '
        'or obvious ones. In the investment profession, stakeholders can include clients, employers, colleagues, '
        'regulators, the investing public, and society at large.'
    )

    pdf.section_heading('Applying the Framework', level=2)
    pdf.body_text(
        'When applying the ethical decision-making framework, consider the following guidance:'
    )
    pdf.bullet_point('Take time to fully understand the situation before making a decision. Gather all relevant facts and consider different perspectives.')
    pdf.bullet_point('Identify all the stakeholders who might be affected by your decision and consider how each would be impacted.')
    pdf.bullet_point('Consider your duties and obligations to each stakeholder. When duties conflict, consider which obligations take priority.')
    pdf.bullet_point('Be aware of your own biases and the situational influences that might affect your judgment.')
    pdf.bullet_point('Consider whether your decision would withstand public scrutiny. Would you be comfortable if your decision were reported in the media?')
    pdf.bullet_point('Seek guidance from trusted colleagues, compliance officers, or legal counsel when facing difficult ethical decisions.')
    pdf.bullet_point('Document your decision-making process, including the factors you considered and the reasons for your decision.')

    # =========================================================================
    # MODULE 2: Code of Ethics and Standards of Professional Conduct
    # =========================================================================
    pdf.module_title(2, 'Code of Ethics and Standards of Professional Conduct')

    pdf.section_heading('Learning Outcomes')
    pdf.body_text('After completing this module, you should be able to:')
    for lo in [
        'Describe the structure of the CFA Institute Professional Conduct Program and the process for the enforcement of the Code and Standards',
        'Identify the six components of the Code of Ethics and the seven Standards of Professional Conduct',
        'Explain the ethical responsibilities required by the Code and Standards, including the sub-sections of each Standard',
    ]:
        pdf.bullet_point(lo)
    pdf.ln(3)

    pdf.section_heading('Evolution of the Code and Standards')
    pdf.body_text(
        'The Code and Standards are regularly reviewed and updated so that they remain effective and continue to '
        'represent the highest ethical standards in the global investment industry. CFA Institute strongly believes '
        'that revisions of the Code and Standards are undertaken not for cosmetic purposes but to add value by '
        'addressing legitimate concerns and improving comprehension. In 2023, the CFA Institute Board of Governors '
        'approved revisions to the Code and Standards.'
    )
    pdf.body_text(
        'Changes to the Code and Standards have far-reaching implications for the CFA Institute membership, the '
        'CFA Program, and the investment industry as a whole. CFA Institute members and candidates are required to '
        'adhere to the Code and Standards. In addition, the Code and Standards are often adopted, in whole or in '
        'part, by firms and regulatory authorities.'
    )

    pdf.section_heading('Summary of 2023 Revisions', level=2)
    pdf.body_text('In 2023, the Board of Governors revised the Standards in three areas:')
    pdf.bullet_point('Within Standard I: Professionalism, the Board approved a new Standard I(E) Competence requiring members to act with and maintain the competence necessary to fulfill their professional responsibilities.')
    pdf.bullet_point('Within Standard V: Investment Analysis, the Board revised Standard V(B) Communication with Clients to require disclosures about the nature of services provided and costs to clients.')
    pdf.bullet_point('Within Standard VI: Conflicts of Interest, the Board changed Standard VI(A) to "Avoid or Disclose Conflicts" requiring members to either avoid or disclose conflicts of interest.')

    pdf.section_heading('CFA Institute Professional Conduct Program')
    pdf.body_text(
        'All CFA Institute members and candidates enrolled in the CFA Program are required to comply with the Code '
        'and Standards. The CFA Institute Board of Governors maintains oversight and responsibility for the '
        'Professional Conduct Program (PCP), which, in conjunction with the Disciplinary Review Committee (DRC), '
        'is responsible for enforcement of the Code and Standards.'
    )
    pdf.body_text(
        'The DRC is a volunteer committee of CFA charterholders who serve on panels to review conduct and partner '
        'with Professional Conduct staff to establish and review professional conduct policies.'
    )

    pdf.section_heading('Sources of Professional Conduct Inquiries', level=2)
    pdf.body_text('Professional Conduct inquiries come from several sources:')
    pdf.bullet_point('Self-disclosure: Members and candidates must self-disclose on the annual Professional Conduct Statement all matters that question their professional conduct, such as involvement in civil litigation, criminal investigation, or being the subject of a written complaint.')
    pdf.bullet_point('Written complaints: Written complaints received by Professional Conduct staff can bring about an investigation.')
    pdf.bullet_point('Public sources: CFA Institute staff may become aware of questionable conduct through the media, regulatory notices, or another public source.')
    pdf.bullet_point('Exam proctors: Candidate conduct is monitored by proctors who complete reports on candidates suspected to have violated testing rules.')
    pdf.bullet_point('Post-exam analysis: CFA Institute may conduct analyses of scores and exam materials after the exam, and monitor online and social media to detect disclosure of confidential exam information.')

    pdf.section_heading('Investigation and Disciplinary Process', level=2)
    pdf.body_text(
        'When an inquiry is initiated, the Professional Conduct staff conducts an investigation that may include: '
        'requesting a written explanation from the member or candidate; interviewing the member or candidate, '
        'complaining parties, and third parties; and collecting documents and records relevant to the investigation.'
    )
    pdf.body_text(
        'Upon reviewing the material obtained during the investigation, the Professional Conduct staff may: '
        '(1) conclude the inquiry with no disciplinary sanction, (2) issue a cautionary letter, or (3) continue '
        'proceedings to discipline the member or candidate.'
    )
    pdf.body_text(
        'If the member or candidate does not accept the charges and proposed sanction, the matter is referred to '
        'a panel composed of DRC members. Sanctions imposed by CFA Institute may include: public censure, suspension '
        'of membership and use of the CFA designation, and revocation of the CFA charter. Candidates may be '
        'suspended or prohibited from further participation in the CFA Program.'
    )

    # Ethics and the Investment Industry
    pdf.section_heading('Ethics and the Investment Industry')

    pdf.section_heading('Why Ethics Matters', level=2)
    pdf.body_text(
        'Ethics is at the heart of the investment profession. Investment management is built on trust, and trust is '
        'built on ethical behavior. When investment professionals act ethically, they contribute to the efficient '
        'functioning of capital markets and the well-being of society.'
    )
    pdf.body_text(
        'The investment industry operates in an environment where information asymmetry is prevalent. Clients '
        'typically know less about investments and markets than the professionals they hire. This information gap '
        'creates opportunities for exploitation. Ethical standards help protect clients by requiring professionals '
        'to act in their clients\' best interests and to provide full and fair disclosure of relevant information.'
    )
    pdf.body_text(
        'Capital markets depend on trust and confidence to function effectively. When investors lose confidence '
        'in the fairness and integrity of markets, they reduce their participation, which can lead to less '
        'efficient capital allocation, higher costs of capital, and slower economic growth. Ethical behavior by '
        'investment professionals helps maintain the confidence and trust that are essential to healthy capital markets.'
    )

    # The Code of Ethics
    pdf.section_heading('The Code of Ethics')
    pdf.body_text(
        'Members of CFA Institute (including CFA charterholders) and candidates for the CFA designation '
        '("Members and Candidates") must:'
    )
    pdf.bullet_point('Act with integrity, competence, diligence, and respect and in an ethical manner with the public, clients, prospective clients, employers, employees, colleagues in the investment profession, and other participants in the global capital markets.')
    pdf.bullet_point('Place the integrity of the investment profession and the interests of clients above their own personal interests.')
    pdf.bullet_point('Use reasonable care and exercise independent professional judgment when conducting investment analysis, making investment recommendations, taking investment actions, and engaging in other professional activities.')
    pdf.bullet_point('Practice and encourage others to practice in a professional and ethical manner that will reflect credit on themselves and the profession.')
    pdf.bullet_point('Promote the integrity and viability of the global capital markets for the ultimate benefit of society.')
    pdf.bullet_point('Maintain and improve their professional competence and strive to maintain and improve the competence of other investment professionals.')

    # Standards of Professional Conduct
    pdf.section_heading('Standards of Professional Conduct')
    pdf.body_text(
        'The Standards of Professional Conduct are organized into seven main standards, each with sub-sections. '
        'These are the practical ethical principles that members and candidates must follow:'
    )

    pdf.section_heading('I. Professionalism', level=2)
    pdf.bullet_point('I(A) Knowledge of the Law')
    pdf.bullet_point('I(B) Independence and Objectivity')
    pdf.bullet_point('I(C) Misrepresentation')
    pdf.bullet_point('I(D) Misconduct')
    pdf.bullet_point('I(E) Competence')

    pdf.section_heading('II. Integrity of Capital Markets', level=2)
    pdf.bullet_point('II(A) Material Nonpublic Information')
    pdf.bullet_point('II(B) Market Manipulation')

    pdf.section_heading('III. Duties to Clients', level=2)
    pdf.bullet_point('III(A) Loyalty, Prudence, and Care')
    pdf.bullet_point('III(B) Fair Dealing')
    pdf.bullet_point('III(C) Suitability')
    pdf.bullet_point('III(D) Performance Presentation')
    pdf.bullet_point('III(E) Preservation of Confidentiality')

    pdf.section_heading('IV. Duties to Employers', level=2)
    pdf.bullet_point('IV(A) Loyalty')
    pdf.bullet_point('IV(B) Additional Compensation Arrangements')
    pdf.bullet_point('IV(C) Responsibilities of Supervisors')

    pdf.section_heading('V. Investment Analysis, Recommendations, and Actions', level=2)
    pdf.bullet_point('V(A) Diligence and Reasonable Basis')
    pdf.bullet_point('V(B) Communication with Clients and Prospective Clients')
    pdf.bullet_point('V(C) Record Retention')

    pdf.section_heading('VI. Conflicts of Interest', level=2)
    pdf.bullet_point('VI(A) Avoid or Disclose Conflicts')
    pdf.bullet_point('VI(B) Priority of Transactions')
    pdf.bullet_point('VI(C) Referral Fees')

    pdf.section_heading('VII. Responsibilities as a CFA Institute Member or CFA Candidate', level=2)
    pdf.bullet_point('VII(A) Conduct as Participants in CFA Institute Programs')
    pdf.bullet_point('VII(B) Reference to CFA Institute, the CFA Designation, and the CFA Program')

    # =========================================================================
    # MODULE 3: Guidance for Standards I-VII (THE BIG MODULE)
    # =========================================================================
    pdf.module_title(3, 'Guidance for Standards I-VII')

    pdf.body_text(
        'This is the most extensive and detailed module in the Ethics curriculum. It provides comprehensive '
        'guidance on each of the seven Standards of Professional Conduct, including the specific requirements '
        'of each standard, recommended procedures for compliance, and numerous examples illustrating how the '
        'standards apply in practice.'
    )

    # ---- STANDARD I: PROFESSIONALISM ----
    pdf.section_heading('STANDARD I: PROFESSIONALISM')

    # I(A) Knowledge of the Law
    pdf.section_heading('Standard I(A): Knowledge of the Law', level=2)
    pdf.body_text(
        'Members and Candidates must understand and comply with all applicable laws, rules, and regulations '
        '(including the CFA Institute Code of Ethics and Standards of Professional Conduct) of any government, '
        'regulatory organization, licensing agency, or professional association governing their professional '
        'activities. In the event of conflict, Members and Candidates must comply with the more strict law, '
        'rule, or regulation. Members and Candidates must not knowingly participate or assist in and must '
        'dissociate from any violation of such laws, rules, or regulations.'
    )

    pdf.section_heading('Guidance', level=3)
    pdf.body_text(
        'Members and candidates must understand the applicable laws and regulations of the countries and '
        'jurisdictions where they do business. They do not need to become legal experts, but they must have '
        'sufficient knowledge to recognize situations that could result in violations. When in doubt, members '
        'should seek the advice of compliance personnel or legal counsel.'
    )
    pdf.body_text(
        'The "more strict law" principle is critical. When members and candidates operate in multiple jurisdictions '
        'or when the Code and Standards impose a higher standard than local law, they must comply with the more '
        'strict requirement. The Code and Standards do not ask members to violate local law; rather, they require '
        'members to follow the higher standard where it does not conflict with local law.'
    )
    pdf.body_text(
        'Key aspects of this standard include:'
    )
    pdf.bullet_point('Relationship between the Code and Standards and applicable law: When the Code and Standards require conduct that is more restrictive than applicable law, members must adhere to the Code and Standards.')
    pdf.bullet_point('Participation in or association with violations by others: Members must not knowingly participate or assist in violations. If they become aware of violations, they must take steps to dissociate from the violating activity.')
    pdf.bullet_point('Investment products and applicable laws: Members must be aware of the laws governing the investment products they deal with, particularly when dealing with products across multiple jurisdictions.')

    pdf.section_heading('Dissociation', level=3)
    pdf.body_text(
        'When members become aware that their employer or a colleague is engaged in illegal or unethical activity, '
        'they must dissociate from the activity. This means they must:'
    )
    pdf.bullet_point('Remove their name from any reports or documents associated with the violation')
    pdf.bullet_point('Report the violation to their supervisor or compliance department')
    pdf.bullet_point('If the firm does not address the violation, consider reporting to the appropriate regulatory authority')
    pdf.bullet_point('In extreme cases, resignation from the firm may be necessary to fully dissociate from the violation')
    pdf.body_text(
        'Simple inaction (i.e., doing nothing) is not sufficient to constitute dissociation. Members must take '
        'affirmative steps to distance themselves from the unethical or illegal activity. However, members are '
        'not required to report violations to governmental or regulatory authorities unless such reporting is '
        'required by law. CFA Institute strongly encourages members to report violations if appropriate.'
    )

    pdf.section_heading('Recommended Procedures for Standard I(A)', level=3)
    pdf.body_text('Members and candidates should:')
    pdf.bullet_point('Maintain current knowledge of applicable laws, rules, and regulations')
    pdf.bullet_point('Regularly review written compliance procedures')
    pdf.bullet_point('When in doubt about the legality or appropriateness of any action, consult with compliance personnel or legal counsel')
    pdf.body_text('Firms should:')
    pdf.bullet_point('Provide readily available written compliance procedures to employees')
    pdf.bullet_point('Maintain a compliance monitoring program')
    pdf.bullet_point('Provide legal guidance on the applicable laws and regulations in each jurisdiction')
    pdf.bullet_point('Establish clear procedures for reporting and investigating potential violations')

    # I(B) Independence and Objectivity
    pdf.section_heading('Standard I(B): Independence and Objectivity', level=2)
    pdf.body_text(
        'Members and Candidates must use reasonable care and judgment to achieve and maintain independence and '
        'objectivity in their professional activities. Members and Candidates must not offer, solicit, or accept '
        'any gift, benefit, compensation, or consideration that reasonably could be expected to compromise their '
        'own or another\'s independence and objectivity.'
    )

    pdf.section_heading('Guidance', level=3)
    pdf.body_text(
        'Independence and objectivity are essential qualities for investment professionals. Clients and the public '
        'depend on investment professionals to provide honest, unbiased analysis and recommendations. Any influence '
        'that compromises this independence and objectivity undermines the trust that is fundamental to the profession.'
    )
    pdf.body_text(
        'Threats to independence and objectivity can come from many sources, including:'
    )
    pdf.bullet_point('Investment banking relationships: Pressure from investment banking divisions to issue favorable research reports on companies that are clients of the investment bank.')
    pdf.bullet_point('Corporate issuer relationships: Companies may offer analysts special access, trips, or other incentives in exchange for favorable coverage.')
    pdf.bullet_point('Gifts and entertainment: Clients, vendors, or other parties may offer gifts, meals, or entertainment that could influence professional judgment.')
    pdf.bullet_point('Travel expenses: Acceptance of travel expenses paid by third parties can create the appearance of compromised independence.')
    pdf.bullet_point('Compensation arrangements: Performance-based compensation tied to specific outcomes can create conflicts of interest.')
    pdf.bullet_point('Intrafirm pressure: Pressure from colleagues or supervisors within the firm to modify analysis or recommendations.')

    pdf.body_text(
        'Members should evaluate the nature and value of any gift, benefit, or consideration offered. Modest gifts '
        'and entertainment that are customary in business (such as occasional meals or small gifts) generally do not '
        'compromise independence and objectivity. However, lavish gifts, expensive trips, or other significant '
        'benefits can create obligations or the appearance of compromise and should be declined or disclosed.'
    )

    pdf.body_text(
        'Special considerations for buy-side analysts: Buy-side analysts and portfolio managers must maintain '
        'their objectivity when evaluating sell-side research. They should not let relationships with sell-side '
        'analysts or the provision of services by sell-side firms influence their investment decisions.'
    )

    pdf.body_text(
        'Special considerations for issuer-paid research: When research is paid for by the company being analyzed, '
        'there is an inherent conflict of interest. Members who produce issuer-paid research must disclose the fact '
        'that they are being paid by the issuer and must take steps to ensure that their analysis remains objective.'
    )

    pdf.section_heading('Recommended Procedures for Standard I(B)', level=3)
    pdf.bullet_point('Establish policies limiting the value and frequency of gifts and entertainment that employees may accept')
    pdf.bullet_point('Create restricted lists of securities about which the firm has material nonpublic information')
    pdf.bullet_point('Restrict employee participation in IPOs')
    pdf.bullet_point('Implement review procedures for research reports, particularly when the firm has investment banking relationships with the subject company')
    pdf.bullet_point('Establish firewalls between research and investment banking departments')
    pdf.bullet_point('Require disclosure of all conflicts of interest')
    pdf.bullet_point('Implement a policy for reporting gifts and entertainment received from external sources')

    # I(C) Misrepresentation
    pdf.section_heading('Standard I(C): Misrepresentation', level=2)
    pdf.body_text(
        'Members and Candidates must not knowingly make any misrepresentations relating to investment analysis, '
        'recommendations, actions, or other professional activities.'
    )

    pdf.section_heading('Guidance', level=3)
    pdf.body_text(
        'Misrepresentation is any untrue statement or omission of a fact, or any statement that is otherwise false '
        'or misleading. A misrepresentation can involve both affirmative statements (actively making false claims) '
        'and omissions (failing to disclose relevant information).'
    )
    pdf.body_text(
        'This standard covers a broad range of communications, including:'
    )
    pdf.bullet_point('Oral and written communications to clients, prospective clients, and the public')
    pdf.bullet_point('Marketing materials and advertisements')
    pdf.bullet_point('Performance presentations')
    pdf.bullet_point('Research reports and investment recommendations')
    pdf.bullet_point('Resumes and qualification summaries')
    pdf.bullet_point('Social media posts and online communications')

    pdf.body_text(
        'Common forms of misrepresentation include:'
    )
    pdf.bullet_point('Guaranteeing investment performance or returns')
    pdf.bullet_point('Exaggerating qualifications or experience')
    pdf.bullet_point('Misrepresenting the services that can be provided')
    pdf.bullet_point('Cherry-picking favorable performance data while omitting unfavorable results')
    pdf.bullet_point('Presenting simulated or backtested results as actual performance')
    pdf.bullet_point('Copying or using the work of others without acknowledgment (plagiarism)')
    pdf.bullet_point('Omitting material information that would affect a client\'s decision')

    pdf.section_heading('Plagiarism', level=3)
    pdf.body_text(
        'Plagiarism is a specific form of misrepresentation that involves using the work of others (ideas, '
        'analysis, charts, graphs, or text) without giving proper attribution. This standard prohibits plagiarism '
        'in any form. Members must give credit to the original source when using the work of others.'
    )
    pdf.body_text(
        'Types of plagiarism include:'
    )
    pdf.bullet_point('Taking a research report or analysis written by another firm and presenting it under one\'s own name')
    pdf.bullet_point('Using excerpts from articles or reports without acknowledgment')
    pdf.bullet_point('Presenting statistical estimates or forecasts prepared by others as one\'s own work')
    pdf.bullet_point('Using charts, graphs, or other visual materials without attribution')
    pdf.body_text(
        'It is important to note that using widely recognized financial data or general public knowledge does not '
        'constitute plagiarism. For example, stating that a company\'s P/E ratio is a certain value, when that '
        'data is widely available from multiple sources, does not require specific attribution.'
    )

    pdf.section_heading('Recommended Procedures for Standard I(C)', level=3)
    pdf.bullet_point('Develop procedures to verify the accuracy of all information presented to clients and the public')
    pdf.bullet_point('Maintain records of the sources of information used in reports and presentations')
    pdf.bullet_point('Establish review procedures for marketing materials and performance presentations')
    pdf.bullet_point('Develop a plagiarism policy that requires proper attribution of the work of others')
    pdf.bullet_point('Keep qualification summaries and resumes up to date and accurate')
    pdf.bullet_point('Regularly review the firm\'s website and other public communications for accuracy')

    # I(D) Misconduct
    pdf.section_heading('Standard I(D): Misconduct', level=2)
    pdf.body_text(
        'Members and Candidates must not engage in any professional conduct involving dishonesty, fraud, or '
        'deceit or commit any act that reflects adversely on their professional reputation, integrity, or competence.'
    )

    pdf.section_heading('Guidance', level=3)
    pdf.body_text(
        'This standard addresses personal behavior that reflects on the member\'s or candidate\'s professional '
        'life. It is not intended to cover all aspects of a member\'s personal life; rather, it focuses on '
        'conduct that could diminish the confidence of the investing public in the investment profession.'
    )
    pdf.body_text(
        'Any act that involves lying, cheating, stealing, or other dishonest conduct is a violation if the '
        'offense reflects on the member\'s or candidate\'s integrity, competence, or professional reputation. '
        'Misconduct does not have to be related to the member\'s professional activities to violate this standard. '
        'Personal conduct that brings dishonor to the profession can be grounds for discipline.'
    )
    pdf.body_text(
        'Examples of behavior that would violate this standard include:'
    )
    pdf.bullet_point('Criminal convictions for fraud, theft, or other dishonest acts')
    pdf.bullet_point('Using the CFA designation to commit fraud')
    pdf.bullet_point('Personally fraudulent behavior even if not directly related to investment activities')
    pdf.bullet_point('Substance abuse that impairs professional judgment or competence')

    # I(E) Competence
    pdf.section_heading('Standard I(E): Competence', level=2)
    pdf.body_text(
        'Members and Candidates must act with and maintain the competence necessary to fulfill their professional '
        'responsibilities.'
    )

    pdf.section_heading('Guidance', level=3)
    pdf.body_text(
        'This standard, added in the 2023 revisions, requires members and candidates to maintain the knowledge, '
        'skills, and abilities needed to perform their professional duties. Given the diverse range of professional '
        'services engaged in by members, the specific competence requirements will vary according to the nature '
        'of their professional duties.'
    )
    pdf.body_text(
        'Key aspects of this standard include:'
    )
    pdf.bullet_point('Members must have the competence necessary for their current role before undertaking professional responsibilities.')
    pdf.bullet_point('As roles expand or change, members must develop new competencies as needed.')
    pdf.bullet_point('Members should stay current with developments in their area of expertise, including new financial products, analytical techniques, and regulatory changes.')
    pdf.bullet_point('This standard does not require participation in any specific continuing education program, but members must be able to demonstrate competence in their professional activities.')
    pdf.bullet_point('Supervisors have a responsibility to ensure that the people they supervise are competent to perform their duties.')

    # ---- STANDARD II: INTEGRITY OF CAPITAL MARKETS ----
    pdf.section_heading('STANDARD II: INTEGRITY OF CAPITAL MARKETS')

    # II(A) Material Nonpublic Information
    pdf.section_heading('Standard II(A): Material Nonpublic Information', level=2)
    pdf.body_text(
        'Members and Candidates who possess material nonpublic information that could affect the value of an '
        'investment must not act or cause others to act on the information.'
    )

    pdf.section_heading('Guidance', level=3)
    pdf.body_text(
        'This standard is designed to prevent insider trading and the misuse of material nonpublic information. '
        'Trading on material nonpublic information undermines market integrity and the confidence of investors '
        'in the fairness of capital markets.'
    )

    pdf.body_text('What is "Material" Information?')
    pdf.body_text(
        'Information is "material" if its disclosure would be likely to have an impact on the price of a security '
        'or if reasonable investors would want to know the information before making an investment decision. '
        'In general, information about the following is likely to be material:'
    )
    pdf.bullet_point('Earnings and revenue information')
    pdf.bullet_point('Mergers, acquisitions, tender offers, or joint ventures')
    pdf.bullet_point('Changes in assets or asset quality')
    pdf.bullet_point('Innovative products, processes, or discoveries')
    pdf.bullet_point('New licenses, patents, or registered trademarks')
    pdf.bullet_point('Developments regarding customers or suppliers')
    pdf.bullet_point('Changes in management or corporate structure')
    pdf.bullet_point('Forthcoming dividends or stock splits')
    pdf.bullet_point('Offering of additional securities')
    pdf.bullet_point('Regulatory or legal developments')
    pdf.bullet_point('Significant financial distress')

    pdf.body_text('What is "Nonpublic" Information?')
    pdf.body_text(
        'Information is "nonpublic" until it has been disseminated or is available to the marketplace in general '
        '(as opposed to a select group of investors). "Disseminated" means the information has been communicated '
        'to the marketplace at large through recognized channels of distribution, such as major news services, '
        'SEC filings, company press releases, or widely disseminated news sources.'
    )
    pdf.body_text(
        'Merely knowing that the information will become public soon does not make it "public." Until the '
        'information is actually disseminated to the marketplace, it remains nonpublic and cannot be acted upon.'
    )

    pdf.section_heading('Mosaic Theory', level=3)
    pdf.body_text(
        'The mosaic theory is an important concept that allows analysts to combine nonmaterial nonpublic information '
        'with publicly available information to form an investment conclusion. Under this theory, an analyst can '
        'reach an investment conclusion about a corporate action or event through an analysis of public information '
        'together with nonmaterial nonpublic information, without violating this standard.'
    )
    pdf.body_text(
        'For example, an analyst who visits a company and observes that the factory floor is unusually busy may '
        'combine this observation (nonmaterial nonpublic information) with publicly available data about the company '
        'to reach a conclusion about the company\'s performance. This is permissible under the mosaic theory because '
        'the individual pieces of nonpublic information are not material on their own.'
    )
    pdf.body_text(
        'However, analysts must be careful not to use the mosaic theory as a justification for trading on material '
        'nonpublic information. If a single piece of information is material and nonpublic, it cannot be used as the '
        'basis for trading, regardless of how it was obtained.'
    )

    pdf.section_heading('Recommended Procedures for Standard II(A)', level=3)
    pdf.bullet_point('Achieve public dissemination of material information before acting on it')
    pdf.bullet_point('Adopt compliance procedures to prevent misuse of material nonpublic information')
    pdf.bullet_point('Establish information barriers ("firewalls") between departments that regularly possess material nonpublic information and those that trade securities')
    pdf.bullet_point('Maintain restricted lists of securities about which the firm has material nonpublic information')
    pdf.bullet_point('Monitor employee trading activities')
    pdf.bullet_point('Issue press releases to ensure wide dissemination of material information')
    pdf.bullet_point('Limit personal trading by employees who have access to material nonpublic information')
    pdf.bullet_point('Maintain records of information received and steps taken to determine whether it is material and/or nonpublic')

    # II(B) Market Manipulation
    pdf.section_heading('Standard II(B): Market Manipulation', level=2)
    pdf.body_text(
        'Members and Candidates must not engage in practices that distort prices or artificially inflate '
        'trading volume with the intent to mislead market participants.'
    )

    pdf.section_heading('Guidance', level=3)
    pdf.body_text(
        'This standard prohibits any activity that is designed to deceive market participants by distorting the '
        'price-setting mechanism of financial instruments or by artificially inflating trading volume. Market '
        'manipulation undermines the integrity and fairness of capital markets.'
    )
    pdf.body_text(
        'Market manipulation can take two general forms:'
    )
    pdf.bullet_point('Information-based manipulation: Spreading false or misleading information about a company or security to influence its price. This includes "pump and dump" schemes, where false positive information is spread to inflate a stock\'s price, and then the perpetrator sells at the inflated price.')
    pdf.bullet_point('Transaction-based manipulation: Engaging in transactions that are designed to create a misleading impression of trading activity or price levels. This includes wash trading (buying and selling the same security to create the appearance of trading activity), marking the close (placing trades near market close to influence closing prices), and spoofing (placing orders with no intention of executing them).')

    pdf.body_text(
        'It is important to note that legitimate trading strategies that may result in price changes are not '
        'considered market manipulation. The key factor is intent - whether the trading activity is designed '
        'to mislead other market participants.'
    )

    # ---- STANDARD III: DUTIES TO CLIENTS ----
    pdf.section_heading('STANDARD III: DUTIES TO CLIENTS')

    # III(A) Loyalty, Prudence, and Care
    pdf.section_heading('Standard III(A): Loyalty, Prudence, and Care', level=2)
    pdf.body_text(
        'Members and Candidates have a duty of loyalty to their clients and must act with reasonable care and '
        'exercise prudent judgment. Members and Candidates must act for the benefit of their clients and place '
        'their clients\' interests before their employer\'s or their own interests.'
    )

    pdf.section_heading('Guidance', level=3)
    pdf.body_text(
        'This standard sets out the fiduciary duty that members and candidates owe to their clients. It requires '
        'them to act in the best interests of clients and to exercise the care, skill, and diligence that a '
        'prudent person acting in a like capacity and familiar with such matters would use.'
    )
    pdf.body_text(
        'Key aspects of this standard include:'
    )
    pdf.bullet_point('Identifying the client: Members must clearly identify who their client is. In some cases, this is straightforward (e.g., an individual investor). In other cases, it may be more complex (e.g., a pension fund manager must consider whether the client is the plan sponsor, the plan participants, or both).')
    pdf.bullet_point('Duty of loyalty: Members must act in the best interests of their clients. This includes avoiding conflicts of interest and ensuring that personal or firm interests do not take priority over client interests.')
    pdf.bullet_point('Prudence and care: Members must exercise the level of care, skill, and diligence that a prudent professional would exercise. This includes conducting thorough research, diversifying investments appropriately, and monitoring portfolios regularly.')
    pdf.bullet_point('Soft dollar arrangements: Members must ensure that any soft dollar arrangements (using client commissions to pay for research or other services) benefit the client. The use of client brokerage should be directed to the benefit of clients.')
    pdf.bullet_point('Proxy voting: Members who have the authority to vote proxies on behalf of clients must do so in the best interests of clients. They should establish written policies for proxy voting.')

    pdf.section_heading('Recommended Procedures for Standard III(A)', level=3)
    pdf.bullet_point('Regularly provide account information to clients, including asset allocation, portfolio performance, and fees charged')
    pdf.bullet_point('Obtain client approval for actions that deviate from the established investment strategy')
    pdf.bullet_point('Establish firm-wide policies and procedures that promote the interests of clients')
    pdf.bullet_point('Follow applicable rules for managing client assets and maintaining appropriate controls')
    pdf.bullet_point('Establish and maintain a system for vote proxies in clients\' best interests')

    # III(B) Fair Dealing
    pdf.section_heading('Standard III(B): Fair Dealing', level=2)
    pdf.body_text(
        'Members and Candidates must deal fairly and objectively with all clients when providing investment '
        'analysis, making investment recommendations, taking investment action, or engaging in other '
        'professional activities.'
    )

    pdf.section_heading('Guidance', level=3)
    pdf.body_text(
        'This standard does not require identical treatment of all clients, but it does require fair treatment. '
        'Different levels of service may be offered to different clients (e.g., premium service for larger accounts), '
        'but differences in service must be disclosed and must not disadvantage any client.'
    )
    pdf.body_text(
        'Key aspects of fair dealing include:'
    )
    pdf.bullet_point('Investment recommendations: When making a change in a recommendation, members must ensure that all clients are informed fairly. No client should receive preferential access to changes in recommendations.')
    pdf.bullet_point('Investment actions: When taking investment actions (such as placing trades), members must ensure fair allocation among clients. This includes fair allocation of IPO shares and other new offerings.')
    pdf.bullet_point('Simultaneous dissemination: Members should disseminate investment recommendations and material changes to recommendations to all clients simultaneously. If simultaneous dissemination is not possible, the order of dissemination should be designed to be fair.')
    pdf.bullet_point('Pro rata allocation: When supply is limited (e.g., in an IPO), allocations should be made on a pro rata basis to ensure fair treatment.')

    pdf.section_heading('Recommended Procedures for Standard III(B)', level=3)
    pdf.bullet_point('Develop firm policies for fair dissemination of investment recommendations')
    pdf.bullet_point('Establish procedures for equitable trade allocation')
    pdf.bullet_point('Disclose trade allocation procedures to clients')
    pdf.bullet_point('Establish systematic account review processes')
    pdf.bullet_point('Disclose different levels of service available to clients')
    pdf.bullet_point('Limit the number of people who have advance knowledge of recommendation changes')
    pdf.bullet_point('Shorten the time between investment decision and trading')

    # III(C) Suitability
    pdf.section_heading('Standard III(C): Suitability', level=2)
    pdf.body_text(
        'When Members and Candidates are in an advisory relationship with a client, they must:'
    )
    pdf.bullet_point('Make a reasonable inquiry into a client\'s or prospective client\'s investment experience, risk and return objectives, and financial constraints prior to making any investment recommendation or taking investment action and must reassess and update this information regularly.')
    pdf.bullet_point('Determine that an investment is suitable to the client\'s financial situation and consistent with the client\'s written objectives, mandates, and constraints before making an investment recommendation or taking investment action.')
    pdf.bullet_point('Judge the suitability of investments in the context of the client\'s total portfolio.')
    pdf.body_text(
        'When Members and Candidates are responsible for managing a portfolio to a specific mandate, strategy, '
        'or style, they must make only investment recommendations or take only investment actions that are '
        'consistent with the stated objectives and constraints of the portfolio.'
    )

    pdf.section_heading('Guidance', level=3)
    pdf.body_text(
        'Suitability is a fundamental concept in the investment profession. It requires that investment '
        'professionals understand their clients\' needs, circumstances, and objectives before making recommendations '
        'or taking actions on their behalf.'
    )
    pdf.body_text(
        'Key aspects include:'
    )
    pdf.bullet_point('Investment Policy Statement (IPS): Members should develop and maintain an IPS for each client that documents the client\'s investment objectives, risk tolerance, time horizon, income needs, liquidity requirements, tax considerations, legal restrictions, and unique circumstances.')
    pdf.bullet_point('Regular updates: The IPS should be reviewed and updated regularly to reflect changes in the client\'s circumstances, objectives, or financial situation.')
    pdf.bullet_point('Total portfolio context: The suitability of an individual investment should be judged in the context of the client\'s entire portfolio, not in isolation. A risky investment may be suitable as part of a diversified portfolio even if it would be unsuitable on its own.')
    pdf.bullet_point('Mandate-based portfolios: When managing a portfolio to a specific mandate (e.g., a small-cap growth fund), the member must ensure that investment actions are consistent with the mandate, even if individual clients who invest in the fund might have different personal objectives.')

    # III(D) Performance Presentation
    pdf.section_heading('Standard III(D): Performance Presentation', level=2)
    pdf.body_text(
        'When communicating investment performance information, Members and Candidates must make reasonable '
        'efforts to ensure that it is fair, accurate, and complete.'
    )

    pdf.section_heading('Guidance', level=3)
    pdf.body_text(
        'This standard requires members to present performance information in a way that is not misleading. '
        'Key requirements include:'
    )
    pdf.bullet_point('Do not misrepresent past performance or reasonably expected performance')
    pdf.bullet_point('Include terminated accounts in performance history to avoid survivorship bias')
    pdf.bullet_point('Present performance of a weighted composite of similar portfolios rather than a single representative account')
    pdf.bullet_point('Clearly distinguish between simulated/backtested performance and actual performance')
    pdf.bullet_point('Disclose the calculation methodology used for performance figures')
    pdf.bullet_point('Include relevant contextual information such as benchmarks, risk measures, and market conditions')
    pdf.bullet_point('Do not cherry-pick favorable time periods or accounts for performance presentation')
    pdf.bullet_point('When presenting results from a prior firm or employer, clearly state that the track record was achieved while at a different firm')

    pdf.section_heading('Recommended Procedures for Standard III(D)', level=3)
    pdf.body_text(
        'The best way to comply with this standard is to adopt and comply with the Global Investment Performance '
        'Standards (GIPS). If not applying GIPS, members should:'
    )
    pdf.bullet_point('Consider the audience when presenting performance data')
    pdf.bullet_point('Include all relevant details needed for a fair presentation')
    pdf.bullet_point('Use a recognized calculation methodology consistently')
    pdf.bullet_point('Present composite performance rather than individual account performance where appropriate')
    pdf.bullet_point('Maintain records supporting all performance presentations')

    # III(E) Preservation of Confidentiality
    pdf.section_heading('Standard III(E): Preservation of Confidentiality', level=2)
    pdf.body_text(
        'Members and Candidates must keep information about current, former, and prospective clients confidential '
        'unless: (1) the information concerns illegal activities on the part of the client or prospective client, '
        '(2) disclosure is required by law, or (3) the client or prospective client permits disclosure of the '
        'information.'
    )

    pdf.section_heading('Guidance', level=3)
    pdf.body_text(
        'Members must maintain the confidentiality of all client information, including:'
    )
    pdf.bullet_point('Client identity and personal information')
    pdf.bullet_point('Account information, portfolio holdings, and transaction history')
    pdf.bullet_point('Investment objectives and strategies')
    pdf.bullet_point('Financial information and tax status')
    pdf.body_text(
        'This duty of confidentiality applies not only during the client relationship but also after the '
        'relationship has ended. Former clients\' information must be treated with the same care as current '
        'clients\' information.'
    )
    pdf.body_text(
        'Exceptions to confidentiality:'
    )
    pdf.bullet_point('Illegal activities: If a member becomes aware that a client is engaged in illegal activities, the member may have an obligation to report such activities to the appropriate authorities, depending on applicable law.')
    pdf.bullet_point('Required by law: If disclosure is required by law or regulation, the member must comply with the legal requirement.')
    pdf.bullet_point('Client permission: If the client gives permission for disclosure, the member may share the information as authorized.')

    pdf.section_heading('Recommended Procedures for Standard III(E)', level=3)
    pdf.bullet_point('Establish procedures for secure storage and transmission of client information')
    pdf.bullet_point('Limit access to confidential client information to authorized personnel only')
    pdf.bullet_point('Communicate clearly with clients about what information is collected and how it will be used')
    pdf.bullet_point('Properly dispose of confidential documents when no longer needed')

    # ---- STANDARD IV: DUTIES TO EMPLOYERS ----
    pdf.section_heading('STANDARD IV: DUTIES TO EMPLOYERS')

    # IV(A) Loyalty
    pdf.section_heading('Standard IV(A): Loyalty', level=2)
    pdf.body_text(
        'In matters related to their employment, Members and Candidates must act for the benefit of their '
        'employer and not deprive their employer of the advantage of their skills and abilities, divulge '
        'confidential information, or otherwise cause harm to their employer.'
    )

    pdf.section_heading('Guidance', level=3)
    pdf.body_text(
        'Members and candidates owe a duty of loyalty to their employer. This duty requires them to act in '
        'the best interests of their employer and to protect the employer\'s confidential information and '
        'intellectual property.'
    )
    pdf.body_text(
        'Key aspects of this standard include:'
    )
    pdf.bullet_point('Employer vs. client interests: When employer and client interests conflict, the client\'s interests must take priority. The duty to clients supersedes the duty to employers.')
    pdf.bullet_point('Independent practice: Members who wish to engage in independent practice (providing services to clients outside of their employer) must obtain written consent from their employer before doing so.')
    pdf.bullet_point('Leaving an employer: When planning to leave an employer, members should not solicit clients or take proprietary information before their departure. After leaving, they may contact former clients as long as they do not use confidential information obtained from the former employer.')
    pdf.bullet_point('Whistleblowing: If a member discovers that their employer is engaged in illegal or unethical activity, the duty to report may override the duty of loyalty to the employer. Members should not be deterred from reporting violations out of a misplaced sense of loyalty.')
    pdf.bullet_point('Nature of employment: The duty of loyalty applies regardless of the nature of the employment relationship (full-time, part-time, contractor). However, the specific obligations may vary depending on the terms of the employment agreement.')

    pdf.body_text(
        'Employer property: Work products created during employment typically belong to the employer. Members '
        'should not take work products, client lists, investment models, or other proprietary materials when '
        'leaving an employer. However, members may retain general knowledge and skills developed during employment.'
    )

    pdf.section_heading('Recommended Procedures for Standard IV(A)', level=3)
    pdf.bullet_point('Establish clear competition policies that define what constitutes competing with the employer')
    pdf.bullet_point('Create termination policies that specify the obligations of departing employees')
    pdf.bullet_point('Implement incident-reporting procedures for reporting suspected violations')
    pdf.bullet_point('Clearly classify employees (full-time, part-time, independent contractor) and communicate corresponding obligations')

    # IV(B) Additional Compensation Arrangements
    pdf.section_heading('Standard IV(B): Additional Compensation Arrangements', level=2)
    pdf.body_text(
        'Members and Candidates must not accept gifts, benefits, compensation, or consideration that competes '
        'with or might reasonably be expected to create a conflict of interest with their employer\'s interest '
        'unless they obtain written consent from all parties involved.'
    )

    pdf.section_heading('Guidance', level=3)
    pdf.body_text(
        'This standard requires members to obtain written consent from their employer before accepting any '
        'additional compensation or benefits from clients or other parties that could create a conflict of '
        'interest. The employer must be made aware of the arrangement so that they can evaluate its impact '
        'on the member\'s objectivity and loyalty.'
    )
    pdf.body_text(
        'Compensation arrangements that must be disclosed include:'
    )
    pdf.bullet_point('Bonus payments from clients for exceptional performance')
    pdf.bullet_point('Referral fees from third parties')
    pdf.bullet_point('Side arrangements to receive additional compensation based on performance')
    pdf.bullet_point('Gifts of significant value from clients')
    pdf.bullet_point('Compensation for outside activities that compete with or relate to the employer\'s business')

    # IV(C) Responsibilities of Supervisors
    pdf.section_heading('Standard IV(C): Responsibilities of Supervisors', level=2)
    pdf.body_text(
        'Members and Candidates must make reasonable efforts to ensure that anyone subject to their supervision '
        'or authority complies with applicable laws, rules, regulations, and the Code and Standards.'
    )

    pdf.section_heading('Guidance', level=3)
    pdf.body_text(
        'This standard applies to anyone who has supervisory responsibility, whether or not they hold a '
        'formal title of supervisor. Members who delegate tasks to others are still responsible for ensuring '
        'that those tasks are performed in compliance with applicable laws and ethical standards.'
    )
    pdf.body_text(
        'Key aspects include:'
    )
    pdf.bullet_point('Reasonable efforts: Supervisors must make reasonable efforts to detect and prevent violations. What constitutes "reasonable" depends on the nature of the activities supervised and the resources available.')
    pdf.bullet_point('Compliance system: Supervisors should establish, or encourage the establishment of, a compliance system that is adequate to detect and prevent violations.')
    pdf.bullet_point('Detection of violations: If a supervisor learns of a violation or potential violation, they must promptly investigate and take appropriate corrective action.')
    pdf.bullet_point('Inadequate compliance procedures: If the firm\'s compliance system is inadequate, the supervisor must take steps to have it improved. If the firm does not improve its compliance system, the supervisor should document their concerns and consider whether continued association with the firm is appropriate.')

    pdf.section_heading('Recommended Procedures for Standard IV(C)', level=3)
    pdf.bullet_point('Establish written codes of ethics and compliance procedures')
    pdf.bullet_point('Ensure that compliance procedures are adequate to detect and prevent violations')
    pdf.bullet_point('Implement compliance education and training programs')
    pdf.bullet_point('Establish an appropriate incentive structure that does not encourage unethical behavior')
    pdf.bullet_point('Create and maintain a system for monitoring employee activities')
    pdf.bullet_point('Respond promptly to detected violations or potential violations')
    pdf.bullet_point('Keep records of compliance activities and investigations')

    # ---- STANDARD V: INVESTMENT ANALYSIS, RECOMMENDATIONS, AND ACTIONS ----
    pdf.section_heading('STANDARD V: INVESTMENT ANALYSIS, RECOMMENDATIONS, AND ACTIONS')

    # V(A) Diligence and Reasonable Basis
    pdf.section_heading('Standard V(A): Diligence and Reasonable Basis', level=2)
    pdf.body_text(
        'Members and Candidates must:'
    )
    pdf.bullet_point('Exercise diligence, independence, and thoroughness in analyzing investments, making investment recommendations, and taking investment actions.')
    pdf.bullet_point('Have a reasonable and adequate basis, supported by appropriate research and investigation, for any investment analysis, recommendation, or action.')

    pdf.section_heading('Guidance', level=3)
    pdf.body_text(
        'This standard requires members to conduct thorough analysis before making investment recommendations '
        'or taking investment actions. The level of diligence required will depend on the complexity of the '
        'investment and the nature of the professional\'s role.'
    )
    pdf.body_text(
        'Key aspects include:'
    )
    pdf.bullet_point('Reasonable basis: The level of research required depends on the product or security complexity, the member\'s role (e.g., portfolio manager vs. retail adviser), and available resources. More complex investments require more rigorous analysis.')
    pdf.bullet_point('Using secondary or third-party research: Members may use research produced by others, but they must verify that the research was conducted with appropriate diligence and that the assumptions and methodology are sound.')
    pdf.bullet_point('Quantitative models: When using quantitative models, members must understand the models\' assumptions, limitations, and risks. They should not rely blindly on model outputs.')
    pdf.bullet_point('Group research and decision-making: When investment decisions are made by a group or committee, each member should be satisfied with the process and the basis for the decision. A member who disagrees with a group recommendation should document their dissent.')
    pdf.bullet_point('Selecting external advisers and subadvisers: Members responsible for selecting external advisers or subadvisers must exercise due diligence in the selection process, including reviewing the adviser\'s qualifications, track record, compliance history, and investment process.')

    # V(B) Communication with Clients
    pdf.section_heading('Standard V(B): Communication with Clients and Prospective Clients', level=2)
    pdf.body_text(
        'Members and Candidates must:'
    )
    pdf.bullet_point('Disclose to clients and prospective clients the nature of the services provided, along with information about the costs to the client associated with those services.')
    pdf.bullet_point('Disclose to clients and prospective clients the basic format and general principles of the investment processes they use to analyze investments, select securities, and construct portfolios and must promptly disclose any changes that might materially affect those processes.')
    pdf.bullet_point('Distinguish between fact and opinion in the presentation of investment analysis and recommendations.')
    pdf.bullet_point('Use reasonable judgment in identifying which factors are important to their investment analyses, recommendations, or actions and include those factors in communications with clients and prospective clients.')

    pdf.section_heading('Guidance', level=3)
    pdf.body_text(
        'This standard requires clear, complete, and timely communication with clients. Members must ensure that '
        'clients have the information they need to make informed decisions about their investments.'
    )
    pdf.body_text(
        'Key aspects include:'
    )
    pdf.bullet_point('Nature of services and costs: Members must clearly communicate the services they provide and the associated costs, including management fees, performance fees, trading costs, and any other charges that the client will bear.')
    pdf.bullet_point('Investment process disclosure: Members must explain their investment approach and methodology in sufficient detail for clients to evaluate and understand the process.')
    pdf.bullet_point('Fact vs. opinion: Members must clearly distinguish between statements of fact and opinions. Investment projections, forecasts, and target prices are opinions and should be clearly identified as such.')
    pdf.bullet_point('Material changes: When there are material changes to the investment process, risk characteristics, or other factors that could affect clients, members must promptly communicate these changes.')
    pdf.bullet_point('Risk and limitations: Members must disclose significant risks and limitations associated with the investment process, including limitations of quantitative models and data used.')

    # V(C) Record Retention
    pdf.section_heading('Standard V(C): Record Retention', level=2)
    pdf.body_text(
        'Members and Candidates must develop and maintain appropriate records to support their investment '
        'analyses, recommendations, actions, and other investment-related communications with clients and '
        'prospective clients.'
    )

    pdf.section_heading('Guidance', level=3)
    pdf.body_text(
        'This standard requires members to maintain records that support their professional activities. Proper '
        'record retention serves several important purposes:'
    )
    pdf.bullet_point('It provides evidence of the basis for investment recommendations and actions')
    pdf.bullet_point('It helps protect the member and the firm in the event of disputes or regulatory inquiries')
    pdf.bullet_point('It ensures continuity when employees change roles or leave the firm')
    pdf.bullet_point('It helps demonstrate compliance with applicable laws and regulations')

    pdf.body_text(
        'Records are the property of the firm, not the individual employee. When members leave a firm, they '
        'cannot take records with them (unless permitted by the firm). However, members should not rely solely '
        'on their employer to maintain their records; they should take reasonable steps to ensure that their '
        'records are properly maintained.'
    )
    pdf.body_text(
        'In the absence of specific regulatory requirements, CFA Institute recommends maintaining records for '
        'at least seven years.'
    )

    # ---- STANDARD VI: CONFLICTS OF INTEREST ----
    pdf.section_heading('STANDARD VI: CONFLICTS OF INTEREST')

    # VI(A) Avoid or Disclose Conflicts
    pdf.section_heading('Standard VI(A): Avoid or Disclose Conflicts', level=2)
    pdf.body_text(
        'Members and Candidates must:'
    )
    pdf.bullet_point('Avoid or make full and fair disclosure of all matters that could reasonably be expected to impair their independence and objectivity and interfere with respective duties to their clients, prospective clients, and employer.')
    pdf.bullet_point('Ensure that such disclosures are prominent, are delivered in plain language, and communicate the relevant information effectively.')

    pdf.section_heading('Guidance', level=3)
    pdf.body_text(
        'Conflicts of interest are unavoidable in the investment profession. This standard recognizes this reality '
        'and requires members either to avoid conflicts where possible or to disclose them when avoidance is not '
        'feasible. The 2023 revision to this standard added the explicit option to "avoid" conflicts, emphasizing '
        'that avoidance is preferred over mere disclosure.'
    )
    pdf.body_text(
        'Common types of conflicts that must be disclosed or avoided include:'
    )
    pdf.bullet_point('Ownership of securities that are the subject of investment recommendations or actions')
    pdf.bullet_point('Board service or other relationships with companies covered in research')
    pdf.bullet_point('Business relationships that might influence investment recommendations')
    pdf.bullet_point('Compensation structures that create incentives to recommend certain products')
    pdf.bullet_point('Family relationships with other market participants')
    pdf.bullet_point('Outside business activities that might compete with or influence the member\'s professional activities')

    pdf.body_text(
        'Disclosure must be:'
    )
    pdf.bullet_point('Prominent: Not buried in fine print or footnotes')
    pdf.bullet_point('In plain language: Understandable to the intended audience')
    pdf.bullet_point('Effective: Communicating the relevant information clearly and completely')
    pdf.bullet_point('Timely: Made before the conflict affects the client relationship')

    # VI(B) Priority of Transactions
    pdf.section_heading('Standard VI(B): Priority of Transactions', level=2)
    pdf.body_text(
        'Investment transactions for clients and employers must have priority over investment transactions in '
        'which a Member or Candidate is the beneficial owner.'
    )

    pdf.section_heading('Guidance', level=3)
    pdf.body_text(
        'This standard establishes the principle that clients\' interests come first. Members must not trade '
        'ahead of clients or allow their personal trading to disadvantage clients.'
    )
    pdf.body_text(
        'Key aspects include:'
    )
    pdf.bullet_point('Personal trading: Members must ensure that their personal trades do not conflict with or take priority over trades for clients. Members should not trade ahead of clients in the same securities.')
    pdf.bullet_point('Front-running: Trading in one\'s own account ahead of client trades, particularly when the member has knowledge of pending client orders, is strictly prohibited.')
    pdf.bullet_point('Family member accounts: Accounts of family members (spouse, children, etc.) are generally treated the same as the member\'s own accounts for purposes of this standard.')
    pdf.bullet_point('IPO allocations: Members must not take personal advantage of IPO allocations at the expense of clients.')

    pdf.section_heading('Recommended Procedures for Standard VI(B)', level=3)
    pdf.bullet_point('Establish policies requiring pre-clearance of personal trades')
    pdf.bullet_point('Require disclosure of personal holdings and trading activity')
    pdf.bullet_point('Establish blackout periods around recommendation changes and client trades')
    pdf.bullet_point('Restrict participation in IPOs by investment personnel')
    pdf.bullet_point('Report and review personal transactions regularly')
    pdf.bullet_point('Establish procedures to ensure that client orders take priority over personal orders')

    # VI(C) Referral Fees
    pdf.section_heading('Standard VI(C): Referral Fees', level=2)
    pdf.body_text(
        'Members and Candidates must disclose to their employer, clients, and prospective clients, as '
        'appropriate, any compensation, consideration, or benefit received from or paid to others for the '
        'recommendation of products or services.'
    )

    pdf.section_heading('Guidance', level=3)
    pdf.body_text(
        'This standard requires full disclosure of any referral fees or arrangements. Clients must be aware '
        'of any financial incentives that might influence the recommendations they receive.'
    )
    pdf.body_text(
        'Key aspects include:'
    )
    pdf.bullet_point('Disclosure must be made to the employer: Members must inform their employer of any referral fee arrangements, whether they are paying or receiving the fees.')
    pdf.bullet_point('Disclosure must be made to clients: Clients and prospective clients must be informed of referral fee arrangements so they can evaluate the potential impact on the member\'s objectivity.')
    pdf.bullet_point('Nature of disclosure: The disclosure should include the nature of the arrangement, the amount of compensation (or a description of it), and the duration of the arrangement.')
    pdf.bullet_point('Both internal and external referrals: This standard applies to referral arrangements both within a firm (interdepartmental referrals) and with outside parties.')

    # ---- STANDARD VII: RESPONSIBILITIES AS A CFA MEMBER ----
    pdf.section_heading('STANDARD VII: RESPONSIBILITIES AS A CFA INSTITUTE MEMBER OR CFA CANDIDATE')

    # VII(A) Conduct as Participants in CFA Institute Programs
    pdf.section_heading('Standard VII(A): Conduct as Participants in CFA Institute Programs', level=2)
    pdf.body_text(
        'Members and Candidates must not engage in any conduct that compromises the reputation or integrity '
        'of CFA Institute or the CFA designation or the integrity, validity, or security of CFA Institute '
        'programs.'
    )

    pdf.section_heading('Guidance', level=3)
    pdf.body_text(
        'This standard is designed to protect the integrity of the CFA examination process and other CFA '
        'Institute programs. The value of the CFA designation depends on the integrity and credibility of '
        'the examination process.'
    )
    pdf.body_text(
        'Violations of this standard include:'
    )
    pdf.bullet_point('Sharing or disclosing exam content (specific questions, topics tested, or question formats) either before, during, or after the examination')
    pdf.bullet_point('Bringing unauthorized materials into the testing center')
    pdf.bullet_point('Continuing to write or fill in answers after the time has been called')
    pdf.bullet_point('Copying or attempting to copy from other candidates')
    pdf.bullet_point('Impersonating another candidate or having someone else take the exam on your behalf')
    pdf.bullet_point('Providing false information on the Professional Conduct Statement')
    pdf.bullet_point('Compromising the integrity of CFA Institute programs through volunteer activities')

    pdf.body_text(
        'Important note: Candidates may discuss the general topics tested on the exam and their overall '
        'experience, but they must not disclose specific questions, calculations, or other detailed exam content. '
        'Expressing an opinion about the difficulty of the exam or the topics covered in general terms is '
        'permitted, but sharing specific details is not.'
    )

    # VII(B) Reference to CFA Institute
    pdf.section_heading('Standard VII(B): Reference to CFA Institute, the CFA Designation, and the CFA Program', level=2)
    pdf.body_text(
        'When referring to CFA Institute, CFA Institute membership, the CFA designation, or candidacy in the '
        'CFA Program, Members and Candidates must not misrepresent or exaggerate the meaning or implications '
        'of membership in CFA Institute, holding the CFA designation, or candidacy in the CFA Program.'
    )

    pdf.section_heading('Guidance', level=3)
    pdf.body_text(
        'This standard protects the integrity and value of the CFA designation and CFA Institute\'s reputation. '
        'Key requirements include:'
    )
    pdf.bullet_point('CFA as an adjective: "CFA" must be used as an adjective, not as a noun. It is correct to say "John Smith, CFA" or "John Smith is a CFA charterholder." It is incorrect to say "John Smith is a CFA."')
    pdf.bullet_point('No guarantees of competence or performance: Members must not imply that the CFA designation guarantees superior performance or competence. While the CFA Program provides a rigorous education, it does not guarantee investment success.')
    pdf.bullet_point('Candidacy claims: Only individuals who are actively registered for a CFA examination may reference their candidacy. Once a candidate is no longer registered, they may not claim candidacy.')
    pdf.bullet_point('Partial designation: Members must not claim to have partially earned the CFA designation by stating they passed one or more levels of the exam. However, stating that one has passed a specific level of the CFA exam is permitted if it is factually correct.')
    pdf.bullet_point('Proper use of marks: The CFA marks (CFA, Chartered Financial Analyst, and the CFA logo) must be used in accordance with CFA Institute trademark guidelines.')

    pdf.section_heading('Recommended Procedures for Standard VII(B)', level=3)
    pdf.bullet_point('Review all marketing materials and communications for proper use of CFA marks')
    pdf.bullet_point('Ensure that all references to CFA status are accurate and not misleading')
    pdf.bullet_point('Follow CFA Institute trademark usage guidelines')
    pdf.bullet_point('Correct any misuse of CFA marks by colleagues or the firm')

    # =========================================================================
    # MODULE 4: Introduction to GIPS
    # =========================================================================
    pdf.module_title(4, 'Introduction to the Global Investment Performance Standards (GIPS)')

    pdf.section_heading('Learning Outcomes')
    pdf.body_text('After completing this module, you should be able to:')
    for lo in [
        'Explain why the GIPS standards were created, what parties the GIPS standards apply to, and who is served by the standards',
        'Explain the construction and purpose of composites in performance reporting',
        'Explain the requirements for verification',
    ]:
        pdf.bullet_point(lo)
    pdf.ln(3)

    pdf.section_heading('Why Were the GIPS Standards Created?')
    pdf.body_text(
        'The Global Investment Performance Standards (GIPS) were created to address the need for a global, '
        'industry-wide set of ethical principles for calculating and presenting investment performance. Before '
        'GIPS, there were no consistent standards for presenting investment performance, which made it difficult '
        'for investors to compare the performance of different investment managers.'
    )
    pdf.body_text(
        'Problems that existed before GIPS included:'
    )
    pdf.bullet_point('Representative accounts: Firms would present the performance of their best-performing accounts rather than a composite of all accounts managed in a similar strategy.')
    pdf.bullet_point('Survivorship bias: Firms would exclude the performance of terminated (closed) accounts, thereby inflating reported performance.')
    pdf.bullet_point('Varying time periods: Firms would select favorable time periods for performance reporting.')
    pdf.bullet_point('Inconsistent calculation methods: Different firms used different methods for calculating returns, making comparisons difficult.')

    pdf.body_text(
        'GIPS addresses these issues by establishing a standardized set of principles for calculating and '
        'presenting investment performance that is based on the fundamental principles of fair representation '
        'and full disclosure.'
    )

    pdf.section_heading('Who Can Claim Compliance?')
    pdf.body_text(
        'GIPS compliance is voluntary and applies to investment management firms (not individuals). Key points '
        'about compliance:'
    )
    pdf.bullet_point('Only investment management firms can claim compliance with GIPS. Individual portfolio managers or analysts cannot claim personal compliance.')
    pdf.bullet_point('Compliance must be on a firm-wide basis. A firm cannot claim partial compliance or compliance for only certain products or divisions.')
    pdf.bullet_point('GIPS compliance is a firm-wide initiative that requires commitment and resources from all levels of the organization.')
    pdf.bullet_point('Once a firm claims compliance, it must comply with all applicable requirements of the GIPS standards.')

    pdf.section_heading('Who Benefits from Compliance?')
    pdf.body_text(
        'GIPS compliance benefits multiple parties:'
    )
    pdf.bullet_point('Prospective clients: Can compare investment performance across firms on a fair and consistent basis, enabling better-informed manager selection decisions.')
    pdf.bullet_point('Existing clients: Can have confidence that performance reporting is accurate, complete, and fairly presented.')
    pdf.bullet_point('Investment management firms: Can demonstrate their commitment to ethical practices and fair performance reporting, potentially attracting more clients.')
    pdf.bullet_point('The investment industry: Benefits from increased transparency, comparability, and confidence in performance reporting.')

    pdf.section_heading('Composites')
    pdf.body_text(
        'A composite is a grouping of individual discretionary portfolios that represents a specific investment '
        'objective or strategy. Composites are a fundamental concept in GIPS because they ensure that performance '
        'reporting reflects the results of all portfolios managed in a particular strategy, not just selected accounts.'
    )
    pdf.body_text(
        'Key requirements for composites:'
    )
    pdf.bullet_point('All actual, fee-paying, discretionary portfolios must be included in at least one composite.')
    pdf.bullet_point('Composites must include terminated portfolios for the periods during which they were managed.')
    pdf.bullet_point('Portfolios must not be switched from one composite to another unless there is a documented change in the client\'s investment objectives or strategy.')
    pdf.bullet_point('New portfolios must be included in a composite in a timely and consistent manner.')
    pdf.bullet_point('The composite definition should be clearly documented, including criteria for inclusion and exclusion.')

    pdf.section_heading('Fundamentals of Compliance')
    pdf.body_text(
        'Key fundamentals of GIPS compliance include:'
    )
    pdf.bullet_point('Definition of the firm: The firm must be defined as an investment firm, subsidiary, or division that is held out to clients as a distinct business entity.')
    pdf.bullet_point('Input data: The GIPS standards rely on the accuracy and completeness of input data. The standards require firms to use accurate and complete data to calculate performance.')
    pdf.bullet_point('Calculation methodology: Returns must be calculated using time-weighted or money-weighted methods as specified by the standards.')
    pdf.bullet_point('Composite construction: Firms must create and maintain composites that represent their investment strategies.')
    pdf.bullet_point('Disclosure: Firms must make specific disclosures when presenting performance, including the composite description, benchmark information, and fees.')
    pdf.bullet_point('Presentation and reporting: Firms must present performance data in GIPS-compliant presentations that include all required information.')
    pdf.bullet_point('Real estate and private equity: GIPS includes specific provisions for real estate and private equity investments.')

    pdf.section_heading('Verification')
    pdf.body_text(
        'Verification is the process by which an independent third party reviews the investment management firm\'s '
        'policies and procedures to determine whether the firm has complied with GIPS requirements on a firm-wide basis.'
    )
    pdf.body_text(
        'Key points about verification:'
    )
    pdf.bullet_point('Verification is not required for GIPS compliance, but it is strongly recommended.')
    pdf.bullet_point('Verification must be performed by an independent third party (not the firm itself).')
    pdf.bullet_point('Verification applies to the firm as a whole, not to individual composites.')
    pdf.bullet_point('A verification report must be issued, stating whether the firm has complied with GIPS requirements.')
    pdf.bullet_point('Verification does not ensure the accuracy of any specific composite presentation.')
    pdf.bullet_point('In addition to verification, firms may also have individual composite presentations examined (a "performance examination"), which provides a higher level of assurance for a specific composite.')

    # =========================================================================
    # MODULE 5: Ethics Application
    # =========================================================================
    pdf.module_title(5, 'Ethics Application')

    pdf.body_text(
        'This module provides additional application scenarios for each of the Standards of Professional Conduct. '
        'It presents case studies and ethical dilemmas that require candidates to apply the standards to complex '
        'real-world situations. The scenarios are designed to test understanding of how multiple standards may '
        'interact and how to resolve situations where competing obligations arise.'
    )

    # Professionalism Applications
    pdf.section_heading('Professionalism Applications')

    pdf.section_heading('Knowledge of the Law - Application Scenarios', level=2)
    pdf.body_text(
        'When members operate across multiple jurisdictions, they must identify and comply with the most restrictive '
        'applicable law, rule, or regulation. This can be particularly challenging when different jurisdictions have '
        'conflicting requirements.'
    )
    pdf.body_text(
        'Key application principles:'
    )
    pdf.bullet_point('When local law is stricter than the Code and Standards, follow local law.')
    pdf.bullet_point('When the Code and Standards are stricter than local law, follow the Code and Standards.')
    pdf.bullet_point('Members must not participate in or assist with violations, even if directed to do so by an employer or client.')
    pdf.bullet_point('When a member becomes aware of a violation, they must take affirmative steps to dissociate - mere inaction is not sufficient.')
    pdf.bullet_point('Members should keep records of their efforts to comply with applicable laws and the Code and Standards.')

    pdf.section_heading('Independence and Objectivity - Application Scenarios', level=2)
    pdf.body_text(
        'Maintaining independence and objectivity requires constant vigilance. Threats can be subtle and may '
        'develop gradually over time.'
    )
    pdf.body_text(
        'Key application principles:'
    )
    pdf.bullet_point('Modest gifts and entertainment customary in the business relationship are generally acceptable, but lavish gifts or trips should be declined.')
    pdf.bullet_point('Issuer-paid research must be clearly disclosed as such to avoid misleading investors.')
    pdf.bullet_point('Buy-side analysts should maintain independence when evaluating sell-side recommendations and must not allow relationships or services provided to influence their decisions.')
    pdf.bullet_point('Internal pressure from sales teams, investment banking divisions, or management to alter research conclusions violates this standard.')
    pdf.bullet_point('Members must not allow trading allocation, commission arrangements, or other financial incentives to compromise their objectivity.')

    pdf.section_heading('Misrepresentation - Application Scenarios', level=2)
    pdf.body_text(
        'Misrepresentation can be intentional or unintentional. Members must take reasonable steps to verify '
        'the accuracy of all information they communicate.'
    )
    pdf.body_text(
        'Key application principles:'
    )
    pdf.bullet_point('Errors in reports must be corrected promptly once discovered. Failure to correct a known error is a misrepresentation.')
    pdf.bullet_point('Guaranteeing investment returns or performance is always a misrepresentation.')
    pdf.bullet_point('Omitting material information (such as risks, fees, or limitations) is a form of misrepresentation through omission.')
    pdf.bullet_point('Plagiarism includes copying not only text but also ideas, analysis, charts, or models without attribution.')
    pdf.bullet_point('Out-of-date information should be clearly identified as such if it is presented to clients.')
    pdf.bullet_point('Composite performance must not be constructed selectively to show only favorable results.')

    pdf.section_heading('Misconduct - Application Scenarios', level=2)
    pdf.body_text(
        'Misconduct extends beyond professional activities to personal conduct that reflects adversely on '
        'professional integrity.'
    )
    pdf.bullet_point('Fraud, theft, and other dishonest acts violate this standard regardless of whether they are related to professional activities.')
    pdf.bullet_point('Substance abuse that impairs professional competence is a violation.')
    pdf.bullet_point('Personal bankruptcy does not, in itself, violate this standard, but dishonest conduct related to financial difficulties may.')

    pdf.section_heading('Competence - Application Scenarios', level=2)
    pdf.body_text(
        'Members must maintain the competence needed for their role and must seek to improve their skills '
        'as their responsibilities change.'
    )
    pdf.bullet_point('When taking on new responsibilities, members must acquire the necessary knowledge and skills before providing services in that area.')
    pdf.bullet_point('Members should stay current with industry developments, new products, and regulatory changes relevant to their role.')
    pdf.bullet_point('Supervisors must ensure that their subordinates are competent to perform their assigned duties.')
    pdf.bullet_point('When a member identifies a gap in their competence, they should take appropriate steps to address it (e.g., training, education, mentoring).')

    # Integrity of Capital Markets Applications
    pdf.section_heading('Integrity of Capital Markets Applications')

    pdf.section_heading('Material Nonpublic Information - Application Scenarios', level=2)
    pdf.body_text(
        'Determining what constitutes material nonpublic information requires careful judgment. The mosaic theory '
        'provides a framework for analysts to combine nonmaterial pieces of information to form investment conclusions.'
    )
    pdf.bullet_point('When in doubt about whether information is material, members should err on the side of caution and assume it is material.')
    pdf.bullet_point('Information from expert networks must be evaluated carefully to ensure it does not constitute material nonpublic information.')
    pdf.bullet_point('The mosaic theory permits combining nonmaterial nonpublic information with public information to reach investment conclusions.')
    pdf.bullet_point('Members who receive material nonpublic information inadvertently must not trade on it or communicate it to others.')
    pdf.bullet_point('Social media and informal communications can be sources of material nonpublic information.')

    pdf.section_heading('Market Manipulation - Application Scenarios', level=2)
    pdf.body_text(
        'Market manipulation includes both information-based and transaction-based manipulation.'
    )
    pdf.bullet_point('"Pump and dump" schemes - spreading positive information to inflate prices before selling - are clear violations.')
    pdf.bullet_point('Wash trading (trading with oneself to create artificial volume) is prohibited.')
    pdf.bullet_point('Legitimate trading strategies that affect prices are not manipulation if they are not designed to mislead.')
    pdf.bullet_point('Spreading false or misleading information about companies or securities is prohibited even if done through social media or informal channels.')
    pdf.bullet_point('Manipulating model inputs to achieve desired results is a form of market manipulation.')

    # Duties to Clients Applications
    pdf.section_heading('Duties to Clients Applications')

    pdf.section_heading('Loyalty, Prudence, and Care - Application Scenarios', level=2)
    pdf.body_text(
        'The duty of loyalty requires placing client interests above the member\'s own interests or the '
        'interests of the employer.'
    )
    pdf.bullet_point('Directing client brokerage to benefit the member (e.g., through soft dollar arrangements) rather than the client violates this standard.')
    pdf.bullet_point('Excessive trading ("churning") to generate commissions is a violation of the duty of care.')
    pdf.bullet_point('When managing pension fund assets, the client is generally the plan beneficiaries, not the plan sponsor.')
    pdf.bullet_point('Members who serve as both broker and investment adviser must disclose this dual role and manage the conflicts it creates.')
    pdf.bullet_point('Proxy voting must be done in the best interests of clients, not the member or the firm.')

    pdf.section_heading('Fair Dealing - Application Scenarios', level=2)
    pdf.body_text(
        'Fair dealing requires equitable treatment of all clients, though not necessarily identical treatment.'
    )
    pdf.bullet_point('Recommendation changes must be disseminated to all affected clients before any trades are executed.')
    pdf.bullet_point('IPO allocations must be distributed fairly among eligible clients, typically on a pro rata basis.')
    pdf.bullet_point('Providing different levels of service is acceptable as long as it is disclosed and does not disadvantage lower-tier clients.')
    pdf.bullet_point('Social media posts about investment recommendations should be accompanied by broad dissemination to all clients.')
    pdf.bullet_point('Trade allocation procedures must be designed to ensure fair treatment of all clients.')

    pdf.section_heading('Suitability - Application Scenarios', level=2)
    pdf.body_text(
        'Suitability requires understanding client circumstances before making recommendations.'
    )
    pdf.bullet_point('An IPS should be prepared for each advisory client and updated regularly.')
    pdf.bullet_point('Suitability should be evaluated in the context of the total portfolio, not individual securities.')
    pdf.bullet_point('When managing to a mandate (e.g., a fund with a specific strategy), the member must adhere to the mandate even if individual fund investors have different personal objectives.')
    pdf.bullet_point('Unsolicited trade requests from clients should still be evaluated for suitability, and the member should advise against unsuitable trades.')
    pdf.bullet_point('Changes in client circumstances (retirement, inheritance, health changes) require IPS updates and portfolio adjustments.')

    pdf.section_heading('Performance Presentation - Application Scenarios', level=2)
    pdf.body_text(
        'Performance presentations must be fair, accurate, and complete.'
    )
    pdf.bullet_point('Cherry-picking favorable accounts or time periods for performance reporting violates this standard.')
    pdf.bullet_point('Simulated or backtested performance must be clearly labeled and distinguished from actual results.')
    pdf.bullet_point('Performance from a prior employer may be presented if it is clearly attributed and the member was responsible for the results.')
    pdf.bullet_point('Changes in performance methodology must be disclosed to clients.')
    pdf.bullet_point('Terminated accounts must be included in composite performance through their termination date.')

    pdf.section_heading('Preservation of Confidentiality - Application Scenarios', level=2)
    pdf.body_text(
        'Client confidentiality extends beyond the duration of the client relationship.'
    )
    pdf.bullet_point('Information about former clients must be kept confidential.')
    pdf.bullet_point('If a member suspects a client is engaged in illegal activity, they should consult with compliance and legal counsel about reporting obligations.')
    pdf.bullet_point('Accidental disclosures of confidential information must be addressed promptly to minimize harm.')
    pdf.bullet_point('Electronic communications about clients should be secured and encrypted where appropriate.')

    # Duties to Employers Applications
    pdf.section_heading('Duties to Employers Applications')

    pdf.section_heading('Loyalty to Employers - Application Scenarios', level=2)
    pdf.body_text(
        'The duty of loyalty to employers is subordinate to the duty to clients and the duty to comply with '
        'the law.'
    )
    pdf.bullet_point('Members planning to leave may not solicit their employer\'s clients or take proprietary materials before their departure.')
    pdf.bullet_point('After leaving, members may contact former clients but must not use confidential information (client lists, proprietary data) from the former employer.')
    pdf.bullet_point('Work products (models, analysis, reports) created during employment belong to the employer.')
    pdf.bullet_point('General skills, knowledge, and experience gained during employment belong to the member and may be used in future positions.')
    pdf.bullet_point('Whistleblowing on illegal or unethical employer conduct does not violate the duty of loyalty.')
    pdf.bullet_point('Members must obtain employer consent before undertaking independent practice or outside activities that compete with the employer.')

    pdf.section_heading('Additional Compensation Arrangements - Application Scenarios', level=2)
    pdf.body_text(
        'All compensation received from parties other than the employer must be disclosed and approved.'
    )
    pdf.bullet_point('Written consent from the employer is required before accepting additional compensation from clients or other parties.')
    pdf.bullet_point('Gift and entertainment policies should be followed, and significant gifts must be disclosed.')
    pdf.bullet_point('Performance bonuses from clients must be disclosed to the employer in writing.')

    pdf.section_heading('Responsibilities of Supervisors - Application Scenarios', level=2)
    pdf.body_text(
        'Supervisors must establish adequate compliance procedures and take action when violations are detected.'
    )
    pdf.bullet_point('A supervisor cannot simply rely on others (compliance department, etc.) to ensure compliance - they have an independent obligation.')
    pdf.bullet_point('If a firm\'s compliance procedures are inadequate, the supervisor must take steps to improve them or escalate the issue.')
    pdf.bullet_point('When violations are detected, the supervisor must investigate and take corrective action promptly.')
    pdf.bullet_point('Supervisors should provide training and education on compliance requirements.')
    pdf.bullet_point('A supervisor who delegates supervisory duties to subordinates remains responsible for ensuring compliance.')

    # Investment Analysis Applications
    pdf.section_heading('Investment Analysis, Recommendations, and Actions Applications')

    pdf.section_heading('Diligence and Reasonable Basis - Application Scenarios', level=2)
    pdf.body_text(
        'The level of diligence required depends on the complexity of the investment and the member\'s role.'
    )
    pdf.bullet_point('Relying on third-party research is acceptable if the member has evaluated the quality and methodology of the research.')
    pdf.bullet_point('Quantitative models must be understood, including their assumptions, limitations, and potential failure modes.')
    pdf.bullet_point('When selecting subadvisers or external managers, thorough due diligence is required, including review of investment process, risk management, compliance, and track record.')
    pdf.bullet_point('A reasonable basis can still exist even if an investment ultimately performs poorly - the standard requires adequate process, not guaranteed results.')

    pdf.section_heading('Communication with Clients - Application Scenarios', level=2)
    pdf.body_text(
        'Clear and complete communication is essential for informed decision-making.'
    )
    pdf.bullet_point('Fees and costs must be disclosed clearly, including all layers of fees in fund-of-funds or multi-manager structures.')
    pdf.bullet_point('Opinions must be clearly distinguished from facts in all communications.')
    pdf.bullet_point('Changes to the investment process must be communicated to clients promptly.')
    pdf.bullet_point('Risks and limitations of investment strategies must be disclosed.')
    pdf.bullet_point('Errors in client reports must be corrected and communicated to affected clients promptly.')

    pdf.section_heading('Record Retention - Application Scenarios', level=2)
    pdf.body_text(
        'Proper record retention supports compliance and protects both the member and the firm.'
    )
    pdf.bullet_point('Records should be maintained for at least seven years in the absence of specific regulatory requirements.')
    pdf.bullet_point('Records are the property of the firm, not the individual employee.')
    pdf.bullet_point('Records should document the basis for investment recommendations, including research, analysis, and the rationale for the recommendation.')

    # Conflicts of Interest Applications
    pdf.section_heading('Conflicts of Interest Applications')

    pdf.section_heading('Avoid or Disclose Conflicts - Application Scenarios', level=2)
    pdf.bullet_point('Ownership of securities that are the subject of recommendations must be disclosed.')
    pdf.bullet_point('Board positions and other relationships with companies covered in research must be disclosed.')
    pdf.bullet_point('Compensation structures that create conflicts (e.g., commissions, referral fees) must be disclosed.')
    pdf.bullet_point('When avoidance of a conflict is not possible, full and prominent disclosure is required.')

    pdf.section_heading('Priority of Transactions - Application Scenarios', level=2)
    pdf.bullet_point('Client trades must always take priority over personal trades in the same securities.')
    pdf.bullet_point('Family member accounts are generally subject to the same restrictions as the member\'s own accounts.')
    pdf.bullet_point('Pre-clearance of personal trades helps prevent conflicts and should be required.')
    pdf.bullet_point('Trading ahead of a recommendation change ("front-running") is strictly prohibited.')

    pdf.section_heading('Referral Fees - Application Scenarios', level=2)
    pdf.bullet_point('All referral fee arrangements must be disclosed to both the employer and the client.')
    pdf.bullet_point('Disclosure should include the nature, amount, and duration of the arrangement.')
    pdf.bullet_point('Both internal (interdepartmental) and external referral arrangements require disclosure.')

    # CFA Institute Member Responsibilities Applications
    pdf.section_heading('Responsibilities as a CFA Institute Member or CFA Candidate Applications')

    pdf.section_heading('Conduct as Participants - Application Scenarios', level=2)
    pdf.bullet_point('Sharing specific exam questions or content (including on social media) is a serious violation.')
    pdf.bullet_point('General discussions about exam difficulty or broad topic areas are permitted.')
    pdf.bullet_point('Bringing unauthorized materials into the exam room is a violation.')
    pdf.bullet_point('Writing after time has been called is a violation.')
    pdf.bullet_point('Volunteers must not use their position to compromise the integrity of CFA Institute programs.')

    pdf.section_heading('Reference to CFA Designation - Application Scenarios', level=2)
    pdf.bullet_point('"CFA" must be used as an adjective (e.g., "CFA charterholder"), not a noun (not "I am a CFA").')
    pdf.bullet_point('Only currently registered candidates may claim candidacy status.')
    pdf.bullet_point('Members who have not paid their dues and are no longer active members cannot use the CFA designation.')
    pdf.bullet_point('Stating factual information about passing CFA exams is permitted (e.g., "I passed all three levels of the CFA exam").')
    pdf.bullet_point('The CFA designation should not be presented as a guarantee of competence or performance.')

    # =========================================================================
    # SUMMARY AND KEY TAKEAWAYS
    # =========================================================================
    pdf.module_title(0, 'Summary and Key Exam Takeaways')
    pdf.body_text('This section provides a concise summary of the most important concepts for exam preparation.')

    pdf.section_heading('Critical Rules to Remember')
    pdf.bullet_point('ALWAYS follow the STRICTER of the Code and Standards or applicable law.')
    pdf.bullet_point('Client interests ALWAYS come before employer and personal interests.')
    pdf.bullet_point('When in doubt, DISCLOSE. Full and fair disclosure is almost always the right answer.')
    pdf.bullet_point('Dissociation requires AFFIRMATIVE ACTION - doing nothing is not enough.')
    pdf.bullet_point('Material nonpublic information must NOT be acted upon - use the mosaic theory for legitimate analysis.')
    pdf.bullet_point('Records belong to the FIRM, not the individual.')
    pdf.bullet_point('GIPS compliance is FIRM-WIDE and VOLUNTARY, but once claimed, all requirements must be met.')
    pdf.bullet_point('Personal trading must ALWAYS be subordinate to client trading.')
    pdf.bullet_point('Competence must be MAINTAINED and IMPROVED throughout a career.')
    pdf.bullet_point('"CFA" is an ADJECTIVE, not a noun or verb.')

    pdf.section_heading('Hierarchy of Interests')
    pdf.body_text(
        'The Code and Standards establish a clear hierarchy of interests that members and candidates must follow:'
    )
    pdf.bullet_point('1. Interests of clients come FIRST')
    pdf.bullet_point('2. Integrity of the investment profession and capital markets')
    pdf.bullet_point('3. Interests of the employer')
    pdf.bullet_point('4. Personal interests of the member or candidate come LAST')

    pdf.section_heading('Common Exam Traps')
    pdf.bullet_point('Confusing "fair dealing" with "equal dealing" - fair dealing allows different service levels if disclosed.')
    pdf.bullet_point('Forgetting that the duty of confidentiality applies to FORMER clients as well as current ones.')
    pdf.bullet_point('Assuming that legal compliance equals ethical compliance - ethical standards typically exceed legal requirements.')
    pdf.bullet_point('Thinking that reporting violations to the government is required - it is encouraged but not required under the Standards (unless required by law).')
    pdf.bullet_point('Confusing suitability requirements for advisory clients vs. mandate-based portfolios.')
    pdf.bullet_point('Forgetting that supervisory responsibility exists even without a formal supervisor title.')
    pdf.bullet_point('Thinking that the mosaic theory permits use of material nonpublic information - it only covers NONmaterial nonpublic information combined with public information.')
    pdf.bullet_point('Assuming GIPS verification is required - it is RECOMMENDED but not mandatory.')

    pdf.section_heading('The Seven Standards - Quick Reference')

    standards = [
        ('I. Professionalism', [
            'I(A) Knowledge of the Law: Comply with the more strict of Code/Standards or local law; dissociate from violations',
            'I(B) Independence and Objectivity: Maintain independent judgment; decline gifts/benefits that could compromise objectivity',
            'I(C) Misrepresentation: Do not make false or misleading statements; give proper attribution (no plagiarism)',
            'I(D) Misconduct: No dishonesty, fraud, or deceit; no conduct reflecting adversely on professional reputation',
            'I(E) Competence: Maintain knowledge, skills, and abilities necessary for professional duties',
        ]),
        ('II. Integrity of Capital Markets', [
            'II(A) Material Nonpublic Information: Do not act on MNPI; mosaic theory allows combining nonmaterial nonpublic info with public info',
            'II(B) Market Manipulation: Do not distort prices or inflate volume to mislead; includes both information-based and transaction-based manipulation',
        ]),
        ('III. Duties to Clients', [
            'III(A) Loyalty, Prudence, and Care: Act in clients\' best interests; exercise prudent judgment; client interests before employer/personal interests',
            'III(B) Fair Dealing: Deal fairly with all clients; simultaneous dissemination of recommendations; pro rata allocation',
            'III(C) Suitability: Understand client circumstances (IPS); judge suitability in total portfolio context; follow mandates',
            'III(D) Performance Presentation: Fair, accurate, and complete; include terminated accounts; disclose methodology',
            'III(E) Preservation of Confidentiality: Keep client info confidential; exceptions for illegal activity, legal requirement, or client permission',
        ]),
        ('IV. Duties to Employers', [
            'IV(A) Loyalty: Act for employer\'s benefit; don\'t take proprietary info when leaving; get consent for independent practice',
            'IV(B) Additional Compensation: Get written employer consent before accepting outside compensation that creates conflicts',
            'IV(C) Responsibilities of Supervisors: Ensure subordinates comply; establish adequate compliance systems; take action on violations',
        ]),
        ('V. Investment Analysis, Recommendations, and Actions', [
            'V(A) Diligence and Reasonable Basis: Thorough analysis; adequate basis for recommendations; understand models and third-party research',
            'V(B) Communication with Clients: Disclose services and costs; disclose investment process; distinguish fact from opinion; disclose changes',
            'V(C) Record Retention: Maintain records supporting investment activities; records belong to the firm; 7-year recommendation',
        ]),
        ('VI. Conflicts of Interest', [
            'VI(A) Avoid or Disclose Conflicts: Avoid conflicts when possible; disclose prominently in plain language when avoidance not feasible',
            'VI(B) Priority of Transactions: Client/employer trades before personal trades; no front-running; family accounts treated as personal',
            'VI(C) Referral Fees: Disclose all referral arrangements to employer and clients; include nature, amount, and duration',
        ]),
        ('VII. Responsibilities as CFA Member/Candidate', [
            'VII(A) Conduct in CFA Programs: Do not compromise integrity of CFA exams; no sharing of specific exam content',
            'VII(B) Reference to CFA: CFA is an adjective; no guarantees of competence; only registered candidates may claim candidacy',
        ]),
    ]

    for std_name, items in standards:
        pdf.section_heading(std_name, level=2)
        for item in items:
            pdf.bullet_point(item)
        pdf.ln(2)

    # Generate PDF
    output_path = '/home/user/new-sid/CFA_Level1_Ethics_Study_Guide.pdf'
    pdf.output(output_path)
    print(f'PDF generated: {output_path}')
    return output_path


if __name__ == '__main__':
    build_study_guide()


