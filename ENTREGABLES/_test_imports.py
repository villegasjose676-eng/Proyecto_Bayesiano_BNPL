# -*- coding: utf-8 -*-
"""
Generador de PDFs v2 FINAL — Proyecto Bayesiano BNPL
ReportLab | Informe academico completo, Poster A1, Dashboard evidencia
"""
import os, sys
import numpy as np

BASE        = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGURAS     = os.path.join(BASE, 'figuras')
ENTREGABLES = os.path.join(BASE, 'ENTREGABLES')

from reportlab.lib.colors import HexColor, white, black
NAVY    = HexColor('#0f2444')
BLUE    = HexColor('#1d4ed8')
BLUE_LT = HexColor('#eff6ff')
BLUE_MID= HexColor('#bfdbfe')
GREEN   = HexColor('#16a34a')
GREEN_LT= HexColor('#f0fdf4')
GREEN_BD= HexColor('#bbf7d0')
RED     = HexColor('#dc2626')
RED_LT  = HexColor('#fef2f2')
AMBER   = HexColor('#d97706')
AMBER_LT= HexColor('#fef3c7')
AMBER_BD= HexColor('#fde68a')
GRAY    = HexColor('#64748b')
GRAY_LT = HexColor('#f8fafc')
BORDER  = HexColor('#e2e8f0')
SLATE   = HexColor('#334155')
from reportlab.lib import colors

from reportlab.lib.pagesizes import A4, landscape, A1
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus.flowables import Flowable

def img(name, width, height):
    path = os.path.join(FIGURAS, name)
    if not os.path.exists(path):
        return Spacer(width, height)
    return Image(path, width=width, height=height)

class SectionRule(Flowable):
    def __init__(self, width, color=NAVY, thickness=1.5):
        Flowable.__init__(self)
        self.width = width; self.color = color
        self.thickness = thickness; self.height = thickness + 3
    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, 0, self.width, 0)

def make_styles():
    s = getSampleStyleSheet()
    def add(name, parent='Normal', **kw):
        if name not in s:
            s.add(ParagraphStyle(name=name, parent=s[parent], **kw))
    add('H1', fontName='Helvetica-Bold', fontSize=14, textColor=NAVY, spaceBefore=22, spaceAfter=4, leading=18)
    add('H2', fontName='Helvetica-Bold', fontSize=11, textColor=BLUE, spaceBefore=14, spaceAfter=3, leading=15)
    add('H3', fontName='Helvetica-Bold', fontSize=9.5, textColor=SLATE, spaceBefore=10, spaceAfter=3, leading=13)
    add('Body', fontName='Helvetica', fontSize=9.5, textColor=colors.black, spaceAfter=6, leading=14, alignment=TA_JUSTIFY)
    add('BodySm', fontName='Helvetica', fontSize=8.5, textColor=SLATE, spaceAfter=5, leading=12, alignment=TA_JUSTIFY)
    add('Caption', fontName='Helvetica-Oblique', fontSize=7.5, textColor=GRAY, spaceAfter=8, alignment=TA_CENTER, leading=10)
    add('Bullet', fontName='Helvetica', fontSize=9.5, textColor=colors.black, spaceAfter=4, leading=14, leftIndent=14, firstLineIndent=-14)
    add('TH', fontName='Helvetica-Bold', fontSize=8, textColor=white, alignment=TA_LEFT, leading=10)
    add('TD', fontName='Helvetica', fontSize=8, textColor=colors.black, alignment=TA_LEFT, leading=11)
    add('CallTitle', fontName='Helvetica-Bold', fontSize=9, textColor=NAVY, spaceAfter=3, leading=12)
    add('CallBody', fontName='Helvetica', fontSize=8.5, textColor=colors.black, spaceAfter=3, leading=12)
    add('TOC1', fontName='Helvetica-Bold', fontSize=10.5, textColor=NAVY, spaceAfter=6, leading=14)
    add('TOC2', fontName='Helvetica', fontSize=9.5, textColor=SLATE, spaceAfter=4, leading=13, leftIndent=12)
    return s
ST = make_styles()

def P(text, style='Body'):   return Paragraph(text, ST[style])
def sp(h=5):                 return Spacer(1, h*mm)
def rule(w, c=NAVY, t=1.5): return SectionRule(w, c, t)
def bul(text):               return P(f'&#8226; {text}', 'Bullet')

