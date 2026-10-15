# -*- coding: utf-8 -*-
"""
Dựng báo cáo Word (.docx) tổng hợp P1-P5 theo khung luận văn học thuật (mẫu:
25007876_Cao Duy Khánh.pdf). Nguồn nội dung: docs/report/BaoCao_Tong_Hop.md,
docs/theory/LyThuyet.md và phần giải thích trong notebooks/P1-P5.ipynb.
Hình minh hoạ trích sẵn từ notebook (docs/report/figures/*.png) - KHÔNG chạy lại notebook.

Chạy:  python scripts/build_report_docx.py
Ra:    docs/report/BaoCao_Tong_Hop.docx
"""
import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH as ALIGN
from docx.enum.text import WD_LINE_SPACING as LS
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(ROOT, "docs", "report", "figures")
OUT = os.path.join(ROOT, "docs", "report", "BaoCao_Tong_Hop.docx")
FONT = "Times New Roman"

doc = Document()

# ---------------------------------------------------------------- page setup
sec = doc.sections[0]
sec.page_height, sec.page_width = Cm(29.7), Cm(21.0)      # A4 portrait
sec.top_margin, sec.bottom_margin = Cm(2.5), Cm(2.5)
sec.left_margin, sec.right_margin = Cm(3.0), Cm(2.0)

# ---------------------------------------------------------------- base styles
def _set_font(style, size, bold=False, color=None):
    style.font.name = FONT
    style.font.size = Pt(size)
    style.font.bold = bold
    if color:
        style.font.color.rgb = color
    rpr = style.element.get_or_add_rPr()
    rf = rpr.find(qn('w:rFonts'))
    if rf is None:
        rf = OxmlElement('w:rFonts'); rpr.append(rf)
    for a in ('w:ascii', 'w:hAnsi', 'w:cs'):
        rf.set(qn(a), FONT)

normal = doc.styles['Normal']
_set_font(normal, 13)
normal.paragraph_format.line_spacing_rule = LS.ONE_POINT_FIVE
normal.paragraph_format.space_after = Pt(6)
normal.paragraph_format.alignment = ALIGN.JUSTIFY

_set_font(doc.styles['Heading 1'], 16, bold=True, color=RGBColor(0, 0, 0))
_set_font(doc.styles['Heading 2'], 14, bold=True, color=RGBColor(0, 0, 0))
_set_font(doc.styles['Heading 3'], 13, bold=True, color=RGBColor(0, 0, 0))
for h in ('Heading 1', 'Heading 2', 'Heading 3'):
    pf = doc.styles[h].paragraph_format
    pf.space_before = Pt(12); pf.space_after = Pt(6)
    pf.line_spacing_rule = LS.ONE_POINT_FIVE

# ---------------------------------------------------------------- helpers
def _fld(run, instr):
    r = run._r
    b = OxmlElement('w:fldChar'); b.set(qn('w:fldCharType'), 'begin'); r.append(b)
    it = OxmlElement('w:instrText'); it.set(qn('xml:space'), 'preserve'); it.text = instr; r.append(it)
    s = OxmlElement('w:fldChar'); s.set(qn('w:fldCharType'), 'separate'); r.append(s)
    e = OxmlElement('w:fldChar'); e.set(qn('w:fldCharType'), 'end'); r.append(e)

def body(text, align=ALIGN.JUSTIFY, indent=True, size=None, italic=False):
    p = doc.add_paragraph()
    p.alignment = align
    if indent:
        p.paragraph_format.first_line_indent = Cm(0.5)
    for i, seg in enumerate(text.split('**')):
        if seg == '':
            continue
        r = p.add_run(seg)
        if i % 2 == 1:
            r.bold = True
        if italic:
            r.italic = True
        if size:
            r.font.size = Pt(size)
    return p

def eq(text):
    p = doc.add_paragraph(); p.alignment = ALIGN.CENTER
    p.paragraph_format.space_before = Pt(4); p.paragraph_format.space_after = Pt(4)
    r = p.add_run(text); r.italic = True; r.font.size = Pt(13)
    return p

def bullet(text):
    p = doc.add_paragraph(style='List Bullet'); p.alignment = ALIGN.JUSTIFY
    for i, seg in enumerate(text.split('**')):
        if seg == '':
            continue
        r = p.add_run(seg); r.bold = (i % 2 == 1)
    return p

def h1(text):
    doc.add_heading(text, level=1)

def h2(text):
    doc.add_heading(text, level=2)

def h3(text):
    doc.add_heading(text, level=3)

def caption(label, text, below=True):
    p = doc.add_paragraph(); p.alignment = ALIGN.CENTER
    p.paragraph_format.space_before = Pt(2 if below else 6)
    p.paragraph_format.space_after = Pt(6 if below else 2)
    r = p.add_run(label + ": "); r.bold = True; r.italic = True; r.font.size = Pt(12)
    r2 = p.add_run(text); r2.italic = True; r2.font.size = Pt(12)
    return p

def figure(fname, label, text, width=Cm(15)):
    path = os.path.join(FIG, fname)
    p = doc.add_paragraph(); p.alignment = ALIGN.CENTER
    p.add_run().add_picture(path, width=width)
    caption(label, text, below=True)

def table(label, cap, headers, rows, widths=None):
    caption(label, cap, below=False)
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = 'Table Grid'
    t.alignment = 1  # center
    hdr = t.rows[0].cells
    for j, htxt in enumerate(headers):
        hdr[j].paragraphs[0].alignment = ALIGN.CENTER
        r = hdr[j].paragraphs[0].add_run(htxt); r.bold = True; r.font.size = Pt(12); r.font.name = FONT
    for row in rows:
        cells = t.add_row().cells
        for j, val in enumerate(row):
            para = cells[j].paragraphs[0]
            para.alignment = ALIGN.CENTER if j > 0 else ALIGN.LEFT
            r = para.add_run(str(val)); r.font.size = Pt(12); r.font.name = FONT
    doc.add_paragraph()
    return t

def pagebreak():
    doc.add_page_break()

# ---------------------------------------------------------------- footer page number
def add_page_numbers(section):
    footer = section.footer
    p = footer.paragraphs[0]; p.alignment = ALIGN.CENTER
    _fld(p.add_run(), 'PAGE')
add_page_numbers(sec)

# ================================================================ COVER PAGE
def center(text, size, bold=False, italic=False, space_after=6, space_before=0):
    p = doc.add_paragraph(); p.alignment = ALIGN.CENTER
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.first_line_indent = Cm(0)
    r = p.add_run(text); r.bold = bold; r.italic = italic; r.font.size = Pt(size); r.font.name = FONT
    return p

center("ĐẠI HỌC QUỐC GIA HÀ NỘI", 13, bold=True, space_before=6)
center("TRƯỜNG ĐẠI HỌC KHOA HỌC TỰ NHIÊN", 13, bold=True)
center("KHOA TOÁN – CƠ – TIN HỌC", 13, bold=True, space_after=36)

center("BÁO CÁO CUỐI KỲ", 22, bold=True, space_after=4)
center("Chuyên đề nghiên cứu 2", 16, italic=True, space_after=28)

center("Đề tài:", 14, italic=True, space_after=8)
center("SO SÁNH MÔ HÌNH CỔ ĐIỂN, MACHINE LEARNING", 17, bold=True, space_after=2)
center("VÀ TIME-SERIES FOUNDATION MODEL CHO DỰ BÁO XÁC SUẤT", 17, bold=True, space_after=2)
center("NHU CẦU GIÁN ĐOẠN TRONG BÁN LẺ,", 17, bold=True, space_after=2)
center("CÓ PHÂN NHÓM THEO ĐẶC TÍNH NHU CẦU", 17, bold=True, space_after=40)

p = doc.add_paragraph(); p.alignment = ALIGN.RIGHT; p.paragraph_format.first_line_indent = Cm(0)
p.add_run("Giảng viên hướng dẫn:  ").font.size = Pt(13)
rr = p.add_run("TS. Hoàng Thị Phương Thảo"); rr.bold = True; rr.font.size = Pt(13)
p = doc.add_paragraph(); p.alignment = ALIGN.RIGHT; p.paragraph_format.first_line_indent = Cm(0)
p.add_run("Học viên thực hiện:  ").font.size = Pt(13)
rr = p.add_run("[Họ và tên] – [Mã học viên]"); rr.bold = True; rr.font.size = Pt(13)

center("Hà Nội, tháng … năm 2026", 13, bold=True, space_before=48)
pagebreak()

# ================================================================ MỤC LỤC
center("MỤC LỤC", 15, bold=True, space_after=10)
p = doc.add_paragraph(); p.alignment = ALIGN.LEFT; p.paragraph_format.first_line_indent = Cm(0)
_fld(p.add_run(), 'TOC \\o "1-3" \\h \\z \\u')
body("(Nhấn chọn mục lục rồi bấm F9 trong Microsoft Word để cập nhật số trang tự động.)",
     align=ALIGN.LEFT, indent=False, size=11, italic=True)
pagebreak()

# ================================================================ DANH MỤC HÌNH VẼ
center("DANH MỤC HÌNH VẼ", 14, bold=True, space_after=8)
FIGS_LIST = [
    "Hình 3.1: Thiết kế rolling-origin ba cửa sổ trượt lùi 28 ngày",
    "Hình 3.2: Lấy mẫu phân tầng – giữ 100% nhóm hiếm, cap 1.000 nhóm phổ biến",
    "Hình 4.1: Phân bố và đặc trưng bốn nhóm nhu cầu theo khung SBC",
    "Hình 4.2: Không gian ADI–CV² và ranh giới bốn nhóm nhu cầu",
    "Hình 4.3: Mức độ gián đoạn (zero-rate) tăng dần theo trục nhóm",
    "Hình 4.4: Nhu cầu trung bình và cấu trúc tiêu thụ theo nhóm",
    "Hình 4.5: Mùa vụ theo ngày trong tuần và theo tháng",
    "Hình 4.6: Hiệu ứng SNAP lên nhu cầu theo từng nhóm",
    "Hình 4.7: Tầm quan trọng đặc trưng của LightGBM",
    "Hình 4.8: Dự báo median của các mô hình so với thực tế",
    "Hình 4.9: Độ rộng khoảng dự báo – cổ điển so với LightGBM",
    "Hình 4.10: Dải phân vị của LightGBM so với thực tế",
    "Hình 4.11: Dự báo median của ba foundation model so với thực tế",
    "Hình 4.12: Dải phân vị của ba foundation model so với thực tế",
    "Hình 4.13: Hồ sơ phân vị foundation model – kẹp đuôi so với trải đều",
    "Hình 4.14: Độ rộng phân phối và chi phí tính toán của foundation model",
    "Hình 4.15: Bản đồ nhiệt WSPL (đã hiệu chuẩn) theo model × nhóm",
    "Hình 4.16: Bản đồ nhiệt RMSSE (đã hiệu chuẩn) theo model × nhóm",
    "Hình 4.17: Coverage danh nghĩa so với thực tế (raw → calibrated)",
    "Hình 4.18: Coverage-95 trước và sau hiệu chuẩn theo model",
]
for s in FIGS_LIST:
    body(s, align=ALIGN.LEFT, indent=False, size=12)

center("DANH MỤC BẢNG BIỂU", 14, bold=True, space_after=8, space_before=12)
TABS_LIST = [
    "Bảng 3.1: Từ điển dữ liệu của bảng data_long (input chung cho P2–P5)",
    "Bảng 3.2: Ba cửa sổ rolling-origin",
    "Bảng 4.1: Phân bố bốn nhóm nhu cầu trên toàn bộ 30.490 chuỗi",
    "Bảng 4.2: WSPL (đã hiệu chuẩn) theo model × nhóm",
    "Bảng 4.3: Khuyến nghị “nhu cầu nào → model nào” và kết quả kiểm định",
    "Bảng 4.4: Lỗi hệ thống của model khuyến nghị (chuẩn hoá theo scale)",
]
for s in TABS_LIST:
    body(s, align=ALIGN.LEFT, indent=False, size=12)
pagebreak()

# ================================================================ CHƯƠNG 1
h1("CHƯƠNG 1: GIỚI THIỆU")

h2("1.1. Bối cảnh và động lực nghiên cứu")
body("Dự báo nhu cầu là bài toán nền tảng của quản trị chuỗi cung ứng và vận hành bán lẻ. "
     "Chất lượng dự báo quyết định trực tiếp mức tồn kho an toàn, chi phí lưu kho, tỷ lệ hết hàng "
     "và cuối cùng là biên lợi nhuận. Tuy nhiên, phần lớn hàng hoá trong bán lẻ hiện đại không có "
     "nhu cầu đều đặn: với hàng chục nghìn mã hàng (SKU) trải trên nhiều cửa hàng, đa số chuỗi bán "
     "hàng ngày mang đặc tính **gián đoạn** (intermittent) – xen kẽ nhiều ngày bằng 0 với một vài "
     "ngày phát sinh bán. Ước tính có tới khoảng 95% SKU bán lẻ thuộc dạng này.")
body("Với chuỗi gián đoạn, một con số dự báo điểm (ví dụ giá trị kỳ vọng) gần như vô dụng cho quyết "
     "định tồn kho: giá trị trung bình thường rơi vào khoảng giữa 0 và cỡ bán điển hình, không phản ánh "
     "được rủi ro thiếu hàng ở đuôi phân phối. Điều mà người ra quyết định thực sự cần là **toàn bộ "
     "phân phối nhu cầu** – trả lời câu hỏi “có bao nhiêu phần trăm khả năng nhu cầu không vượt quá "
     "một mức nào đó” – để đặt mức tồn kho an toàn theo mức dịch vụ mong muốn. Đây chính là động lực "
     "của **dự báo xác suất** (probabilistic forecasting), trục xuyên suốt của nghiên cứu này.")
body("Song song, những năm gần đây chứng kiến sự trỗi dậy của **time-series foundation model** – các "
     "mô hình lớn được tiền huấn luyện trên kho chuỗi thời gian khổng lồ rồi áp dụng **zero-shot** cho "
     "bài toán mới mà không cần huấn luyện lại. Câu hỏi tự nhiên đặt ra cho giới nghiên cứu lẫn thực hành "
     "là: liệu các mô hình nền tảng này có thực sự vượt trội so với các phương pháp cổ điển chuyên trị "
     "nhu cầu gián đoạn (họ Croston) và các mô hình học máy đã được tối ưu (gradient boosting), đặc biệt "
     "trên tiêu chí xác suất và sau khi đã kiểm định thống kê nghiêm túc?")

h2("1.2. Vấn đề nghiên cứu")
body("Thực hành dự báo nhu cầu bán lẻ đối mặt ba khó khăn đan xen. **Thứ nhất**, tính gián đoạn làm "
     "các metric dự báo điểm (sai số tuyệt đối, bình phương) mất ý nghĩa và dễ gây hiểu nhầm khi so sánh "
     "mô hình. **Thứ hai**, tập SKU cực kỳ không đồng nhất: cùng một mô hình có thể rất tốt cho nhóm hàng "
     "bán đều nhưng lại tệ cho nhóm hàng bán thưa, nên một kết luận “trung bình toàn tập” thường "
     "che giấu các khác biệt quan trọng theo nhóm. **Thứ ba**, mỗi họ mô hình sinh ra khoảng dự báo bằng "
     "một cơ chế khác nhau (phân vị gốc, bọc phân phối, nội suy), khiến việc so sánh độ phủ trực tiếp trở "
     "nên thiếu công bằng – ta vô tình so sánh “lớp bọc” chứ không phải năng lực dự báo thật.")
body("Nghiên cứu này giải quyết đồng thời ba khó khăn trên bằng cách: (i) chuyển trọng tâm sang dự báo "
     "xác suất với các proper scoring rule; (ii) **phân nhóm nhu cầu theo đặc tính** (khung SBC) để kết "
     "luận có điều kiện theo từng nhóm; và (iii) áp một lớp **hiệu chuẩn chung bằng split-conformal** để "
     "mọi mô hình được so sánh trên “cùng một cây thước”, kèm **kiểm định thống kê** với quy tắc "
     "tuyên bố thắng khắt khe.")

h2("1.3. Mục tiêu và câu hỏi nghiên cứu")
body("Mục tiêu tổng quát là xây dựng và kiểm chứng một khung so sánh công bằng ba họ mô hình dự báo xác "
     "suất nhu cầu gián đoạn, phân nhóm theo đặc tính nhu cầu, trên bộ dữ liệu chuẩn M5 của Walmart. Cụ "
     "thể, nghiên cứu hướng tới trả lời hai câu hỏi cốt lõi:")