def ts_base():
    return TableStyle([
        ('BACKGROUND',    (0,0), (-1,0),  NAVY),
        ('TEXTCOLOR',     (0,0), (-1,0),  white),
        ('FONTNAME',      (0,0), (-1,0),  'Helvetica-Bold'),
        ('FONTSIZE',      (0,0), (-1,0),  8),
        ('FONTNAME',      (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE',      (0,1), (-1,-1), 8),
        ('ROWBACKGROUNDS',(0,1), (-1,-1), [white, GRAY_LT]),
        ('GRID',          (0,0), (-1,-1), 0.3, BORDER),
        ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING',    (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING',   (0,0), (-1,-1), 6),
        ('RIGHTPADDING',  (0,0), (-1,-1), 6),
    ])

def callout(title, lines, bg=GREEN_LT, bd=GREEN, stripe=GREEN):
    rows = []
    if title:
        rows.append([P(title, 'CallTitle')])
    for l in lines:
        rows.append([P(l, 'CallBody')])
    inner = Table(rows, colWidths=['100%'])
    inner.setStyle(TableStyle([
        ('TOPPADDING',(0,0),(-1,-1),2), ('BOTTOMPADDING',(0,0),(-1,-1),2),
        ('LEFTPADDING',(0,0),(-1,-1),0), ('RIGHTPADDING',(0,0),(-1,-1),0),
    ]))
    t = Table([[Spacer(3*mm,1), inner]], colWidths=[4*mm, '100%'])
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),bg),
        ('LINEBEFORE',(0,0),(0,-1),3.5,stripe),
        ('BOX',(0,0),(-1,-1),0.5,bd),
        ('TOPPADDING',(0,0),(-1,-1),8), ('BOTTOMPADDING',(0,0),(-1,-1),8),
        ('LEFTPADDING',(1,0),(1,-1),8), ('RIGHTPADDING',(1,0),(1,-1),10),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
    ]))
    return t

def draw_cover(c, pw, ph, title_lines, subtitle, authors, course, doc_type='INFORME ACADEMICO'):
    steps = 50
    for i in range(steps):
        t = i/steps
        r=int(0x0f+t*(0x16-0x0f)); g=int(0x24+t*(0x3a-0x24)); b=int(0x44+t*(0x6b-0x44))
        c.setFillColor(HexColor(f'#{r:02x}{g:02x}{b:02x}'))
        c.rect(0, ph*i/steps, pw, ph/steps+1, fill=1, stroke=0)
    c.setFillColor(HexColor('#ffffff08'))
    c.circle(pw-40*mm, ph-50*mm, 80*mm, fill=1, stroke=0)
    c.setStrokeColor(HexColor('#3b82f6')); c.setLineWidth(2.5)
    c.line(22*mm, ph-45*mm, pw*0.45, ph-45*mm)
    c.setFillColor(HexColor('#94a3b8')); c.setFont('Helvetica', 7.5)
    c.drawCentredString(pw/2, ph-20*mm, 'ESCUELA SUPERIOR POLITECNICA DEL LITORAL - ESPOL')
    c.setFont('Helvetica', 7)
    c.drawCentredString(pw/2, ph-26*mm, course)
    c.setFillColor(HexColor('#60a5fa')); c.setFont('Helvetica-Bold', 7.5)
    c.drawCentredString(pw/2, ph*0.72, doc_type.upper())
    c.setFillColor(white); c.setFont('Helvetica-Bold', 18)
    y0 = ph*0.67
    for line in title_lines:
        c.drawCentredString(pw/2, y0, line); y0 -= 12*mm
    c.setFillColor(HexColor('#cbd5e1')); c.setFont('Helvetica', 8.5)
    c.drawCentredString(pw/2, y0-5*mm, subtitle)
    bw,bh = 130*mm,40*mm; bx=(pw-bw)/2; by=ph*0.30
    c.setFillColor(HexColor('#ffffff12')); c.setStrokeColor(HexColor('#ffffff22')); c.setLineWidth(1)
    c.roundRect(bx, by, bw, bh, 5, fill=1, stroke=1)
    c.setFillColor(HexColor('#94a3b8')); c.setFont('Helvetica', 7)
    c.drawCentredString(pw/2, by+bh-7*mm, 'INTEGRANTES')
    c.setFillColor(white); c.setFont('Helvetica', 9.5)
    members = [a.strip() for a in authors.split('*')]
    for i,m in enumerate(members):
        c.drawCentredString(pw/2, by+bh-14*mm-i*6.5*mm, m)
    c.setFillColor(HexColor('#475569')); c.setFont('Helvetica', 7)
    c.drawCentredString(pw/2, 12*mm, 'Proyecto Final de Curso  *  I Semestre 2026')

print("Script parcial OK - probando imports")