bullet("**Câu hỏi 1 – “Nhu cầu nào thì nên dùng mô hình nào?”** Với mỗi nhóm đặc tính nhu cầu "
       "(smooth, erratic, intermittent, lumpy), mô hình nào cho chất lượng dự báo xác suất tốt nhất, và "
       "ưu thế đó có **vững qua kiểm định thống kê** hay chỉ là dao động ngẫu nhiên?")
bullet("**Câu hỏi 2 – Foundation model có thực sự hơn không?** Các time-series foundation model zero-shot "
       "có vượt trội so với mô hình cổ điển và học máy trên tiêu chí xác suất, sau khi đã hiệu chuẩn chung "
       "và tính đến chi phí tính toán?")
body("Xuyên suốt, nghiên cứu dùng **chín mức phân vị** {0,005; 0,025; 0,165; 0,25; 0,5; 0,75; 0,835; "
     "0,975; 0,995} cho mỗi dự báo thay vì một điểm, và chấm trên **ba cửa sổ rolling-origin** để kết luận "
     "không phụ thuộc một gốc thời gian duy nhất.")

h2("1.4. Đối tượng và phạm vi nghiên cứu")
h3("1.4.1. Đối tượng nghiên cứu")
body("Đối tượng nghiên cứu là nhu cầu bán hàng ngày ở cấp (mặt hàng × cửa hàng) của bộ dữ liệu M5 "
     "(Walmart). Đối tượng phương pháp là ba họ mô hình dự báo xác suất: **cổ điển** (Naive, "
     "SeasonalNaive, Croston, SBA, TSB), **machine learning** (LightGBM hồi quy phân vị), và "
     "**time-series foundation model** (Chronos-Bolt, TinyTimeMixer, Moirai-2), cùng khung phân nhóm "
     "nhu cầu SBC và lớp hiệu chuẩn split-conformal.")
h3("1.4.2. Phạm vi nghiên cứu")
body("Về **dữ liệu**, nghiên cứu dùng bộ M5 công khai gồm 30.490 chuỗi × 1.941 ngày, kèm lịch sự kiện "
     "và giá bán; mọi metric được chấm trên một mẫu phân tầng 3.474 chuỗi (giữ toàn bộ nhóm hiếm, giới "
     "hạn nhóm phổ biến) để các nhóm hiếm không bị lấn át. Về **phương pháp**, foundation model được dùng "
     "ở chế độ zero-shot (không fine-tune trên M5); bước few-shot được xem là ablation tuỳ chọn và chưa "
     "thực hiện. Về **tiêu chí**, nghiên cứu tập trung vào chất lượng dự báo xác suất (WSPL là tiêu chí "
     "chính), kèm độ chính xác điểm (RMSSE) và độ phủ (coverage) làm chẩn đoán.")

h2("1.5. Cấu trúc bài luận")
body("Báo cáo gồm năm chương. **Chương 1** giới thiệu bối cảnh, vấn đề, mục tiêu và phạm vi. **Chương 2** "
     "trình bày cơ sở lý thuyết: chuỗi thời gian và nhu cầu gián đoạn, phân nhóm SBC, dự báo điểm so với "
     "xác suất, lý thuyết ba họ mô hình, hiệu chuẩn conformal và khung đánh giá – kiểm định. **Chương 3** "
     "mô tả dữ liệu, tiền xử lý, thiết kế thực nghiệm (phân tầng, rolling-origin, chống rò rỉ) và giao "
     "thức hiệu chuẩn – đánh giá. **Chương 4** trình bày và thảo luận toàn bộ kết quả thực nghiệm. "
     "**Chương 5** kết luận, nêu hạn chế và đề xuất hướng phát triển.")
pagebreak()

# ================================================================ CHƯƠNG 2
h1("CHƯƠNG 2: CƠ SỞ LÝ THUYẾT")

h2("2.1. Chuỗi thời gian và bài toán nhu cầu gián đoạn")
body("Dữ liệu nghiên cứu là **chuỗi thời gian**: giá trị tại một ngày phụ thuộc vào quá khứ, nên mọi "
     "thao tác xử lý phải tôn trọng trục thời gian. Ba thành phần thường được khai thác là **lag** (giá "
     "trị trễ k ngày), **mùa vụ** (chu kỳ tuần/năm) và **rolling** (thống kê trượt như trung bình, độ "
     "lệch chuẩn của n ngày gần nhất).")
body("**Nhu cầu gián đoạn** là chuỗi có nhiều ngày bằng 0 xen kẽ vài ngày có bán. Khi đó trung bình "
     "không đại diện và dự báo điểm kém ý nghĩa. Để mô tả định lượng mức gián đoạn, ta dùng hai chỉ số "
     "tính **chỉ trên khoảng train** (tránh rò rỉ): **ADI** (Average Demand Interval) bằng số ngày chia "
     "cho số ngày có bán dương, đo độ thưa; và **CV²** – bình phương hệ số biến thiên của cỡ nhu cầu các "
     "ngày có bán dương, đo độ biến động cỡ nhu cầu.")
eq("ADI = (số ngày) / (số ngày có bán > 0);     CV² = (σ/μ)²  trên các ngày có bán > 0")

h2("2.2. Phân nhóm nhu cầu theo khung SBC")
body("Khung **Syntetos–Boylan–Croston (SBC)** chia chuỗi thành bốn nhóm bằng hai ngưỡng kinh điển "
     "**ADI = 1,32** và **CV² = 0,49**: **smooth** (đều và ổn định), **erratic** (đều nhưng biến động "
     "mạnh), **intermittent** (thưa và ổn định), **lumpy** (thưa và biến động mạnh). Việc phân nhóm cho "
     "phép đưa ra kết luận *có điều kiện* theo từng loại nhu cầu thay vì một trung bình toàn tập dễ gây "
     "hiểu nhầm, và là điều kiện cần để trả lời câu hỏi “nhu cầu nào → mô hình nào”.")

h2("2.3. Dự báo điểm so với dự báo xác suất")
body("**Dự báo điểm** trả về một con số (thường là median); với chuỗi nhiều 0, con số này thường bằng 0 "
     "và vô dụng cho quyết định tồn kho. **Dự báo xác suất** trả về cả phân phối thông qua chín mức phân "
     "vị, cho phép trả lời “80% khả năng nhu cầu không vượt bao nhiêu” và đặt mức tồn kho an "
     "toàn. Đây là trục chính của nghiên cứu. Đầu ra chung của mọi mô hình trong báo cáo là 9 phân vị cho "
     "28 ngày; mô hình nào chỉ sinh điểm sẽ được **bọc phân phối Negative Binomial** để thành phân vị.")

h2("2.4. Họ mô hình cổ điển")
body("**Naive** giả định “ngày mai giống hôm nay”, dự báo bằng giá trị quan sát gần nhất – rẻ "
     "nhất và là mốc tham chiếu bắt buộc, nhưng bỏ qua mùa vụ nên kém nhất với chuỗi gián đoạn. "
     "**SeasonalNaive(7)** lặp lại giá trị cùng ngày tuần trước, bắt được mùa vụ tuần của bán lẻ.")
body("**Croston** là phương pháp chuẩn mực cho nhu cầu gián đoạn: tách nhu cầu thành **cỡ bán** (khi có "
     "bán) và **khoảng cách giữa hai lần bán**, làm mượt riêng từng thành phần bằng san mũ, rồi cho nhu "
     "cầu suất mỗi kỳ bằng cỡ bán chia cho khoảng cách.")
eq("ẑ_t = α·y_t + (1−α)·ẑ_{t−1};   p̂_t = α·q + (1−α)·p̂_{t−1};   ŷ = ẑ / p̂")
body("**SBA (Syntetos–Boylan Approximation)** là bản khử thiên lệch của Croston, nhân thêm hệ số "
     "(1 − α/2) để kéo ước lượng về gần kỳ vọng thật khi chuỗi rất thưa; trong thực nghiệm SBA/Croston "
     "thường dẫn đầu họ cổ điển. **TSB (Teunter–Syntetos–Babai)** cập nhật **xác suất có bán** ở mọi kỳ "
     "(kể cả kỳ bằng 0), nhờ đó dự báo tự hạ khi hàng có dấu hiệu ngừng bán – phù hợp SKU có vòng đời tắt dần.")

h2("2.5. Họ machine learning – LightGBM hồi quy phân vị")
body("**LightGBM** là tập hợp cây quyết định cộng dồn (gradient boosting) học quan hệ phi tuyến giữa "
     "nhiều đặc trưng và nhu cầu, dùng ở chế độ **hồi quy phân vị** để sinh trực tiếp từng mức phân vị. "
     "Mỗi cây mới học phần dư (gradient) của tổ hợp cây trước; với mức phân vị τ, hàm mất mát là "
     "**pinball loss** nên cây được tối ưu đúng cho mức τ đó. Mô hình huấn luyện **global** (một mô hình "
     "cho mọi chuỗi) nên “mượn sức” từ toàn tập, và khai thác được các biến ngoại sinh (lịch, "
     "giá, SNAP). Đặc trưng chi phối là mức nhu cầu và độ biến động gần đây – trong thực nghiệm, "
     "**rmean_28** (~67%) và **rstd_28** (~17%) áp đảo tầm quan trọng.")

h2("2.6. Họ foundation model")
body("Các **time-series foundation model** được tiền huấn luyện trên kho chuỗi thời gian khổng lồ rồi "
     "dùng **zero-shot**: đưa chuỗi M5 vào là dự báo ngay, không huấn luyện lại, dựa trên nhận dạng mẫu "
     "đã học. Điểm chung là chúng chỉ nhìn **context** (chuỗi quá khứ ≤ train_end), không dùng biến ngoại sinh.")
body("**Chronos-Bolt** “ngôn ngữ hoá” chuỗi: lượng tử hoá giá trị thành token, dùng kiến trúc "
     "T5 encoder–decoder sinh đa bước, trả về phân vị gốc – nhưng head huấn luyện trên dải [0,1; 0,9] nên "
     "**kẹp đuôi**. **TinyTimeMixer (TTM)** là mô hình MLP-Mixer nhẹ của IBM, rất nhanh, chỉ sinh điểm "
     "rồi **bọc NB** để ra phân vị. **Moirai-2** là transformer universal forecasting của Salesforce, "
     "sinh phân vị gốc trên lưới ~0,1–0,9 rồi **nội suy và sắp xếp** để khử quantile crossing. Cả Chronos "
     "và Moirai đều **hẹp đuôi** do kẹp biên, nên bắt buộc phải hiệu chuẩn trước khi dùng cho tồn kho.")
body("**Lưu ý rò rỉ tiền huấn luyện.** “Zero-shot” ở đây chỉ nghĩa là không cập nhật trọng số "
     "bằng M5, không đồng nghĩa M5 chưa từng xuất hiện trong tiền huấn luyện. Rà soát model card cho thấy "
     "M5 là tập giữ-ngoài trong benchmark zero-shot của Chronos và không nằm trong corpus công bố của "
     "TTM/Moirai-2, nên rủi ro rò rỉ trực tiếp là **thấp**; tuy vậy, do các corpus quy mô lớn không công "
     "bố đầy đủ, mọi kết luận về foundation model vẫn cần diễn giải thận trọng.")

h2("2.7. Bọc Negative Binomial – biến điểm thành phân phối")
body("Để mô hình chỉ sinh điểm (cổ điển, TTM) có được phân phối 9 phân vị, ta bọc một phân phối "
     "**Negative Binomial (NB)** cá thể hoá theo từng chuỗi. Coi dự báo điểm là trung bình μ và ước phương "
     "sai σ² từ lịch sử, ta suy tham số NB rồi lấy phân vị nghịch đảo. NB là phân phối đếm có phương sai "
     "lớn hơn trung bình (overdispersion), đuôi dày – hợp với nhu cầu bán lẻ biến động.")
eq("r = μ² / (σ² − μ),   p = r / (r + μ)   (nếu σ² > μ; ngược lại dùng Poisson);   q̂_τ = NB⁻¹(τ; r, p)")

h2("2.8. Hiệu chuẩn dự báo xác suất bằng split-conformal")
body("Ba họ mô hình sinh dải bằng ba cơ chế khác nhau (phân vị gốc kẹp đuôi · bọc NB · nội suy), nên đo "
     "coverage trực tiếp là đo lẫn “lớp bọc” chứ không phải năng lực thật. **Split-conformal** "
     "(phân phối tự do) giải quyết điều này: trên tập **validation**, tính sai số phân vị (residual) của "
     "mỗi mô hình, lấy offset bằng thống kê thứ tự của residual theo **từng (nhóm × mức τ)** (nguyên tắc "
     "Mondrian), rồi cộng offset vào dự báo test, sắp xếp lại giữ đơn điệu và kẹp không âm. Nhờ áp cùng "
     "một thủ tục cho mọi mô hình, ta đưa tất cả về **cùng một cây thước** – mục tiêu cốt lõi khi so sánh "
     "các họ khác nhau. Báo cáo trình bày cả bản **raw** lẫn **calibrated** để vừa thấy năng lực vẽ dải "
     "gốc, vừa có bảng xếp hạng trên sân chơi bình đẳng. Cần phân biệt: bọc NB *vẽ* dải (biến điểm thành "
     "phân vị), còn conformal *chỉnh* vị trí và độ rộng của dải đã có cho đúng coverage – hai lớp bổ sung, "
     "không thay thế nhau.")

h2("2.9. Khung đánh giá và kiểm định thống kê")
h3("2.9.1. Metric – hai trục độ phủ và độ sắc")
body("Một dải dự báo tốt phải đạt đồng thời **độ phủ** (coverage đúng mức danh nghĩa) và **độ sắc** "
     "(cùng độ phủ thì hẹp hơn là tốt hơn). Nới dải quá rộng thì coverage đẹp nhưng vô dụng; thu hẹp quá "
     "thì thiếu phủ. Vì vậy nghiên cứu **không xếp hạng bằng coverage** mà bằng **pinball (SPL/WSPL)** – "
     "một proper scoring rule phạt đồng thời cả hai trục trong một con số; coverage, độ rộng và bias chỉ "
     "là chẩn đoán để giải thích *vì sao* pinball tốt hay xấu.")
eq("ρ_τ(d) = max( τ·d , (τ−1)·d ),   với d = y − q̂_τ")
body("Ở τ = 0,975, thiếu phủ bị phạt hệ số 0,975 còn thừa chỉ 0,025, nên pinball **ép phân vị cao phải "
     "đủ cao**; sự phi đối xứng này neo mỗi mức τ đúng chỗ. Trung bình pinball trên 9 mức xấp xỉ CRPS rời "
     "rạc hoá. **WSPL** là SPL gộp các chuỗi theo **trọng số doanh thu** (giá × sản lượng 28 ngày trước "
     "gốc), nên phạt nặng hơn khi sai ở SKU đáng tiền – đây là **tiêu chí chính**. Độ chính xác điểm được "
     "đo bằng **RMSSE/MASE** chuẩn hoá theo scale naive tính trên train (leak-free). Tổng hợp theo hai "
     "cách: **balanced** (trung bình đều 4 nhóm) và **frequency-weighted** (trọng số theo tần suất thật "
     "trên 30.490 chuỗi).")
h3("2.9.2. Kiểm định Diebold–Mariano, MCB và quy tắc tuyên bố thắng")
body("Vì chênh lệch nhỏ giữa các mô hình có thể do may rủi, nghiên cứu dùng kiểm định thống kê với đơn "
     "vị quan sát là (chuỗi, cửa sổ). **Diebold–Mariano (DM)** dạng panel so sánh chênh loss giữa mỗi mô "
     "hình và mô hình tốt nhất, với **sai số chuẩn gom cụm theo chuỗi** (các cửa sổ của cùng một SKU không "
     "độc lập) và hiệu chỉnh **Holm** cho đa so sánh. DM được chọn làm kiểm định quyết định vì nó "
     "model-free và tôn trọng trọng số của WSPL. **MCB** (so sánh bội với mô hình tốt nhất, dựa hạng "
     "trung bình Nemenyi) được báo cáo kèm để tham chiếu.")
body("**Quy tắc tuyên bố thắng (win rule)** rất bảo thủ: một mô hình bị coi là **thua rõ** mô hình tốt "
     "nhất chỉ khi **p-Holm < 0,05 VÀ thua ở cả ba cửa sổ**. Mô hình tốt nhất **thắng rõ** khi mọi mô "
     "hình khác đều thua rõ; ngược lại các mô hình không thua rõ được xem **tương đương**, và khi đó "
     "khuyến nghị chọn mô hình **rẻ nhất** (nguyên tắc Occam và chi phí vận hành). Hai điều kiện độc lập "
     "này bù cho nhược điểm của DM (coi các chuỗi độc lập nên p có thể hơi lạc quan) bằng rào ổn định qua "
     "cả ba cửa sổ.")
pagebreak()

# ================================================================ CHƯƠNG 3
h1("CHƯƠNG 3: DỮ LIỆU VÀ MÔ HÌNH")

h2("3.1. Nguồn dữ liệu")
body("Nghiên cứu sử dụng bộ dữ liệu **M5 (Walmart)** – chuẩn mực trong cộng đồng dự báo nhờ quy mô và "
     "độ gián đoạn thực tế. Bộ dữ liệu gồm **30.490 chuỗi** (3.049 mặt hàng × 10 cửa hàng thuộc 3 bang, "
     "3 ngành) trên **1.941 ngày**, kèm bảng **calendar** (lễ/sự kiện và ngày phát trợ cấp thực phẩm "
     "**SNAP**) và bảng **sell_prices** (giá bán theo tuần). Các biến lịch, sự kiện, SNAP và giá đóng vai "
     "trò **biến ngoại sinh** giải thích biến động không theo mùa vụ.")

h2("3.2. Tiền xử lý dữ liệu")
body("Dữ liệu thô dạng **wide** (mỗi chuỗi một hàng, mỗi ngày một cột) được chuẩn hoá về dạng **long** "
     "(mỗi dòng là một cặp chuỗi × ngày), ghép thêm calendar và giá, rồi tạo các đặc trưng nền (ngày "
     "trong tuần, tháng, cờ sự kiện, SNAP, giá bán). Kết quả là bảng **data_long** – input chung, tất "
     "định (seed 42) cho toàn bộ P2–P5. Bảng 3.1 mô tả các cột chính.")
table("Bảng 3.1", "Từ điển dữ liệu của bảng data_long (input chung cho P2–P5).",
      ["Cột", "Ý nghĩa"],
      [["series_id", "Mã chuỗi = mặt hàng × cửa hàng (khoá chính)"],
       ["d_int / date", "Ngày dạng số (1…1941) / ngày lịch"],
       ["sales", "Lượng bán mỗi ngày (biến mục tiêu)"],
       ["item_id … state_id", "Phân cấp sản phẩm và cửa hàng"],
       ["wday, month, year, wm_yr_wk", "Biến lịch (ngày trong tuần, tháng, năm, tuần Walmart)"],
       ["event_name_1, event_type_1, is_event", "Sự kiện/lễ và cờ có sự kiện"],
       ["snap_CA, snap_TX, snap_WI, snap", "Ngày phát trợ cấp SNAP theo bang và cờ chung"],
       ["sell_price", "Giá bán"],
       ["segment", "Nhãn SBC: smooth / erratic / intermittent / lumpy"]])

h2("3.3. Lấy mẫu phân tầng và chia dữ liệu")
body("Phân bố nhóm nhu cầu rất mất cân bằng (xem Chương 4), nên nếu lấy mẫu ngẫu nhiên, hai nhóm hiếm "
     "**smooth** và **erratic** (chỉ ~5% tổng thể) sẽ bị nhóm thưa lấn át khi phân tích theo đặc tính. "
     "Do đó nghiên cứu áp quy tắc **“giữ hiếm, cap phổ biến”**: giữ 100% nhóm smooth (980) và "
     "erratic (494), giới hạn mỗi nhóm intermittent/lumpy ở 1.000 chuỗi, thu được **3.474 chuỗi** cân "
     "bằng để phân tích. Nhãn SBC vẫn được sinh cho đủ 30.490 chuỗi nhằm phục vụ trọng số tần suất khi "
     "tổng hợp. Hình 3.1 và Hình 3.2 minh hoạ thiết kế chia dữ liệu và lấy mẫu.")
figure("P1_1.png", "Hình 3.1",
       "Thiết kế rolling-origin ba cửa sổ trượt lùi 28 ngày: train nở dần về quá khứ, test luôn ≤ d_1941 "
       "(phạm vi có actuals), bảo đảm không rò rỉ tương lai.")
figure("P1_2.png", "Hình 3.2",
       "Lấy mẫu phân tầng theo quy tắc giữ hiếm – cap phổ biến: 100% smooth (980) và erratic (494), "
       "giới hạn 1.000 cho intermittent/lumpy, tổng 3.474 chuỗi.")
body("Để đánh giá ổn định và chống rò rỉ, dữ liệu được chia theo thời gian thành **ba cửa sổ "
     "rolling-origin** trượt lùi 28 ngày, mọi tập test đều ≤ d_1941 (Bảng 3.2). Mỗi cửa sổ gồm train "
     "(quá khứ) → validation (28 ngày, để hiệu chuẩn) → test (28 ngày kế).")
table("Bảng 3.2", "Ba cửa sổ rolling-origin.",
      ["Cửa sổ", "Train (≤)", "Validation", "Test"],
      [["W1", "d_1885", "d_1886–1913", "d_1914–1941"],
       ["W2", "d_1857", "d_1858–1885", "d_1886–1913"],
       ["W3", "d_1829", "d_1830–1857", "d_1858–1885"]])
body("Kiểm chứng tự động (P1) xác nhận: train < test, mỗi test đúng 28 ngày, các cửa sổ không chồng lấn, "
     "data_long đủ 3.474 chuỗi (6.743.034 dòng), không trùng cặp (series_id, d_int) và các cột khoá không "
     "khuyết.")

h2("3.4. Chống rò rỉ và kỹ thuật đặc trưng")
body("Nguyên tắc xuyên suốt là **cấm trộn ngẫu nhiên** – mọi thao tác chỉ dùng quá khứ. Với họ machine "
     "learning, để dự báo đủ 28 ngày test chỉ từ dữ liệu đến gốc, mọi đặc trưng từ sales phải **lùi ít "
     "nhất bằng horizon** (lag ≥ 28): nếu dùng lag-1 sẽ cần biết giá trị ngày hôm trước của test (chưa "
     "có). LightGBM dùng các đặc trưng lag_28/35/56, rolling (rmean_28, rstd_28, rmean_7), số ngày kể từ "
     "lần bán gần nhất, cùng các biến lịch/giá/SNAP. Hệ số chuẩn hoá scale của RMSSE/MASE cũng chỉ tính "
     "trên train.")

h2("3.5. Giao thức mô hình hoá")
body("Họ **cổ điển** (Naive, SeasonalNaive(7), Croston, SBA, TSB qua statsforecast) sinh điểm rồi bọc NB "
     "thành 9 phân vị. **LightGBM** huấn luyện 9 mô hình phân vị riêng cho mỗi cửa sổ, dùng validation để "
     "early-stopping và lưu forecast phục vụ hiệu chuẩn, xử lý quantile crossing bằng sắp xếp đơn điệu. "
     "Ba **foundation model** chạy zero-shot với context ≤ train_end: Chronos-Bolt sinh phân vị gốc (kẹp "
     "đuôi), TTM sinh điểm rồi bọc NB/Poisson, Moirai-2 nội suy phân vị gốc rồi sắp xếp khử crossing. "
     "Đáng chú ý về **bất đối xứng horizon**: cổ điển/LightGBM dự báo test ở h = 1–28, còn ba foundation "
     "model lấy context ≤ train_end và dự báo 56 ngày (val = h 1–28, test = h 29–56) – nghĩa là chúng dự "
     "báo test xa hơn và residual hiệu chuẩn “dễ hơn” test, nên dải sau hiệu chuẩn có thể vẫn "
     "hơi hẹp; mọi kết luận về foundation model được diễn giải kèm lưu ý này.")

h2("3.6. Giao thức hiệu chuẩn và đánh giá")
body("Giao thức được **chốt trước khi xem kết quả** (pre-registration) để tránh thiên lệch lựa chọn. "
     "**Bước hiệu chuẩn**: split-conformal một phía cho từng mức phân vị, residual chuẩn hoá theo scale "
     "MAE-naive của chuỗi, Mondrian theo nhóm nhu cầu; tập hiệu chuẩn của mỗi cửa sổ là forecast "
     "validation out-of-sample mà P3/P4 nộp, bảo đảm không rò rỉ và “cùng một cây thước” cho mọi "
     "mô hình. **Bước metric**: RMSSE (điểm, chính), MASE (phụ), WSPL (xác suất, chính), SPL (phụ), "
     "coverage 50/67/95/99 cùng độ rộng dải 95 và bias để phân tích lỗi; báo cả raw lẫn calibrated, theo "
     "cả balanced lẫn frequency-weighted. **Bước kiểm định**: Diebold–Mariano panel (cluster theo chuỗi, "
     "Holm) và MCB tham chiếu, áp dụng win rule đã nêu ở Mục 2.9.2.")
pagebreak()

# ================================================================ CHƯƠNG 4
h1("CHƯƠNG 4: KẾT QUẢ THỰC NGHIỆM")

h2("4.1. Phân nhóm và đặc tính nhu cầu")
body("Áp ngưỡng SBC lên 30.490 chuỗi cho phân bố **cực kỳ mất cân bằng** (Bảng 4.1): hai nhóm thưa "
     "**intermittent** (75,75%) và **lumpy** (19,42%) chiếm tới **95,17%** tổng thể, trong khi smooth chỉ "
     "3,21% và erratic 1,62%. Đây là đặc tính thực của bán lẻ M5 – phần lớn SKU bán lẻ tẻ, nhiều ngày = 0 "
     "(zero-rate trung bình của intermittent ≈ 0,74; lumpy ≈ 0,60).")
table("Bảng 4.1", "Phân bố bốn nhóm nhu cầu trên toàn bộ 30.490 chuỗi.",
      ["Nhóm", "Số chuỗi", "Tỷ lệ", "zero_rate (TB)", "ADI (median)", "CV² (median)"],
      [["smooth", "980", "3,21%", "0,138", "1,18", "0,37"],
       ["erratic", "494", "1,62%", "0,167", "1,22", "0,61"],
       ["intermittent", "23.095", "75,75%", "0,738", "4,60", "0,30"],
       ["lumpy", "5.921", "19,42%", "0,604", "2,50", "0,62"]])
body("Phân bố này kéo theo ba hệ quả phương pháp: (i) các metric điểm kém ý nghĩa với chuỗi thưa nên ưu "
     "tiên metric xác suất; (ii) đánh giá phải tách theo nhóm để nhóm thưa không nuốt tín hiệu của nhóm "
     "hiếm; (iii) khi tổng hợp toàn tập cần trọng số theo tần suất để kết luận đại diện đúng dân số. "
     "Hình 4.1–4.3 minh hoạ trực quan phân bố, không gian ADI–CV² và mức độ gián đoạn.")
figure("P2_1.png", "Hình 4.1",
       "Phân bố và đặc trưng bốn nhóm nhu cầu theo khung SBC; bảng dùng median cho ADI/CV² (phân phối "
       "lệch phải mạnh nên trung vị bền hơn trung bình).")
figure("P2_2.png", "Hình 4.2",
       "Không gian ADI–CV²: khối điểm dồn mạnh về phía ADI lớn (đa số chuỗi thưa); ranh giới dọc "
       "ADI = 1,32 là yếu tố tách chính, rất ít chuỗi nằm ở vùng “đều” bên trái.")
figure("P1_3.png", "Hình 4.3",
       "Mức độ gián đoạn (zero-rate) tăng dần smooth → intermittent; nhóm thưa có khoảng 60–90% ngày "
       "bằng 0 – căn cứ để toàn dự án ưu tiên dự báo xác suất và tách nhóm khi đánh giá.")
body("Về đặc tính tiêu thụ (Hình 4.4), nhu cầu trung bình mỗi ngày giảm khoảng **10 lần** theo trục gián "
     "đoạn: smooth ≈ 7,0 và erratic ≈ 6,8 nhưng intermittent ≈ 0,63 và lumpy ≈ 1,58. Về **mùa vụ** "
     "(Hình 4.5), mùa vụ tuần rất rõ – cuối tuần cao hơn ngày thường khoảng **+31%** – trong khi mùa vụ "
     "năm nhẹ (đỉnh tháng 8, đáy tháng 1); điều này biện minh cho baseline SeasonalNaive(7) và cho giá "
     "trị của đặc trưng ngày-trong-tuần. Sự kiện/lễ gần như **không** làm tăng nhu cầu trung bình (thậm "
     "chí giảm nhẹ), nên cờ sự kiện nên dùng ở mức chi tiết theo loại. Ngược lại, **SNAP** làm tăng nhu "
     "cầu ở mọi nhóm (Hình 4.6), mạnh nhất ở lumpy (+16,2%) và erratic (+13,8%), thấp nhất ở intermittent "
     "(+9,7%) – một tín hiệu ngoại sinh ổn định mà machine learning có thể khai thác.")
figure("P2_3.png", "Hình 4.4",
       "Nhu cầu trung bình và cấu trúc tiêu thụ theo nhóm: nhu cầu/ngày chênh ~10 lần giữa nhóm đều và "
       "nhóm thưa, củng cố việc tách nhóm khi đánh giá.")
figure("P2_4.png", "Hình 4.5",
       "Mùa vụ theo ngày trong tuần (cuối tuần +31%) và theo tháng (đỉnh tháng 8, đáy tháng 1).")
figure("P2_5.png", "Hình 4.6",
       "Hiệu ứng SNAP lên nhu cầu theo nhóm: uplift dương toàn bộ, mạnh nhất ở lumpy và erratic.")

h2("4.2. Hành vi dự báo của các mô hình")
body("Trước khi so sánh định lượng, cần hiểu *cách* mỗi họ sinh dự báo. Với LightGBM (Hình 4.7), tầm "
     "quan trọng đặc trưng cho thấy **nhu cầu gần đây chi phối**: rmean_28 (~67%) và rstd_28 (~17%) áp "
     "đảo, các lag thô đóng góp nhỏ – hợp lý cho chuỗi bán lẻ. Về đường median (Hình 4.8), LightGBM bám "
     "mùa vụ tuần sát nhất, trong khi Croston/Naive cho đường mượt hoặc phẳng hơn do sinh từ điểm rồi bọc "
     "NB.")
figure("P3_1.png", "Hình 4.7",
       "Tầm quan trọng đặc trưng của LightGBM: nhu cầu và biến động gần đây (rmean_28, rstd_28, rmean_7) "
       "chi phối dự báo.")
figure("P3_2.png", "Hình 4.8",
       "Dự báo median của các mô hình so với thực tế: LightGBM bám mùa vụ tuần sát nhất; cổ điển cho "
       "đường mượt/phẳng hơn.")
body("Về **độ rộng khoảng** (Hình 4.9 và Hình 4.10), LightGBM (phân vị gốc) cho khoảng hẹp hơn, còn họ "
     "cổ điển bọc NB cho khoảng rộng hơn. Khác biệt này chủ yếu do **cách sinh phân phối** (gốc so với "
     "bọc NB), không phải chênh năng lực – đây chính là lý do bắt buộc phải hiệu chuẩn chung ở Mục 4.5 "
     "trước khi chấm coverage và SPL chính thức.")
figure("P3_3.png", "Hình 4.9",
       "Độ rộng khoảng dự báo – cổ điển (bọc NB) rộng hơn LightGBM (phân vị gốc); khác biệt do lớp sinh "
       "phân phối, sẽ được hiệu chuẩn ở bước sau.")
figure("P3_4.png", "Hình 4.10",
       "Dải phân vị của LightGBM: chín mức phân vị gốc ôm quanh thực tế, median bám mùa vụ tuần, khoảng "
       "hẹp hơn nhóm cổ điển.")
body("Với foundation model, Hình 4.11 cho thấy ba mô hình bám mùa vụ ở các mức khác nhau; Hình 4.12 và "
     "Hình 4.13 làm rõ đặc tính đuôi: Chronos và Moirai **kẹp đuôi** [0,1; 0,9] nên hồ sơ phân vị phẳng "
     "ở hai biên, trong khi TTM bọc NB cho đuôi **trải đều** và khoảng rộng nhất. Hình 4.14 so sánh độ "
     "rộng phân phối cùng chi phí tính toán: Chronos-Bolt tốn ~93,5 s, Moirai-2 ~36,7 s và TTM chỉ ~8,0 s "
     "cho ba cửa sổ × 3.474 chuỗi – chênh lệch chi phí đáng kể giữa các kiến trúc.")
figure("P4_1.png", "Hình 4.11",
       "Dự báo median của ba foundation model (Chronos-Bolt, TTM, Moirai-2) so với thực tế trên một chuỗi "
       "smooth và một chuỗi lumpy.")
figure("P4_3.png", "Hình 4.12",
       "Dải phân vị của ba foundation model so với thực tế: TTM (bọc NB) cho dải rộng nhất; Chronos/Moirai "
       "hẹp đuôi do kẹp biên.")
figure("P4_4.png", "Hình 4.13",
       "Hồ sơ phân vị (chuỗi smooth): đuôi phẳng do kẹp [0,1; 0,9] của Chronos/Moirai so với đuôi trải "
       "đều của TTM bọc NB.")
figure("P4_2.png", "Hình 4.14",
       "Độ rộng phân phối và chi phí tính toán của foundation model: Chronos-Bolt ~93,5 s, Moirai-2 "
       "~36,7 s, TTM ~8,0 s cho ba cửa sổ × 3.474 chuỗi.")

h2("4.3. Chất lượng dự báo xác suất – WSPL")
body("Trên tiêu chí chính **WSPL (đã hiệu chuẩn)**, trung bình ba cửa sổ, **LightGBM đạt điểm thấp nhất "
     "toàn cục** ở cả hai cách gộp – balanced 0,252 và frequency-weighted 0,265 – kế đến Moirai-2 "
     "(0,260 / 0,285) và Chronos-Bolt (0,274 / 0,302). Theo từng nhóm (Bảng 4.2), LightGBM dẫn ở ba trong "
     "bốn nhóm (smooth, intermittent, lumpy), còn Moirai-2 thấp nhất ở erratic.")
table("Bảng 4.2", "WSPL (đã hiệu chuẩn) theo model × nhóm (thấp hơn là tốt hơn; ★ = tốt nhất cột).",
      ["Model", "smooth", "erratic", "intermittent", "lumpy"],
      [["naive", "0,294", "0,368", "0,398", "0,431"],
       ["snaive", "0,254", "0,340", "0,374", "0,413"],
       ["croston", "0,211", "0,301", "0,316", "0,356"],
       ["sba", "0,211", "0,298", "0,316", "0,355"],
       ["tsb", "0,216", "0,305", "0,318", "0,362"],
       ["lgbm", "0,200 ★", "0,248", "0,260 ★", "0,300 ★"],
       ["chronos_bolt", "0,211", "0,254", "0,300", "0,330"],
       ["ttm", "0,224", "0,307", "0,331", "0,375"],
       ["moirai_2", "0,210", "0,241 ★", "0,284", "0,306"]])
body("Cần lưu ý hai cách gộp đều tính **trên cùng mẫu 3.474 chuỗi**: balanced là trung bình đều 4 nhóm, "
     "còn frequency-weighted gán trọng số theo tỷ lệ dân số 30.490 chuỗi (nên nhóm intermittent/lumpy chi "
     "phối) – đây không phải chạy lại trên toàn 30.490. Hình 4.15 trực quan hoá thứ hạng WSPL.")
figure("P5_2.png", "Hình 4.15",
       "Bản đồ nhiệt WSPL (đã hiệu chuẩn) theo model × nhóm; ô đậm = tốt nhất cột. LightGBM dẫn ba nhóm, "
       "Moirai-2 ở erratic.")

h2("4.4. Độ chính xác điểm – RMSSE")
body("Độ chính xác điểm (RMSSE đã hiệu chuẩn) xác nhận lại thứ hạng WSPL: LightGBM dẫn ở smooth (0,737), "
     "intermittent (0,803) và lumpy (0,726), còn Moirai-2 tốt nhất ở erratic (0,687); Naive và "
     "SeasonalNaive kém nhất ở mọi nhóm (Hình 4.16).")
figure("P5_4.png", "Hình 4.16",
       "Bản đồ nhiệt RMSSE (đã hiệu chuẩn) theo model × nhóm; thấp hơn là tốt hơn. Độ chính xác điểm xác "
       "nhận lại thứ hạng WSPL.")

h2("4.5. Hiệu chuẩn độ phủ")
body("Trước hiệu chuẩn, Chronos và Moirai **thiếu phủ đuôi** (coverage-95 ≈ 0,75 do kẹp [0,1; 0,9]), "
     "trong khi nhóm bọc NB (croston/sba/tsb) hơi **thừa phủ** (≈ 0,98). Sau split-conformal, mọi mô hình "
     "về khoảng **0,95–0,99** (Hình 4.17 và Hình 4.18) – xác nhận lớp hiệu chuẩn chung hoạt động và đây "
     "là lý do bắt buộc phải có bước hiệu chuẩn trước khi so sánh.")
figure("P5_1.png", "Hình 4.17",
       "Coverage danh nghĩa so với thực tế (raw → calibrated) theo model × nhóm; đường chéo = hiệu chuẩn "
       "hoàn hảo, dưới đường chéo = dải quá hẹp.")
figure("P5_3.png", "Hình 4.18",
       "Coverage-95 trước và sau hiệu chuẩn: conformal kéo Chronos/Moirai từ ~0,75 về sát danh nghĩa 0,95.")
body("Một lưu ý quan trọng: với dữ liệu đếm có sàn 0, khi phân vị 2,5% bằng 0 thì không thể “miss "
     "phía dưới”, nên coverage-95 thực tế hội tụ về khoảng 0,975 chứ không đúng 0,95. Đây là đặc tính "
     "của dữ liệu gián đoạn, không phải lỗi hiệu chuẩn – phía trên (phía quyết định tồn kho) vẫn đạt mức "
     "danh nghĩa.")

h2("4.6. Kiểm định thống kê và bảng quyết định")
body("Áp win rule lên kết quả WSPL hiệu chuẩn (Bảng 4.3), chỉ nhóm **smooth** cho kết luận chắc chắn "
     "thống kê: LightGBM **thắng rõ** với chênh +4,9% so với á quân và p = 0,007 (DM, Holm). Ba nhóm còn "
     "lại (erratic, intermittent, lumpy) có nhiều mô hình **tương đương** về thống kê (p ≫ 0,05) – khi đó "
     "nghiên cứu khuyến nghị mô hình **đơn giản/rẻ** (SeasonalNaive, Croston), dù mô hình mạnh nhất theo "
     "WSPL lần lượt là Moirai-2 (erratic) và LightGBM (intermittent, lumpy).")
table("Bảng 4.3", "Khuyến nghị “nhu cầu nào → model nào” và kết quả kiểm định (tiêu chí: WSPL calibrated).",
      ["Nhóm", "Khuyến nghị", "Mạnh nhất", "Kết luận", "Chênh á quân", "p (DM, Holm)", "Cov-95"],
      [["smooth", "LightGBM", "lgbm", "thắng rõ", "+4,9%", "0,007", "0,974"],
       ["erratic", "SeasonalNaive", "moirai_2", "tương đương", "+3,1%", "0,418", "0,973"],
       ["intermittent", "Croston", "lgbm", "tương đương", "+9,4%", "0,163", "0,987"],
       ["lumpy", "LightGBM", "lgbm", "tương đương", "+2,2%", "0,302", "0,972"]])

h2("4.7. Phân tích lỗi")
body("Bảng 4.4 phân rã lỗi hệ thống của các mô hình khuyến nghị. Trường hợp đáng chú ý là **croston ở "
     "nhóm intermittent**: bias âm mạnh (−0,831) và over_rate rất nhỏ (0,073). Điều này phản ánh đúng bản "
     "chất nhu cầu gián đoạn – median thường bằng 0 nên lỗi chủ yếu là **thiên lệch thấp ở chuỗi nhiều "
     "0**, không phải sai hệ thống về dải (coverage vẫn ổn định ở 0,987). Các nhóm còn lại có bias nhẹ và "
     "tỷ lệ vượt/thiếu tương đối cân đối.")
table("Bảng 4.4", "Lỗi hệ thống của model khuyến nghị (chuẩn hoá theo scale).",
      ["Nhóm", "Model", "zero_rate", "bias", "over_rate", "under_rate", "Cov-95"],
      [["smooth", "lgbm", "0,138", "−0,149", "0,501", "0,499", "0,974"],
       ["erratic", "snaive", "0,167", "−0,107", "0,517", "0,483", "0,973"],
       ["intermittent", "croston", "0,738", "−0,831", "0,073", "0,332", "0,987"],
       ["lumpy", "lgbm", "0,604", "−0,389", "0,481", "0,406", "0,972"]])
pagebreak()

# ================================================================ CHƯƠNG 5
h1("CHƯƠNG 5: KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN")

h2("5.1. Kết luận")
body("Nghiên cứu đã xây dựng và kiểm chứng một khung so sánh công bằng ba họ mô hình dự báo xác suất nhu "
     "cầu gián đoạn, phân nhóm theo đặc tính nhu cầu, trên bộ M5. Trả lời trực tiếp hai câu hỏi nghiên cứu:")
bullet("**Nhu cầu nào → mô hình nào.** Với nhóm đều và ổn định (**smooth**), **LightGBM thắng rõ** về "
       "thống kê (p = 0,007). Với ba nhóm thưa/biến động chiếm ~95% tập (erratic, intermittent, lumpy), "
       "**không có mô hình thắng tuyệt đối** – các mô hình tương đương về thống kê, nên nên dùng baseline "
       "cổ điển rẻ (SeasonalNaive, Croston) làm mặc định, hoặc LightGBM như một lựa chọn chung an toàn vì "
       "có WSPL toàn cục thấp nhất.")
bullet("**Foundation model có hơn không.** Moirai-2 nhỉnh ở erratic nhưng **không vượt ngưỡng ý "
       "nghĩa**, đồng thời chi phí tính toán cao hơn nhiều (Chronos ~93,5 s so với TTM ~8,0 s). Do đó "
       "**chưa đủ bằng chứng** để ưu tiên foundation model zero-shot trên M5 theo tiêu chí xác suất.")
body("Hai thông điệp phương pháp cũng được khẳng định: **phân nhóm theo đặc tính nhu cầu là điều kiện "
     "cần** để kết luận đúng (một trung bình toàn tập sẽ che giấu khác biệt theo nhóm), và **hiệu chuẩn "
     "split-conformal chung là bắt buộc** để so sánh công bằng (nó sửa được thiếu phủ đuôi của foundation "
     "model, kéo coverage-95 từ ~0,75 về sát 0,95). Thông điệp cuối cùng: không có “mô hình tốt "
     "nhất” đơn lẻ; lựa chọn phụ thuộc nhóm nhu cầu, và ở phần lớn tập nó nằm trong sai số thống kê – "
     "nên tối ưu theo **chi phí vận hành** khi hiệu năng ngang nhau.")

h2("5.2. Hạn chế của nghiên cứu")
bullet("**Rò rỉ tiền huấn luyện foundation model.** Đã rà model card và đánh giá rủi ro trực tiếp là "
       "thấp (M5 là benchmark zero-shot của Chronos, không nằm trong corpus công bố của TTM/Moirai), "
       "nhưng các corpus quy mô lớn không công bố đầy đủ nên vẫn cần thận trọng.")
bullet("**Bất đối xứng horizon.** Cổ điển/LightGBM dự báo test ở h = 1–28, còn ba foundation model dự "
       "báo test ở h = 29–56 (dùng h = 1–28 làm validation để hiệu chuẩn); residual hiệu chuẩn “dễ "
       "hơn” test nên dải foundation model sau hiệu chuẩn có thể vẫn hơi hẹp.")
bullet("**Coverage rời rạc.** Dữ liệu đếm có sàn 0 khiến coverage-95 hội tụ ~0,975 thay vì đúng 0,95.")
bullet("**Phạm vi mẫu.** Mọi metric tính trên mẫu phân tầng 3.474 chuỗi; bản frequency-weighted tái tạo "
       "tỷ trọng dân số 30.490 bằng trọng số chứ chưa chấm lại trực tiếp trên toàn bộ – kết luận cho "
       "quy mô đầy đủ cần xác nhận thêm.")
bullet("**Few-shot foundation model** là ablation tuỳ chọn và chưa thực hiện.")

h2("5.3. Hướng phát triển")
body("Các hướng tiếp theo gồm: (i) **chấm lại trực tiếp trên toàn bộ 30.490 chuỗi** để xác nhận kết "
     "luận ở quy mô đầy đủ thay vì qua trọng số; (ii) thực hiện **few-shot/fine-tune nhẹ** cho foundation "
     "model trên một lát train để kiểm tra liệu ưu thế có xuất hiện khi mô hình được thích nghi với M5; "
     "(iii) bổ sung **biến ngoại sinh** (giá, SNAP, sự kiện theo loại) cho các mô hình hỗ trợ covariate; "
     "(iv) mở rộng sang **tổ hợp mô hình** (model combination) cho nhu cầu gián đoạn, vốn thường cải thiện "
     "độ ổn định; và (v) khảo sát **cân bằng chi phí – hiệu năng** một cách hệ thống để hỗ trợ quyết định "
     "triển khai ở quy mô hàng chục nghìn SKU.")
pagebreak()

# ================================================================ TÀI LIỆU THAM KHẢO
h1("DANH MỤC TÀI LIỆU THAM KHẢO")
refs = [
    "Makridakis, S., Spiliotis, E., & Assimakopoulos, V. (2022). The M5 Accuracy competition: Results, findings and conclusions. International Journal of Forecasting.",
    "M5 Forecasting – Accuracy & Uncertainty. Kaggle/Walmart (M-competitions).",
    "Syntetos, A. A., & Boylan, J. E. (2005). The accuracy of intermittent demand estimates. International Journal of Forecasting, 21(2), 303–314.",
    "Croston, J. D. (1972). Forecasting and stock control for intermittent demands. Operational Research Quarterly, 23(3), 289–303.",
    "Teunter, R. H., Syntetos, A. A., & Babai, M. Z. (2011). Intermittent demand: Linking forecasting to inventory obsolescence (TSB). European Journal of Operational Research.",
    "Ke, G., et al. (2017). LightGBM: A highly efficient gradient boosting decision tree. NeurIPS.",
    "Ansari, A. F., et al. (2024). Chronos: Learning the Language of Time Series. TMLR. arXiv:2403.07815.",
    "Ekambaram, V., et al. (2024). Tiny Time Mixers (TTM): Fast pre-trained models for enhanced zero/few-shot forecasting. arXiv:2401.03955.",
    "Woo, G., et al. (2024). Unified Training of Universal Time Series Forecasting Transformers (Moirai / Moirai-2). Salesforce.",
    "Vovk, V., Gammerman, A., & Shafer, G. Algorithmic Learning in a Random World (Conformal prediction).",
    "Romano, Y., Patterson, E., & Candès, E. (2019). Conformalized Quantile Regression. NeurIPS.",
    "Gibbs, I., & Candès, E. (2021). Adaptive conformal inference under distribution shift. NeurIPS.",
    "Diebold, F. X., & Mariano, R. S. (1995). Comparing predictive accuracy. Journal of Business & Economic Statistics, 13(3), 253–263.",
    "Harvey, D., Leybourne, S., & Newbold, P. (1997). Testing the equality of prediction mean squared errors. International Journal of Forecasting.",
    "Koning, A. J., Franses, P. H., Hibon, M., & Stekler, H. O. (2005). The M3 competition: Statistical tests of the results (MCB). International Journal of Forecasting.",
    "Wang, X., Kang, Y., & Petropoulos, F. (2024). Combining probabilistic forecasts of intermittent demand. European Journal of Operational Research.",
]
for i, r in enumerate(refs, 1):
    p = doc.add_paragraph(); p.alignment = ALIGN.JUSTIFY
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.left_indent = Cm(0.75)
    p.paragraph_format.first_line_indent = Cm(-0.75)
    rr = p.add_run(f"[{i}] "); rr.bold = True
    p.add_run(r)

body("", indent=False)
body("Báo cáo tổng hợp từ P1 (dữ liệu & điều phối), P2 (EDA & phân nhóm), P3 (cổ điển & machine "
     "learning), P4 (foundation model) và P5 (hiệu chuẩn & đánh giá). Số liệu trích trực tiếp từ "
     "data/outputs/ và các notebook P1–P5; hình minh hoạ lấy từ kết quả đã lưu trong các notebook.",
     indent=False, size=11, italic=True)

doc.save(OUT)
print("SAVED:", OUT)
