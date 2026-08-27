
# -*- coding: utf-8 -*-
"""
Generador de PDFs v2 FINAL - Proyecto Bayesiano BNPL
ReportLab | Informe + Poster A1 + Dashboard evidencia
"""
import os, sys

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
    PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
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
    add('H1', fontName='Helvetica-Bold', fontSize=14, textColor=NAVY,
        spaceBefore=22, spaceAfter=4, leading=18)
    add('H2', fontName='Helvetica-Bold', fontSize=11, textColor=BLUE,
        spaceBefore=14, spaceAfter=3, leading=15)
    add('H3', fontName='Helvetica-Bold', fontSize=9.5, textColor=SLATE,
        spaceBefore=10, spaceAfter=3, leading=13)
    add('Body', fontName='Helvetica', fontSize=9.5, textColor=colors.black,
        spaceAfter=6, leading=14, alignment=TA_JUSTIFY)
    add('BodySm', fontName='Helvetica', fontSize=8.5, textColor=SLATE,
        spaceAfter=5, leading=12, alignment=TA_JUSTIFY)
    add('Caption', fontName='Helvetica-Oblique', fontSize=7.5, textColor=GRAY,
        spaceAfter=8, alignment=TA_CENTER, leading=10)
    add('Bullet', fontName='Helvetica', fontSize=9.5, textColor=colors.black,
        spaceAfter=4, leading=14, leftIndent=14, firstLineIndent=-14)
    add('TH', fontName='Helvetica-Bold', fontSize=8, textColor=white,
        alignment=TA_CENTER, leading=10)
    add('TD', fontName='Helvetica', fontSize=8, textColor=colors.black,
        leading=11)
    add('CallTitle', fontName='Helvetica-Bold', fontSize=9, textColor=NAVY,
        spaceAfter=3, leading=12)
    add('CallBody', fontName='Helvetica', fontSize=8.5, textColor=colors.black,
        spaceAfter=3, leading=12)
    add('TOC1', fontName='Helvetica-Bold', fontSize=10.5, textColor=NAVY,
        spaceAfter=6, leading=14)
    add('TOC2', fontName='Helvetica', fontSize=9.5, textColor=SLATE,
        spaceAfter=4, leading=13, leftIndent=12)
    return s


ST = make_styles()


def P(text, style='Body'):   return Paragraph(text, ST[style])
def sp(h=5):                 return Spacer(1, h*mm)
def rule(w, c=NAVY, t=1.5): return SectionRule(w, c, t)
def bul(text):               return P('&#8226; ' + text, 'Bullet')


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


def callout(title, lines, bg=GREEN_LT, bd=GREEN, stripe=GREEN, w=0):
    """Single-col callout with LINEBEFORE stripe. Safe in any nesting context."""
    rows = []
    if title:
        rows.append([P(title, 'CallTitle')])
    for l in lines:
        rows.append([P(l, 'CallBody')])
    cw = [w] if w > 0 else ['100%']
    t = Table(rows, colWidths=cw)
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),bg),
        ('LINEBEFORE',(0,0),(0,-1),4,stripe),
        ('BOX',(0,0),(-1,-1),0.5,bd),
        ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),
        ('LEFTPADDING',(0,0),(-1,-1),12),('RIGHTPADDING',(0,0),(-1,-1),10),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
    ]))
    return t


def draw_cover(c, pw, ph, title_lines, subtitle, authors, course,
               doc_type='INFORME ACADEMICO'):
    """Portada formal academica — fondo blanco, diseño sobrio."""
    # Fondo blanco
    c.setFillColor(white)
    c.rect(0, 0, pw, ph, fill=1, stroke=0)

    # Barra superior azul marino
    BAR_H = 18*mm
    c.setFillColor(NAVY)
    c.rect(0, ph-BAR_H, pw, BAR_H, fill=1, stroke=0)
    c.setFillColor(white); c.setFont('Helvetica-Bold', 10)
    c.drawCentredString(pw/2, ph-10*mm, 'ESCUELA SUPERIOR POLITECNICA DEL LITORAL')
    c.setFont('Helvetica', 8)
    c.drawCentredString(pw/2, ph-15*mm, 'ESPOL')

    # Linea divisoria delgada bajo la barra
    c.setStrokeColor(HexColor('#1d4ed8')); c.setLineWidth(0.5)
    c.line(22*mm, ph-BAR_H-0.5*mm, pw-22*mm, ph-BAR_H-0.5*mm)

    # Subtitulo de curso (gris)
    c.setFillColor(GRAY); c.setFont('Helvetica', 9)
    c.drawCentredString(pw/2, ph-28*mm, course)

    # Tipo de documento (etiqueta pequena azul)
    c.setFillColor(BLUE); c.setFont('Helvetica-Bold', 8)
    c.drawCentredString(pw/2, ph*0.73, doc_type.upper())

    # Linea decorativa corta centrada
    lx = pw/2 - 18*mm
    c.setStrokeColor(NAVY); c.setLineWidth(1)
    c.line(lx, ph*0.725, lx+36*mm, ph*0.725)

    # Titulo del proyecto (grande, azul marino)
    c.setFillColor(NAVY); c.setFont('Helvetica-Bold', 17)
    y0 = ph*0.67
    for line in title_lines:
        c.drawCentredString(pw/2, y0, line); y0 -= 11*mm

    # Subtitulo metodologico (gris discreto)
    c.setFillColor(GRAY); c.setFont('Helvetica-Oblique', 8)
    c.drawCentredString(pw/2, y0-6*mm, subtitle)

    # Caja de integrantes — borde fino azul, fondo gris muy suave
    bw, bh = 120*mm, 44*mm
    bx = (pw-bw)/2; by = ph*0.30
    c.setFillColor(HexColor('#f8fafc'))
    c.setStrokeColor(HexColor('#cbd5e1')); c.setLineWidth(0.6)
    c.roundRect(bx, by, bw, bh, 4, fill=1, stroke=1)
    # Acento izquierdo de la caja
    c.setFillColor(NAVY)
    c.roundRect(bx, by, 3*mm, bh, 2, fill=1, stroke=0)
    # Encabezado de la caja
    c.setFillColor(GRAY); c.setFont('Helvetica-Bold', 7)
    c.drawCentredString(pw/2, by+bh-7*mm, 'INTEGRANTES')
    # Linea horizontal dentro de la caja
    c.setStrokeColor(HexColor('#e2e8f0')); c.setLineWidth(0.4)
    c.line(bx+6*mm, by+bh-9.5*mm, bx+bw-4*mm, by+bh-9.5*mm)
    # Nombres
    c.setFillColor(HexColor('#1e293b')); c.setFont('Helvetica', 9)
    members = [a.strip() for a in authors.split('|')]
    for i, m in enumerate(members):
        c.drawCentredString(pw/2, by+bh-16*mm-i*6.5*mm, m)

    # Pie de pagina — linea + texto
    c.setStrokeColor(HexColor('#e2e8f0')); c.setLineWidth(0.4)
    c.line(22*mm, 20*mm, pw-22*mm, 20*mm)
    c.setFillColor(GRAY); c.setFont('Helvetica', 7.5)
    c.drawCentredString(pw/2, 13*mm, 'Proyecto Final de Curso  |  Termino 1 - 2026')


# =============================================================================
# INFORME
# =============================================================================
def build_informe():
    out = os.path.join(ENTREGABLES, 'informe_BNPL.pdf')
    W, H = A4; ML=MR=22*mm; MT=MB=22*mm; CW=W-ML-MR

    doc = SimpleDocTemplate(out, pagesize=A4,
        leftMargin=ML, rightMargin=MR, topMargin=MT, bottomMargin=MB,
        title='Inferencia Bayesiana sobre el Riesgo de Incumplimiento en Consumidores BNPL',
        author='Parrales | Villegas | Paredes | Benitez - ESPOL')

    def on_first_page(c, doc):
        draw_cover(c, W, H,
            ['Inferencia Bayesiana sobre el Riesgo de',
             'Incumplimiento en Consumidores BNPL'],
            'Normal-Normal  |  Regresion Bayesiana MCMC-NUTS  |  Beta-Binomial  |  n=10 000',
            'Levi Parrales | Jose Villegas | Alessandro Paredes | Diego Benitez',
            'Estadistica Bayesiana  |  I Semestre 2026')

    def on_later_pages(c, doc):
        c.saveState()
        c.setFillColor(BORDER); c.rect(0, MB-8*mm, W, 0.4, fill=1, stroke=0)
        c.setFillColor(GRAY); c.setFont('Helvetica', 7)
        c.drawString(ML, MB-6*mm,
            'ESPOL  |  Estadistica Bayesiana  |  Inferencia Bayesiana sobre Riesgo BNPL')
        c.drawRightString(W-MR, MB-6*mm, f'Pag. {doc.page}')
        c.restoreState()

    def sec1(t): return [sp(4), P(t,'H1'), rule(CW,NAVY,1.5), sp(3)]
    def sec2(t): return [P(t,'H2'), sp(1)]

    story = [PageBreak()]

    # TOC
    story += [P('Tabla de Contenidos','H1'), rule(CW,NAVY,1.5), sp(6)]
    for num, title in [
        ('1.','Introduccion'), ('2.','Datos y Variable Principal'),
        ('3.','Analisis Descriptivo'),
        ('3.1','Estadisticas descriptivas de las variables cuantitativas'),
        ('3.2','Variables categoricas y distribucion del riesgo'),
        ('3.3','Credit_Score por nivel de riesgo'),
        ('3.4','Relaciones entre variables - matriz de correlaciones'),
        ('4.','Analisis Bayesiano'),
        ('4.1','Modelo 1 - Normal-Normal: Credit_Score por grupo de riesgo'),
        ('4.2','Modelo 2 - Regresion Lineal Bayesiana con MCMC (NUTS)'),
        ('4.3','Modelo 3 - Beta-Binomial: tasa de pagos tardios por empleo'),
        ('5.','Analisis Etico e Impacto Social'),
        ('6.','Conclusiones'), ('7.','Referencias'),
    ]:
        style = 'TOC1' if len(num)<=2 else 'TOC2'
        story.append(P(f'{num}  {title}', style))
    story.append(PageBreak())

    # 1. INTRODUCCION
    story += sec1('1. Introduccion')
    story.append(P(
        'El modelo de financiamiento <i>Buy Now, Pay Later</i> (BNPL) ha experimentado un '
        'crecimiento acelerado a nivel global. Servicios como Klarna, Afterpay y Affirm '
        'permiten a los consumidores fraccionar compras de comercio electronico en cuotas '
        'diferidas, a menudo sin intereses explicitos, reduciendo la friccion en el momento '
        'de la decision de compra. Sin embargo, este esquema ha generado preocupacion entre '
        'reguladores y academicos: al no reportar a las agencias de credito tradicionales y '
        'no estar sujetos a las mismas verificaciones de solvencia, los servicios BNPL pueden '
        'favorecer la acumulacion silenciosa de deuda, especialmente en consumidores jovenes, '
        'estudiantes o con empleo informal (Dobbie &amp; Song, 2015; Gathergood et al., 2019).'))
    story.append(sp(3))
    story.append(P(
        'El puntaje crediticio (<i>credit score</i>) es la medida operativa estandar de '
        'solvencia financiera y el indicador mas directamente vinculado al riesgo de '
        'incumplimiento. Comprender que factores determinan este puntaje y como varia entre '
        'grupos de consumidores BNPL con distintos perfiles demograficos y laborales es '
        'fundamental tanto para los proveedores del servicio como para los reguladores.'))
    story.append(sp(5))
    story += sec2('Pregunta de investigacion')
    story.append(callout('', [
        '<b>Pregunta:</b> Que factores demograficos, laborales y de comportamiento '
        'financiero explican el Credit_Score de los usuarios de servicios BNPL, y como '
        'difiere este puntaje entre grupos definidos por nivel de riesgo de incumplimiento '
        'y estado de empleo?'
    ], bg=BLUE_LT, bd=BLUE_MID, stripe=BLUE))
    story.append(sp(5))
    story += sec2('Objetivo general')
    story.append(P(
        'Analizar los factores asociados al Credit_Score de usuarios de servicios BNPL '
        'mediante inferencia bayesiana, cuantificando la incertidumbre posterior sobre '
        'las estimaciones y comparando distribuciones entre grupos de riesgo y de estado laboral.'))
    story.append(sp(4))
    story += sec2('Objetivos especificos')
    for txt in [
        'Estimar bayesianamente la distribucion del Credit_Score por grupo de riesgo '
        'mediante un modelo Normal-Normal conjugado y calcular la probabilidad posterior '
        'de que el grupo de bajo riesgo supere al de alto riesgo.',
        'Identificar los predictores demograficos, laborales y conductuales del '
        'Credit_Score mediante regresion lineal bayesiana estimada por MCMC (NUTS), '
        'evaluando la significancia mediante intervalos de credibilidad al 95%.',
        'Comparar la proporcion de pagos tardios entre grupos de estado laboral mediante '
        'un modelo Beta-Binomial conjugado, cuantificando la probabilidad posterior de '
        'diferencias entre grupos.',
        'Evaluar las implicaciones eticas del uso de caracteristicas demograficas y '
        'laborales como predictores en sistemas de scoring crediticio automatizado.',
    ]:
        story.append(bul(txt))
    story.append(PageBreak())

    # 2. DATOS
    story += sec1('2. Datos y Variable Principal')
    story += sec2('2.1 Fuente de datos')
    story.append(P(
        'Se utilizo el <i>BNPL Financial Default Risk Dataset</i> (Kaggle, 2024), un '
        'conjunto de datos <b>sintetico</b> con <b>10 000 observaciones</b> y '
        '<b>11 variables</b>, disenado para simular el comportamiento crediticio de '
        'consumidores de servicios BNPL. La naturaleza sintetica implica que las '
        'relaciones estadisticas son plausibles y estructuralmente coherentes, pero '
        'no directamente extrapolables a poblaciones reales sin validacion adicional.'))
    story.append(sp(4))
    story += sec2('2.2 Descripcion de variables')
    var_data = [
        [P('Variable','TH'), P('Tipo','TH'), P('Descripcion','TH')],
        [P('Age'), P('Continua'), P('Edad del consumidor (anos)')],
        [P('Income_USD'), P('Continua'), P('Ingreso anual en USD')],
        [P('<b>Credit_Score &#9733;</b>'), P('<b>Continua</b>'),
         P('<b>Puntaje crediticio (300-850) - Variable principal</b>')],
        [P('Total_BNPL_Active_Loans'), P('Discreta'), P('Numero de prestamos BNPL activos')],
        [P('Total_BNPL_Debt_USD'), P('Continua'), P('Deuda BNPL total en USD')],
        [P('Average_Transaction_Value_USD'), P('Continua'), P('Valor promedio de transacciones BNPL')],
        [P('Late_Payment_History'), P('Binaria'), P('Historial de pagos tardios (Yes/No)')],
        [P('Employment_Status'), P('Categorica'), P('Employed, Freelancer, Student, Unemployed')],
        [P('Default_Risk'), P('Ordinal'), P('Nivel de riesgo: Low, Medium, High')],
    ]
    t_var = Table(var_data, colWidths=[50*mm, 24*mm, CW-74*mm])
    ts_var = ts_base(); ts_var.add('BACKGROUND',(0,3),(-1,3),BLUE_LT)
    t_var.setStyle(ts_var); story.append(t_var)
    story.append(P('Tabla 1. Descripcion de las variables. &#9733; Variable principal.','Caption'))
    story.append(sp(4))
    story += sec2('2.3 Seleccion y justificacion de la variable principal')
    story.append(P(
        'El <b>Credit_Score</b> fue seleccionado como variable principal por cuatro razones: '
        '(1) es la medida operativa estandar de solvencia crediticia (rango 300-850); '
        '(2) su distribucion es aproximadamente normal (media=663.7, std=76.2, sesgo=-0.66), '
        'lo que hace apropiados los modelos probabilisticos normales; '
        '(3) su correlacion con Default_Risk (r=-0.41) confirma su relevancia; '
        '(4) a diferencia de Total_BNPL_Debt_USD (sesgo=+1.82), no requiere transformaciones '
        'que compliquen la interpretacion de los resultados.'))
    story.append(sp(4))
    story += sec2('2.4 Tratamiento de valores faltantes')
    story.append(P(
        'Credit_Score e Income_USD presentan un 3% de valores faltantes. Bajo el supuesto '
        '<i>MCAR (Missing Completely At Random)</i>, se adopto el analisis de casos completos: '
        '<b>9 702 observaciones</b> para los modelos Normal-Normal y Beta-Binomial, y '
        '<b>9 409 observaciones</b> para la regresion bayesiana. '
        'La perdida es menor al 5% y metodologicamente aceptable.'))
    story.append(PageBreak())

    # 3. DESCRIPTIVO
    story += sec1('3. Analisis Descriptivo')
    story += sec2('3.1 Estadisticas descriptivas - variables cuantitativas')
    story.append(P(
        'La Tabla 2 resume las estadisticas descriptivas. El Credit_Score presenta '
        'distribucion asimetrica a la izquierda (sesgo=-0.66): la mediana (673) es '
        'superior a la media (663.7), indicando una cola hacia puntajes bajos. '
        'Income_USD es aproximadamente simetrico, mientras que Total_BNPL_Debt_USD '
        'muestra fuerte sesgo positivo (sesgo=+1.82), justificando no usarla como '
        'variable principal sin transformacion.'))
    desc_data = [
        [P('Variable','TH'), P('n','TH'), P('Media','TH'), P('Std','TH'),
         P('Min','TH'), P('Mediana','TH'), P('Max','TH'), P('Sesgo','TH')],
        [P('Age'),               P('10 000'), P('34.3'),   P('12.9'),   P('18'),   P('31'),    P('64'),     P('+0.63')],
        [P('Income_USD'),        P('9 695'),  P('53 981'), P('29 797'), P('5 000'),P('58 596'),P('139 452'),P('-0.08')],
        [P('<b>Credit_Score</b>'),P('9 702'), P('<b>663.7</b>'),P('76.2'),P('300'),P('673'),   P('850'),    P('-0.66')],
        [P('BNPL_Active_Loans'), P('10 000'), P('2.32'),  P('1.85'),   P('0'),    P('2'),     P('10'),     P('+1.38')],
        [P('BNPL_Debt_USD'),     P('10 000'), P('348.8'), P('315.1'),  P('0'),    P('262.5'), P('2 731'),  P('+1.82')],
        [P('Avg_Transact_USD'),  P('10 000'), P('331.8'), P('264.4'),  P('10'),   P('294.5'), P('1 420'),  P('+0.79')],
    ]
    t2 = Table(desc_data, colWidths=[42*mm,17*mm,18*mm,15*mm,13*mm,20*mm,20*mm,15*mm])
    ts2 = ts_base(); ts2.add('BACKGROUND',(0,3),(-1,3),BLUE_LT)
    t2.setStyle(ts2)
    story.append(KeepTogether([t2,
        P('Tabla 2. Estadisticas descriptivas. &#9733; Variable principal.','Caption')]))
    story.append(sp(2))
    story.append(KeepTogether([
        img('fig1_distribuciones_continuas.png', CW*0.90, CW*0.47),
        P('Figura 1. Distribuciones de las variables cuantitativas (histograma + KDE). '
          'Se aprecia la asimetria negativa del Credit_Score y la fuerte asimetria '
          'positiva de la deuda BNPL, que justifica la seleccion del Credit_Score.','Caption'),
    ]))
    story += sec2('3.2 Variables categoricas y distribucion del riesgo')
    story.append(P(
        'La variable <b>Default_Risk</b> muestra un marcado desbalance de clases tipico '
        'de datos crediticios: el <b>88.0%</b> pertenece al nivel bajo (<i>Low</i>), '
        'el 6.8% al nivel medio y el 5.2% al nivel alto. Este desbalance refleja que la '
        'gran mayoria de los usuarios no presenta signos de incumplimiento, pero el '
        'subgrupo de alto riesgo es el de mayor interes analitico. '
        'En cuanto a <b>Employment_Status</b>, predominan los empleados formales (60.3%), '
        'seguidos de estudiantes (19.7%), independientes (14.9%) y desempleados (5.1%).'))
    story.append(KeepTogether([
        img('fig2_categoricas.png', CW*0.82, CW*0.43),
        P('Figura 2. Distribucion de las variables categoricas principales. '
          'El desbalance en Default_Risk es caracteristico de datos crediticios reales.','Caption'),
    ]))
    story += sec2('3.3 Credit_Score por nivel de riesgo')
    story.append(P(
        'La diferencia entre el grupo de bajo riesgo (media=675.3) y el de alto riesgo '
        '(media=566.2) asciende a <b>109 puntos</b>, brecha estadisticamente y '
        'practicamente significativa. En terminos del scoring crediticio, esta diferencia '
        'equivale a la transicion entre categorias de credito con impacto directo sobre '
        'tasas de interes y probabilidad de aprobacion. Este hallazgo anticipara los '
        'resultados del analisis bayesiano.'))
    cs_data = [
        [P('Grupo','TH'), P('n','TH'), P('Media','TH'), P('Std','TH'), P('Min','TH'), P('Max','TH')],
        [P('Low (bajo riesgo)'),     P('8 539'), P('675.3'), P('67.4'), P('337'), P('850')],
        [P('Medium (riesgo medio)'), P('654'),   P('587.3'), P('83.2'), P('320'), P('844')],
        [P('High (alto riesgo)'),    P('509'),   P('566.2'), P('79.7'), P('300'), P('770')],
    ]
    t3 = Table(cs_data, colWidths=[60*mm,24*mm,28*mm,24*mm,24*mm,24*mm])
    ts3 = ts_base()
    ts3.add('BACKGROUND',(0,1),(-1,1),GREEN_LT); ts3.add('BACKGROUND',(0,3),(-1,3),RED_LT)
    t3.setStyle(ts3)
    story.append(KeepTogether([t3,
        P('Tabla 3. Estadisticas del Credit_Score por grupo de Default_Risk.','Caption')]))
    story.append(KeepTogether([
        img('fig3_credit_score_por_riesgo.png', CW*0.82, CW*0.45),
        P('Figura 3. Distribucion del Credit_Score por grupo (violin + boxplot). '
          'La separacion entre grupos es clara. La brecha Low-High es de 109 pts.','Caption'),
    ]))
    story += sec2('3.4 Relaciones entre variables - matriz de correlaciones')
    story.append(P(
        'La matriz de correlaciones revela dos relaciones clave: '
        '<b>Credit_Score con Income_USD</b> (r=0.51), asociacion positiva moderada; y '
        '<b>Credit_Score con Default_Risk</b> codificado numericamente (r=-0.41). '
        'Notablemente, las variables de comportamiento BNPL presentan correlaciones '
        'casi nulas con el Credit_Score (prestamos activos: r=0.015; deuda: r=0.008), '
        'sugiriendo que el uso del servicio BNPL per se no predice el puntaje. '
        'Este hallazgo anticipara el resultado de la regresion bayesiana.'))
    story.append(KeepTogether([
        img('fig4_correlaciones.png', CW*0.78, CW*0.57),
        P('Figura 4. Matriz de correlaciones de Pearson. '
          'Correlaciones clave: Credit_Score-Income (r=0.51), Credit_Score-Default_Risk (r=-0.41). '
          'Las variables BNPL tienen correlaciones casi nulas con el Credit_Score.','Caption'),
    ]))
    story.append(PageBreak())

    # 4. BAYESIANO
    story += sec1('4. Analisis Bayesiano')
    story.append(P(
        'El analisis bayesiano se estructura en tres modelos complementarios que forman '
        'una <b>cadena argumental integrada</b>: el primer modelo cuantifica la diferencia '
        'en Credit_Score entre grupos de riesgo; el segundo identifica que variables '
        'predicen ese puntaje; el tercero explica por que ciertos grupos tienen peores '
        'historiales de pago. Juntos construyen una explicacion coherente del riesgo BNPL '
        'desde sus determinantes hasta sus manifestaciones.'))
    story.append(sp(4))

    # 4.1
    story += sec2('4.1 Modelo 1 - Normal-Normal: Credit_Score por grupo de riesgo')
    story += [P('<b>Objetivo</b>','H3'), sp(1)]
    story.append(P(
        'Estimar la distribucion posterior de la media del Credit_Score (mu_k) para '
        'cada grupo de Default_Risk y calcular la probabilidad bayesiana de que el '
        'grupo de bajo riesgo supere al de alto riesgo en puntaje promedio.'))
    story += [sp(3), P('<b>Especificacion y metodo de estimacion</b>','H3'), sp(1)]
    spec_nn = [
        [P('Componente','TH'), P('Distribucion','TH'), P('Justificacion','TH')],
        [P('Verosimilitud'), P('Y_i | mu_k ~ Normal(mu_k, sigma_k^2)'),
         P('Credit_Score es continuo y aprox. normal dentro de cada grupo')],
        [P('Prior'), P('mu_k ~ Normal(mu0=650, tau0=100)'),
         P('mu0=650 pts: media razonable para BNPL. IC 95%=[454,846]: debilmente informativo')],
        [P('Posterior (analitico)'), P('mu_k | datos ~ Normal(mun, taun^2)'),
         P('taun^2=(1/tau0^2+nk/sigmak^2)^-1; mun=taun^2*(mu0/tau0^2+ybar_k*nk/sigmak^2)')],
    ]
    t_nn = Table(spec_nn, colWidths=[32*mm, 68*mm, CW-100*mm])
    t_nn.setStyle(ts_base())
    story.append(KeepTogether([t_nn,
        P('Tabla 4. Especificacion del modelo Normal-Normal. '
          'La conjugacion permite solucion analitica exacta sin simulacion.','Caption')]))
    story.append(sp(3))
    story.append(P(
        'El modelo Normal-Normal es conjugado: la distribucion posterior se obtiene '
        '<b>analiticamente</b> aplicando las formulas de actualizacion bayesiana. '
        'Con muestras grandes (n>500), el prior debilmente informativo tiene influencia '
        'minima y la posterior coincide practicamente con la media muestral. '
        'La distribucion posterior de la diferencia (mu_Low - mu_High) se obtiene '
        'directamente: la diferencia de dos normales es normal, con media y varianza '
        'calculadas de forma exacta.'))
    story += [sp(4), P('<b>Resultados</b>','H3'), sp(1)]
    nn_res = [
        [P('Grupo','TH'), P('n','TH'), P('ybar obs.','TH'), P('mun posterior','TH'),
         P('taun','TH'), P('IC 95% inf.','TH'), P('IC 95% sup.','TH')],
        [P('Low'),    P('8 539'), P('675.33'), P('<b>675.33</b>'), P('0.73'), P('673.90'), P('676.76')],
        [P('Medium'), P('654'),   P('587.32'), P('<b>587.39</b>'), P('3.25'), P('581.02'), P('593.76')],
        [P('High'),   P('509'),   P('566.23'), P('<b>566.33</b>'), P('3.53'), P('559.42'), P('573.25')],
    ]
    t_nnr = Table(nn_res, colWidths=[22*mm,18*mm,24*mm,28*mm,16*mm,26*mm,26*mm])
    ts_nnr = ts_base()
    ts_nnr.add('BACKGROUND',(0,1),(-1,1),GREEN_LT); ts_nnr.add('BACKGROUND',(0,3),(-1,3),RED_LT)
    t_nnr.setStyle(ts_nnr)
    story.append(KeepTogether([t_nnr,
        P('Tabla 5. Distribuciones posteriores de mu_k. Los IC al 95% son muy estrechos '
          '(+-1.5 pts para Low, +-7 pts para High), indicando alta precision en la estimacion.','Caption')]))
    story.append(sp(3))
    story.append(KeepTogether([
        img('fig6_normal_normal_posteriors.png', CW, CW*0.47),
        P('Figura 5. Distribuciones posteriores de mu_k por grupo. Las distribuciones no '
          'se solapan entre si, anticipando la certeza bayesiana del resultado.','Caption'),
    ]))
    story.append(sp(2))
    story.append(callout('Resultado principal - Modelo Normal-Normal', [
        'E[mu_Low - mu_High | datos] = <b>108.99 puntos</b>  |  IC 95%: [101.95, 116.03]',
        'P(mu_High &lt; mu_Low | datos) = <b>1.000000</b>  |  P(mu_Med &lt; mu_Low) = <b>1.000000</b>',
        '',
        'La brecha de 109 puntos entre los grupos extremos se estima con certeza bayesiana '
        'total: el limite inferior del IC al 95% (102 pts) esta muy alejado del cero. '
        'En el contexto del scoring crediticio, esta diferencia equivale a la transicion '
        'entre categorias de credito (p.ej., de "Fair" a "Good" o "Good" a "Very Good" '
        'en escala FICO), con consecuencias directas sobre tasas de interes y aprobacion.',
    ], bg=GREEN_LT, bd=GREEN, stripe=GREEN))
    story.append(sp(3))
    story.append(KeepTogether([
        img('fig7_comparacion_grupos.png', CW*0.80, CW*0.43),
        P('Figura 6. Distribucion posterior de la diferencia mu_Low - mu_High. '
          'Toda la masa de probabilidad esta en valores positivos, confirmando con '
          'certeza bayesiana que el grupo de bajo riesgo tiene mayor Credit_Score.','Caption'),
    ]))
    story.append(PageBreak())

    # 4.2 MCMC
    story += sec2('4.2 Modelo 2 - Regresion Lineal Bayesiana con MCMC (NUTS)')
    story += [P('<b>Objetivo</b>','H3'), sp(1)]
    story.append(P(
        'Identificar que variables demograficas, laborales y conductuales predicen '
        'el Credit_Score, y cuantificar la magnitud e incertidumbre de cada efecto '
        'mediante distribuciones posteriores con IC al 95%.'))
    story += [sp(3), P('<b>Especificacion del modelo</b>','H3'), sp(1)]
    story.append(P(
        'Se especifico un modelo de regresion lineal bayesiana con 9 predictores: '
        '4 variables continuas estandarizadas (z-score), 1 variable binaria y '
        '3 dummies de estado laboral (referencia: Employed):'))
    spec_reg = [
        [P('Componente','TH'), P('Distribucion','TH'), P('Justificacion','TH')],
        [P('Verosimilitud'), P('Credit_Score_i ~ Normal(mu_i, sigma^2)'),
         P('Normal apropiada para variable continua en rango [300,850]')],
        [P('Funcion de enlace'), P('mu_i = beta0 + Sum(betaj*Xij) + gamma_k*Empleo'),
         P('9 predictores; continuas estandarizadas para comparabilidad de coeficientes')],
        [P('Prior intercepto'), P('beta0 ~ Normal(650, 100^2)'),
         P('650 pts media generica BNPL; IC 95%=[454,846] debilmente informativo')],
        [P('Prior coeficientes'), P('betaj ~ Normal(0, 50^2)'),
         P('Centrado en cero (sin efecto a priori); IC 95%=[-98,+98] pts')],
        [P('Prior dispersion'), P('sigma ~ HalfNormal(80)'),
         P('Prior difuso; admite solo valores positivos por definicion')],
    ]
    t_reg = Table(spec_reg, colWidths=[32*mm, 60*mm, CW-92*mm])
    t_reg.setStyle(ts_base())
    story.append(KeepTogether([t_reg,
        P('Tabla 6. Especificacion del modelo de regresion lineal bayesiana.','Caption')]))
    story += [sp(4), P('<b>Metodo de estimacion - MCMC con NUTS</b>','H3'), sp(1)]
    story.append(P(
        'Dado que este modelo no admite solucion analitica, se estimo mediante '
        '<b>Cadenas de Markov Monte Carlo (MCMC)</b> usando el algoritmo '
        '<b>No-U-Turn Sampler (NUTS)</b> en <b>PyMC v5</b>. '
        'NUTS es una variante adaptativa del muestreo de Hamilton (HMC) que ajusta '
        'automaticamente la longitud del trayecto en el espacio de parametros, eliminando '
        'la necesidad de sintonizacion manual y reduciendo drasticamente la autocorrelacion '
        'entre muestras. A diferencia de Metropolis-Hastings, HMC utiliza informacion del '
        'gradiente de la log-posterior para proponer saltos mas eficientes.'))
    story.append(P(
        'La configuracion fue: <b>4 cadenas independientes</b>, <b>1 000 iteraciones de '
        'ajuste</b> (<i>tuning/warm-up</i>) descartadas, <b>1 000 iteraciones de muestreo</b> '
        'por cadena (4 000 muestras totales), target_accept=0.92 y random_seed=42.'))
    story += [sp(4), P('<b>Diagnostico de convergencia</b>','H3'), sp(1)]
    story.append(P(
        'La convergencia se evaluo con tres criterios estandar '
        '(Vehtari et al., 2021; Gelman et al., 2013; Hoffman &amp; Gelman, 2014):'))
    for txt in [
        '<b>R&#770; de Gelman-Rubin:</b> mide varianza entre cadenas relativa a varianza '
        'dentro de las cadenas. R&#770;=1.0 indica convergencia perfecta; criterio: R&#770; &lt; 1.01. '
        'Valor maximo obtenido: <b>1.0013</b> - criterio alcanzado.',
        '<b>ESS (Effective Sample Size):</b> numero efectivo de muestras independientes, '
        'corrigiendo por autocorrelacion. Criterio minimo: ESS &gt; 400. '
        'ESS bulk minimo obtenido: <b>2 675</b> - muy superior al umbral.',
        '<b>Divergencias NUTS:</b> indicadores de problemas geometricos en el espacio '
        'posterior. Se obtuvieron <b>0 divergencias</b>, confirmando exploracion sin '
        'dificultades numericas.',
    ]:
        story.append(bul(txt))
    conv_data = [
        [P('Criterio','TH'), P('Valor obtenido','TH'), P('Umbral','TH'), P('Estado','TH')],
        [P('R&#770; max. (Gelman-Rubin)'), P('1.0013'), P('&lt; 1.01'), P('&#10003; Convergencia')],
        [P('ESS bulk minimo'),             P('2 675'),  P('&gt; 400'), P('&#10003; Suficiente')],
        [P('Divergencias NUTS'),           P('0'),      P('= 0'),      P('&#10003; Sin problemas')],
        [P('Cadenas / Draw / Tune'),       P('4 / 1000 / 1000'), P('-'),P('4 000 muestras totales')],
    ]
    t_conv = Table(conv_data, colWidths=[58*mm,30*mm,25*mm,CW-113*mm])
    ts_conv = ts_base(); ts_conv.add('BACKGROUND',(3,1),(3,3),GREEN_LT)
    t_conv.setStyle(ts_conv)
    story.append(KeepTogether([t_conv,
        P('Tabla 7. Diagnostico de convergencia MCMC. Todos los criterios son satisfactorios.','Caption')]))
    story.append(sp(2))
    story.append(KeepTogether([
        img('fig8_trazas_mcmc.png', CW, CW*0.50),
        P('Figura 7. Trazas MCMC (izq.) y distribuciones marginales posteriores (der.) '
          'para cuatro parametros representativos. Las trazas estacionarias y bien '
          'mezcladas confirman visualmente la convergencia de las cadenas.','Caption'),
    ]))
    story.append(PageBreak())
    story += [P('<b>Coeficientes bayesianos e interpretaciones</b>','H3'), sp(1)]
    story.append(P(
        'Las variables continuas estan estandarizadas (z-score): el coeficiente betaj '
        'representa el cambio esperado en Credit_Score por 1 desviacion estandar en Xj, '
        'manteniendo el resto constante. Los coeficientes de empleo representan la '
        'diferencia respecto a los empleados formales (referencia). '
        '&#10003; indica IC al 95% separado del cero (efecto significativo).'))
    coef_data = [
        [P('Parametro','TH'), P('Media post.','TH'), P('Std','TH'),
         P('IC 95% inf.','TH'), P('IC 95% sup.','TH'), P('R&#770;','TH'), P('Sig.','TH')],
        [P('Intercepto (beta0)'),             P('705.65'), P('0.91'), P('703.87'), P('707.46'), P('1.001'), P('-')],
        [P('Ingreso anual (std)'),             P('+1.32'),  P('0.92'), P('-0.51'),  P('+3.16'),  P('1.000'), P('-')],
        [P('Edad (std)'),                      P('+0.18'),  P('0.56'), P('-0.91'),  P('+1.27'),  P('1.000'), P('-')],
        [P('Prestamos BNPL activos (std)'),    P('+0.80'),  P('0.56'), P('-0.31'),  P('+1.92'),  P('1.000'), P('-')],
        [P('Val. prom. transaccion (std)'),    P('-0.30'),  P('0.57'), P('-1.41'),  P('+0.81'),  P('1.001'), P('-')],
        [P('<b>Pago tardio (Si=1)</b>'),   P('<b>-43.41</b>'), P('1.36'),
         P('<b>-46.18</b>'), P('<b>-40.80</b>'), P('1.000'), P('<b>&#10003;</b>')],
        [P('<b>Empleo: Student</b>'),      P('<b>-88.62</b>'),  P('2.32'),
         P('<b>-93.07</b>'), P('<b>-84.06</b>'), P('1.001'), P('<b>&#10003;</b>')],
        [P('<b>Empleo: Freelancer</b>'),   P('<b>-47.15</b>'),  P('1.70'),
         P('<b>-50.50</b>'), P('<b>-43.80</b>'), P('1.000'), P('<b>&#10003;</b>')],
        [P('<b>Empleo: Unemployed</b>'),   P('<b>-133.92</b>'), P('3.28'),
         P('<b>-140.42</b>'),P('<b>-127.35</b>'),P('1.001'), P('<b>&#10003;</b>')],
        [P('sigma residual'),              P('55.04'),  P('0.41'), P('54.23'),  P('55.84'),  P('1.000'), P('-')],
    ]
    t_coef = Table(coef_data, colWidths=[52*mm,20*mm,14*mm,20*mm,20*mm,14*mm,14*mm])
    ts_coef = ts_base()
    for r in [7,8,9,10]: ts_coef.add('BACKGROUND',(0,r),(-1,r),RED_LT)
    t_coef.setStyle(ts_coef)
    story.append(KeepTogether([t_coef,
        P('Tabla 8. Resumen posterior de los coeficientes. Referencia: Employed, sin pago tardio. '
          'Variables continuas estandarizadas (z-score). &#10003; = IC 95% no incluye el cero.','Caption')]))
    story.append(sp(3))
    story.append(P(
        '<b>Hallazgo central:</b> las cuatro variables continuas (ingreso, edad, prestamos, '
        'valor de transacciones) tienen IC al 95% que incluyen el cero: condicionalmente al '
        'tipo de empleo, no hay evidencia bayesiana de efecto directo sobre el Credit_Score. '
        'El efecto del ingreso parece estar mediado por el tipo de empleo: al controlar el '
        'estado laboral, el ingreso adicional no aporta informacion incremental significativa.'))
    story.append(sp(2))
    story.append(P('En contraste, las variables categoricas muestran efectos masivos:'))
    for txt in [
        '<b>Desempleo (Unemployed):</b> reduce el Credit_Score en <b>133.9 puntos</b> '
        '(IC 95%: [-140.4, -127.4]). El efecto mas grande del modelo. Un consumidor '
        'desempleado con identico perfil financiero que uno empleado tendra 134 puntos '
        'menos, lo que puede excluirlo del acceso a credito formal.',
        '<b>Ser estudiante (Student):</b> reduce el Credit_Score en <b>88.6 puntos</b> '
        '(IC 95%: [-93.1, -84.1]). Refleja historiales crediticios mas cortos y '
        'mayores limitaciones de ingreso de este grupo demografico.',
        '<b>Trabajo independiente (Freelancer):</b> reduce el Credit_Score en '
        '<b>47.2 puntos</b> (IC 95%: [-50.5, -43.8]). Efecto intermedio, consistente '
        'con mayor variabilidad de ingresos del trabajo autonomo.',
        '<b>Historial de pagos tardios:</b> reduce el Credit_Score en <b>43.4 puntos</b> '
        '(IC 95%: [-46.2, -40.8]). Efecto directo e independiente del tipo de empleo: '
        'tener pagos tardios reduce el puntaje en ~43 puntos adicionales sin importar '
        'la situacion laboral.',
    ]:
        story.append(bul(txt))
    story.append(sp(2))
    story.append(KeepTogether([
        img('fig9_forest_plot_coeficientes.png', CW, CW*0.47),
        P('Figura 8. Forest plot bayesiano: media posterior, IQR (50%) e IC 95%. '
          'Rojo: IC 95% separado del cero (efectos significativos). '
          'Las variables continuas no son significativas al controlar por tipo de empleo.','Caption'),
    ]))
    story.append(sp(3))
    story += [P('<b>Verificacion predictiva posterior (PPC)</b>','H3'), sp(1)]
    story.append(P(
        'La PPC evalua si el modelo genera datos simulados coherentes con los observados. '
        'La Figura 9 muestra que la distribucion de replicas (y_rep) reproduce fielmente '
        'la distribucion observada (y_obs) en forma y rango, confirmando que el modelo '
        'captura adecuadamente la estructura de los datos y que sus predicciones son confiables.'))
    story.append(KeepTogether([
        img('fig10_posterior_predictive.png', CW*0.78, CW*0.43),
        P('Figura 9. Verificacion predictiva posterior. Las replicas simuladas (azul) '
          'reproducen bien la distribucion observada del Credit_Score (negro).','Caption'),
    ]))
    story.append(sp(3))
    story += [P('<b>Predicciones para perfiles representativos</b>','H3'), sp(1)]
    story.append(P(
        'La Tabla 9 muestra predicciones del Credit_Score para tres perfiles hipoteticos. '
        'La diferencia entre el perfil mas y menos favorable asciende a <b>179 puntos</b>, '
        'con consecuencias directas sobre el acceso al credito formal.'))
    pred_data = [
        [P('Perfil','TH'), P('Caracteristicas','TH'),
         P('Credit_Score pred.','TH'), P('IC 95%','TH')],
        [P('Empleado estandar'),
         P('Income=$75k, Edad=35, sin pago tardio'), P('<b>706</b>'), P('[599, 814]')],
        [P('Estudiante tipico'),
         P('Income=$12k, Edad=22, sin pago tardio'), P('615'), P('[508, 724]')],
        [P('<b>Desempleado c/ pagos tardios</b>'),
         P('Income=$15k, Edad=27, con pago tardio'), P('<b>527</b>'), P('[420, 638]')],
    ]
    t_pred = Table(pred_data, colWidths=[40*mm, 76*mm, 30*mm, 26*mm])
    ts_pred = ts_base()
    ts_pred.add('BACKGROUND',(0,1),(-1,1),GREEN_LT); ts_pred.add('BACKGROUND',(0,3),(-1,3),RED_LT)
    t_pred.setStyle(ts_pred)
    story.append(KeepTogether([t_pred,
        P('Tabla 9. Predicciones bayesianas para perfiles representativos. '
          'IC al 95% incluye la incertidumbre del modelo (sigma aprox. 55 pts).','Caption')]))
    story.append(PageBreak())

    # 4.3 Beta-Binomial
    story += sec2('4.3 Modelo 3 - Beta-Binomial: tasa de pagos tardios por estado laboral')
    story += [P('<b>Objetivo</b>','H3'), sp(1)]
    story.append(P(
        'Estimar la distribucion posterior de la proporcion de pagos tardios (pi_k) para '
        'cada grupo de Employment_Status y calcular la probabilidad bayesiana de que '
        'ciertos grupos tengan tasas significativamente superiores. '
        'Este modelo cierra la cadena causal: si el desempleo reduce el Credit_Score '
        '(Modelo 2), el Modelo 3 explica el mecanismo - los desempleados tienen '
        'historiales de pago mucho mas deteriorados.'))
    story += [sp(3), P('<b>Especificacion y metodo</b>','H3'), sp(1)]
    spec_bb = [
        [P('Componente','TH'), P('Distribucion','TH'), P('Justificacion','TH')],
        [P('Verosimilitud'), P('X_k | pi_k ~ Binomial(n_k, pi_k)'),
         P('X_k = pagos tardios en el grupo k; n_k = tamanio del grupo')],
        [P('Prior'), P('pi_k ~ Beta(1, 1) = Uniforme(0,1)'),
         P('Prior no informativo: todos los valores de la tasa son igualmente plausibles')],
        [P('Posterior (analitico)'), P('pi_k | datos ~ Beta(1+X_k, 1+n_k-X_k)'),
         P('Solucion conjugada exacta; la Beta es el prior conjugado de la Binomial')],
    ]
    t_bb = Table(spec_bb, colWidths=[30*mm, 68*mm, CW-98*mm])
    t_bb.setStyle(ts_base())
    story.append(KeepTogether([t_bb,
        P('Tabla 10. Especificacion del modelo Beta-Binomial. '
          'La conjugacion permite solucion analitica exacta.','Caption')]))
    story.append(sp(3))
    story.append(P(
        'El modelo Beta-Binomial admite solucion analitica exacta: la posterior de '
        'cada grupo es Beta(1+X_k, 1+n_k-X_k). Las probabilidades de superioridad '
        'entre grupos se calculan mediante <b>simulacion Monte Carlo</b>: se generan '
        '100 000 muestras de cada posterior Beta y se estima la proporcion de casos '
        'en que la muestra del grupo de mayor riesgo supera a la del menor. '
        'Este Monte Carlo actua como verificacion numerica de una comparacion ya '
        'evidente dado el escaso solapamiento de las distribuciones posteriores.'))
    story += [sp(4), P('<b>Resultados</b>','H3'), sp(1)]
    bb_res = [
        [P('Grupo','TH'), P('n','TH'), P('Pag. tard.','TH'),
         P('pi obs.','TH'), P('pi post. (media)','TH'), P('IC 95% inf.','TH'), P('IC 95% sup.','TH')],
        [P('<b>Employed</b>'),  P('6 029'), P('902'), P('15.0%'), P('<b>14.97%</b>'), P('14.1%'), P('15.9%')],
        [P('Freelancer'),       P('1 495'), P('395'), P('26.4%'), P('<b>26.45%</b>'), P('24.3%'), P('28.7%')],
        [P('Student'),          P('1 968'), P('869'), P('44.2%'), P('<b>44.16%</b>'), P('42.0%'), P('46.4%')],
        [P('<b>Unemployed</b>'),P('508'),   P('310'), P('61.0%'), P('<b>60.98%</b>'), P('56.7%'), P('65.2%')],
    ]
    t_bbr = Table(bb_res, colWidths=[28*mm,18*mm,22*mm,18*mm,30*mm,22*mm,22*mm])
    ts_bbr = ts_base()
    ts_bbr.add('BACKGROUND',(0,1),(-1,1),GREEN_LT); ts_bbr.add('BACKGROUND',(0,4),(-1,4),RED_LT)
    t_bbr.setStyle(ts_bbr)
    story.append(KeepTogether([t_bbr,
        P('Tabla 11. Distribuciones posteriores de pi_k. Con prior uniforme Beta(1,1), '
          'la media posterior coincide practicamente con la proporcion observada.','Caption')]))
    story.append(sp(3))
    story.append(P(
        'Los resultados revelan diferencias marcadas y bien separadas. Los '
        '<b>desempleados</b> presentan una tasa de pagos tardios del <b>61%</b>, '
        'cuatro veces superior a la de los empleados formales (15%). '
        'Estudiantes (44%) e independientes (27%) ocupan posiciones intermedias, '
        'reflejando la mayor precariedad de sus situaciones laborales. '
        'Las distribuciones posteriores son muy estrechas para los Employed (n=6 029), '
        'indicando alta precision; para los Unemployed (n=508) son algo mas amplias '
        'pero siguen sin solaparse con las de los Employed.'))
    story.append(sp(2))
    story.append(KeepTogether([
        img('fig11_beta_posteriors.png', CW, CW*0.47),
        P('Figura 10. Distribuciones posteriores Beta(1+X_k, 1+n_k-X_k). '
          'Las distribuciones de Employed y Unemployed no se solapan en absoluto, '
          'confirmando con certeza bayesiana la diferencia entre grupos.','Caption'),
    ]))
    story.append(sp(2))
    story.append(KeepTogether([
        img('fig12_comparaciones_proporciones.png', CW*0.82, CW*0.47),
        P('Figura 11. Distribuciones posteriores de las diferencias pi_k - pi_Employed. '
          'Toda la masa de probabilidad esta en valores positivos para los tres grupos.','Caption'),
    ]))
    story.append(sp(2))
    story.append(callout('Resultado principal - Modelo Beta-Binomial', [
        'P(pi_Unemployed &gt; pi_Employed | datos) = <b>1.0000</b>  |  '
        'Diferencia: +0.460, IC 95%: [0.417, 0.503]',
        'P(pi_Student &gt; pi_Employed | datos) = <b>1.0000</b>  |  '
        'Diferencia: +0.292, IC 95%: [0.268, 0.316]',
        'P(pi_Freelancer &gt; pi_Employed | datos) = <b>1.0000</b>  |  '
        'Diferencia: +0.115, IC 95%: [0.093, 0.137]',
        '',
        'Los tres grupos no-Employed tienen tasas de pagos tardios significativamente '
        'superiores con certeza bayesiana total. Este resultado cierra la cadena causal: '
        'el estado laboral determina la frecuencia de pagos tardios, que deteriora el '
        'historial crediticio, reduce el Credit_Score y eleva el riesgo de incumplimiento.',
    ], bg=AMBER_LT, bd=AMBER_BD, stripe=AMBER))
    story.append(PageBreak())

    # 5. ETICA
    story += sec1('5. Analisis Etico e Impacto Social')
    story.append(P(
        'El uso de modelos estadisticos en decisiones crediticias plantea dilemas eticos '
        'que van mas alla de la validez tecnica. Los modelos desarrollados identifican '
        'variables de alta capacidad predictiva - especialmente el estado laboral - pero '
        'su aplicacion en sistemas de decision automatizada conlleva riesgos que '
        'merecen examen explicito.'))
    story += [sp(4), P('Discriminacion estadistica y equidad algoritmica','H3'), sp(1)]
    story.append(P(
        'El modelo asigna un Credit_Score predicho 134 puntos inferior a los desempleados '
        'y 89 puntos inferior a los estudiantes respecto a los empleados formales. '
        'Desde la perspectiva estadistica, este resultado es valido. Desde la perspectiva '
        'de la equidad, implica que consumidores son penalizados por caracteristicas '
        'temporales (el desempleo o el ser estudiante son fases de vida) o que reflejan '
        'desigualdades estructurales previas (barreras de acceso al empleo formal).'))
    story += [sp(3), P('Analisis de escenarios','H3'), sp(1)]
    for txt in [
        '<b>Corto plazo:</b> Si este modelo se usa para decisiones automaticas de '
        'aprobacion BNPL, los desempleados y estudiantes enfrentaran condiciones '
        'mas restrictivas, agravando la exclusion financiera del segmento que '
        'mas podria beneficiarse del acceso razonable al credito.',
        '<b>Mediano plazo:</b> Normalizar modelos de scoring en BNPL puede aumentar '
        'la eficiencia del mercado (reduciendo morosidad), pero a costa de reducir '
        'la inclusion financiera. Este equilibrio es una decision regulatoria.',
        '<b>Largo plazo:</b> Si los modelos se entrenan con datos que reflejan '
        'discriminacion historica, la reproduciran de forma auto-perpetuante, '
        'creando ciclos de exclusion dificiles de romper sin intervencion deliberada.',
    ]:
        story.append(bul(txt))
    story.append(sp(4))
    story.append(callout('Dilema etico central', [
        'Tiene una institucion el derecho de utilizar el tipo de empleo como factor '
        'determinante en un modelo de riesgo crediticio automatizado?',
        '',
        'Desde la eficiencia del mercado: si. Estas variables tienen poder predictivo '
        'estadisticamente respaldado y reducen la morosidad. Desde la equidad: es '
        'cuestionable. Las personas no deberian ser excluidas de servicios financieros '
        'por caracteristicas temporales o que reflejan desigualdades estructurales. '
        'Los reguladores y equipos de etica en IA deben determinar que variables son '
        'admisibles en sistemas de decision automatizada.',
    ], bg=AMBER_LT, bd=AMBER_BD, stripe=AMBER))
    story.append(PageBreak())

    # 6. CONCLUSIONES
    story += sec1('6. Conclusiones')
    story.append(callout('Cadena causal integrada - validada por los tres modelos', [
        'Estado laboral -> comportamiento de pago -> historial crediticio -> '
        'Credit_Score -> riesgo de incumplimiento BNPL.',
    ], bg=GREEN_LT, bd=GREEN, stripe=GREEN))
    story.append(sp(4))
    for txt in [
        '<b>Conclusion 1 - Diferencia entre grupos confirmada:</b> '
        'Los consumidores de alto riesgo tienen Credit_Score promedio 109 puntos inferior '
        'al de los de bajo riesgo (IC 95%: [102, 116], P posterior=1.000000). '
        'Esta brecha equivale a la transicion entre categorias crediticias con impacto '
        'directo sobre tasas de interes y acceso al credito.',
        '<b>Conclusion 2 - El estado laboral domina la prediccion:</b> '
        'El modelo MCMC-NUTS (R-hat max=1.0013, ESS min=2 675, 0 divergencias) demuestra '
        'que ser desempleado reduce el Credit_Score en 134 puntos y tener historial de '
        'pagos tardios lo reduce en 43 puntos adicionales, ambos con IC al 95% separados '
        'del cero. Las variables continuas no son significativas al controlar por empleo.',
        '<b>Conclusion 3 - El desempleo cuadruplica el riesgo de pago tardio:</b> '
        'El modelo Beta-Binomial (conjugado analitico) confirma con P=1.0000 que los '
        'desempleados tienen tasa de pagos tardios (61%) cuatro veces mayor que los '
        'empleados (15%). Esto explica mecanicamente el efecto dominante del Modelo 2.',
        '<b>Conclusion 4 - Limitaciones:</b> Dataset sintetico sin contexto geografico '
        'limita la generalizacion. Se recomienda validacion sobre datos observacionales '
        'reales. La posible circularidad entre Credit_Score y Default_Risk en el dataset '
        'podria inflar las correlaciones observadas.',
        '<b>Lineas de investigacion futura:</b> Modelos jerarquicos bayesianos con '
        'variacion geografica; clasificacion bayesiana directa sobre Default_Risk; '
        'analisis de equidad (fairness) con metricas de igualdad de oportunidades; '
        'comparacion con modelos frecuentistas equivalentes.',
    ]:
        story.append(bul(txt))
    story.append(PageBreak())

    # 7. REFERENCIAS
    story += sec1('7. Referencias')
    for i, ref in enumerate([
        'Dobbie, W., &amp; Song, J. (2015). Debt relief and debtor outcomes. '
        '<i>American Economic Review, 105</i>(3), 1272-1311. https://doi.org/10.1257/aer.20130612',
        'Gathergood, J., Mahoney, N., Stewart, N., &amp; Weber, J. (2019). '
        'How do individuals repay their debt? '
        '<i>American Economic Review, 109</i>(3), 844-875.',
        'Gelman, A., Carlin, J. B., Stern, H. S., Dunson, D. B., Vehtari, A., &amp; '
        'Rubin, D. B. (2013). <i>Bayesian Data Analysis</i> (3a ed.). Chapman and Hall/CRC.',
        'Hoffman, M. D., &amp; Gelman, A. (2014). The No-U-Turn Sampler. '
        '<i>JMLR, 15</i>(1), 1593-1623.',
        'PyMC Development Team. (2023). <i>PyMC: Probabilistic programming in Python</i> (v5). '
        'https://www.pymc.io',
        'Salvatier, J., Wiecki, T. V., &amp; Fonnesbeck, C. (2016). '
        'Probabilistic programming in Python using PyMC3. '
        '<i>PeerJ Computer Science, 2</i>, e55.',
        'Vehtari, A., Gelman, A., Simpson, D., Carpenter, B., &amp; Burkner, P.-C. (2021). '
        'Rank-normalization, folding, and localization: An improved R-hat. '
        '<i>Bayesian Analysis, 16</i>(2), 667-718.',
    ], 1):
        story.append(P(f'{i}. {ref}', 'BodySm'))
        story.append(sp(2))

    doc.build(story, onFirstPage=on_first_page, onLaterPages=on_later_pages)
    sz = os.path.getsize(out)/1024
    print(f'  informe_BNPL.pdf  ->  {sz:.0f} KB')
    return out


# =============================================================================
# POSTER A1
# =============================================================================
def build_poster():
    """Poster academico en UNA SOLA pagina A1 apaisado — dibujado directo en canvas."""
    from reportlab.pdfgen.canvas import Canvas
    out = os.path.join(ENTREGABLES, 'poster_BNPL.pdf')
    PW, PH = landscape(A1)          # 841.9 x 594.9 mm aprox en pts: 2383.9 x 1683.8
    PAD = 14*mm

    canv = Canvas(out, pagesize=landscape(A1))
    canv.setTitle('Poster - Inferencia Bayesiana sobre Riesgo BNPL')

    # ── Helpers ──
    def box(x, y, w, h, fill_color=white, stroke_color=BORDER, rnd=3, lw=0.4):
        canv.setFillColor(fill_color); canv.setStrokeColor(stroke_color)
        canv.setLineWidth(lw)
        canv.roundRect(x, y, w, h, rnd, fill=1, stroke=1)

    def stripe_box(x, y, w, h, fill_color, stripe_color, rnd=3):
        box(x, y, w, h, fill_color, HexColor('#d1d5db'), rnd)
        canv.setFillColor(stripe_color)
        canv.roundRect(x, y, 3.5*mm, h, 2, fill=1, stroke=0)

    def txt(text, x, y, font='Helvetica', size=8, color=HexColor('#1e293b')):
        canv.setFillColor(color); canv.setFont(font, size)
        canv.drawString(x, y, text)

    def ctxt(text, cx, y, font='Helvetica', size=8, color=HexColor('#1e293b')):
        canv.setFillColor(color); canv.setFont(font, size)
        canv.drawCentredString(cx, y, text)

    def para(lines, x, y, font='Helvetica', size=8, color=HexColor('#1e293b'),
             leading=None, max_w=None):
        """Draw list of strings as stacked lines. Returns new y."""
        if leading is None: leading = size * 1.35
        canv.setFillColor(color); canv.setFont(font, size)
        for line in lines:
            canv.drawString(x, y, line)
            y -= leading
        return y

    def sec_hdr(text, x, y, w, color=NAVY):
        """Section header bar. Returns new y below bar."""
        hh = 7*mm
        canv.setFillColor(color); canv.setStrokeColor(color)
        canv.setLineWidth(0)
        canv.roundRect(x, y-hh+1*mm, w, hh, 2, fill=1, stroke=0)
        canv.setFillColor(white); canv.setFont('Helvetica-Bold', 9)
        canv.drawString(x+4*mm, y-hh+3.5*mm, text)
        return y - hh - 2*mm

    def kpi(x, y, value, label, w=32*mm, h=18*mm, vc=BLUE, lc=GRAY):
        box(x, y, w, h, GRAY_LT, BORDER, 3)
        ctxt(value, x+w/2, y+h-8*mm, 'Helvetica-Bold', 13, vc)
        ctxt(label, x+w/2, y+2*mm, 'Helvetica', 7, lc)

    def result_box(x, y, w, h, lines, bg, stripe):
        stripe_box(x, y, w, h, bg, stripe, 3)
        cy = y + h - 7*mm
        canv.setFont('Helvetica', 7.5); canv.setFillColor(HexColor('#1e293b'))
        for line in lines:
            canv.drawString(x+5*mm, cy, line); cy -= 5.5*mm

    # ═══════════════════════════════════════════════
    # HEADER
    # ═══════════════════════════════════════════════
    HDR_H = 38*mm
    canv.setFillColor(NAVY)
    canv.rect(0, PH-HDR_H, PW, HDR_H, fill=1, stroke=0)
    # Accent line
    canv.setStrokeColor(BLUE); canv.setLineWidth(1.5)
    canv.line(0, PH-HDR_H, PW, PH-HDR_H)

    # Institution
    ctxt('ESCUELA SUPERIOR POLITECNICA DEL LITORAL  |  ESPOL  |  Estadistica Bayesiana  |  Termino 1 - 2026',
         PW/2, PH-8*mm, 'Helvetica', 8, HexColor('#94a3b8'))
    # Title
    ctxt('Inferencia Bayesiana sobre el Riesgo de Incumplimiento en Consumidores BNPL',
         PW/2, PH-18*mm, 'Helvetica-Bold', 20, white)
    # Methods
    ctxt('Modelo Normal-Normal  |  Regresion Bayesiana MCMC-NUTS  |  Modelo Beta-Binomial  |  n = 10 000',
         PW/2, PH-26*mm, 'Helvetica', 9, HexColor('#93c5fd'))
    # Authors
    ctxt('Levi Parrales  |  Jose Villegas  |  Alessandro Paredes  |  Diego Benitez',
         PW/2, PH-33*mm, 'Helvetica', 8.5, HexColor('#cbd5e1'))

    # ═══════════════════════════════════════════════
    # LAYOUT: 4 columnas
    # ═══════════════════════════════════════════════
    BODY_TOP = PH - HDR_H - PAD
    BODY_BOT = 10*mm
    BODY_H   = BODY_TOP - BODY_BOT
    NCOLS    = 4
    GAP      = 6*mm
    AVAIL_W  = PW - 2*PAD
    COL_W    = (AVAIL_W - (NCOLS-1)*GAP) / NCOLS
    xs = [PAD + i*(COL_W+GAP) for i in range(NCOLS)]

    # ──────────────────────────────────────────────
    # COLUMNA 1 — Introduccion + Datos
    # ──────────────────────────────────────────────
    x1 = xs[0]; cy = BODY_TOP

    cy = sec_hdr('CONTEXTO Y PREGUNTA DE INVESTIGACION', x1, cy, COL_W, NAVY)
    box(x1, cy-24*mm, COL_W, 24*mm, BLUE_LT, BLUE_MID, 3)
    para([
        'El sector BNPL (Buy Now, Pay Later) ha crecido',
        'exponencialmente. Servicios como Klarna, Afterpay',
        'y Affirm permiten compras a plazo sin reportar a',
        'agencias crediticias tradicionales, generando riesgo',
        'de acumulacion silenciosa de deuda.',
    ], x1+4*mm, cy-6*mm, size=7.5)
    cy -= 26*mm

    box(x1, cy-17*mm, COL_W, 17*mm, AMBER_LT, AMBER_BD, 3)
    canv.setFillColor(AMBER); canv.setFont('Helvetica-Bold', 7.5)
    canv.drawString(x1+4*mm, cy-5.5*mm, 'Pregunta de investigacion:')
    para([
        'Que factores demograficos, laborales y conductuales',
        'predicen el Credit_Score de los usuarios BNPL',
        'y como difiere entre grupos de riesgo y empleo?',
    ], x1+4*mm, cy-11*mm, size=7.5, color=HexColor('#92400e'))
    cy -= 19*mm

    cy = sec_hdr('DATOS Y VARIABLE PRINCIPAL', x1, cy, COL_W, NAVY)
    # KPIs en 2x2
    kw = (COL_W - 3*mm)/2
    kpi(x1,           cy-18*mm, '10 000', 'Consumidores',  kw, 16*mm)
    kpi(x1+kw+3*mm,   cy-18*mm, '11',     'Variables',     kw, 16*mm)
    kpi(x1,           cy-36*mm, '663.7',  'Media Credit Score', kw, 16*mm)
    kpi(x1+kw+3*mm,   cy-36*mm, '88.0%',  'Bajo Riesgo',   kw, 16*mm)
    cy -= 39*mm

    box(x1, cy-20*mm, COL_W, 20*mm, BLUE_LT, BORDER, 3)
    canv.setFillColor(NAVY); canv.setFont('Helvetica-Bold', 8)
    canv.drawString(x1+4*mm, cy-6*mm, 'Variable principal: Credit_Score')
    para([
        '&#8226; Rango: 300-850  |  Media: 663.7  |  Std: 76.2',
        '&#8226; Distribucion aprox. normal (sesgo = -0.66)',
        '&#8226; Correlacion con Default_Risk: r = -0.41',
    ], x1+4*mm, cy-11*mm, size=7.5)
    cy -= 22*mm

    cy = sec_hdr('CADENA CAUSAL INTEGRADA', x1, cy, COL_W, HexColor('#065f46'))
    box(x1, cy-22*mm, COL_W, 22*mm, GREEN_LT, GREEN, 3, lw=0.8)
    ctxt('Estado laboral', x1+COL_W*0.12, cy-9*mm, 'Helvetica-Bold', 8, NAVY)
    ctxt('>', x1+COL_W*0.28, cy-9*mm, 'Helvetica-Bold', 10, GRAY)
    ctxt('Pagos tardios', x1+COL_W*0.44, cy-9*mm, 'Helvetica-Bold', 8, NAVY)
    ctxt('>', x1+COL_W*0.60, cy-9*mm, 'Helvetica-Bold', 10, GRAY)
    ctxt('Credit_Score', x1+COL_W*0.72, cy-9*mm, 'Helvetica-Bold', 8, NAVY)
    ctxt('Modelo 1: Credit Score por grupo de riesgo', x1+COL_W/2, cy-14*mm, 'Helvetica', 7, GRAY)
    ctxt('Modelo 2: Regresion MCMC-NUTS (predictores)', x1+COL_W/2, cy-18*mm, 'Helvetica', 7, GRAY)
    ctxt('Modelo 3: Tasa de pagos tardios por empleo', x1+COL_W/2, cy-22*mm, 'Helvetica', 7, GRAY)

    # ──────────────────────────────────────────────
    # COLUMNA 2 — Modelo 1 Normal-Normal
    # ──────────────────────────────────────────────
    x2 = xs[1]; cy = BODY_TOP

    cy = sec_hdr('MODELO 1 — NORMAL-NORMAL (Conjugado)', x2, cy, COL_W, HexColor('#1e40af'))
    box(x2, cy-20*mm, COL_W, 20*mm, BLUE_LT, BLUE_MID, 3)
    para([
        'Verosimilitud: Y_i | mu_k ~ Normal(mu_k, sigma_k^2)',
        'Prior:  mu_k ~ Normal(650, 100^2)  — debilmente informativo',
        'Posterior: mu_k | datos ~ Normal(mun, taun^2)',
        'Metodo: Solucion analitica exacta (conjugado)',
    ], x2+4*mm, cy-5.5*mm, size=7.5)
    cy -= 22*mm

    # Tabla resultados
    box(x2, cy-22*mm, COL_W, 22*mm, GRAY_LT, BORDER, 2)
    canv.setFillColor(NAVY); canv.setFont('Helvetica-Bold', 7.5)
    cols_nn = [x2+3*mm, x2+COL_W*0.38, x2+COL_W*0.62]
    canv.drawString(cols_nn[0], cy-5.5*mm, 'Grupo')
    canv.drawString(cols_nn[1], cy-5.5*mm, 'mu_n posterior')
    canv.drawString(cols_nn[2], cy-5.5*mm, 'IC 95%')
    canv.setStrokeColor(BORDER); canv.setLineWidth(0.3)
    canv.line(x2+2*mm, cy-7*mm, x2+COL_W-2*mm, cy-7*mm)
    rows_nn = [
        ('Low (bajo riesgo)',  '675.3 pts', '[673.9, 676.8]'),
        ('Medium',            '587.4 pts', '[581.0, 593.8]'),
        ('High (alto riesgo)','566.3 pts', '[559.4, 573.3]'),
    ]
    colors_nn = [GREEN_LT, GRAY_LT, RED_LT]
    ry = cy-13*mm
    for (grp, mu, ic), bg in zip(rows_nn, colors_nn):
        canv.setFillColor(bg)
        canv.rect(x2+2*mm, ry-1*mm, COL_W-4*mm, 4.5*mm, fill=1, stroke=0)
        canv.setFillColor(HexColor('#1e293b')); canv.setFont('Helvetica', 7)
        canv.drawString(cols_nn[0], ry+2.5*mm, grp)
        canv.drawString(cols_nn[1], ry+2.5*mm, mu)
        canv.drawString(cols_nn[2], ry+2.5*mm, ic)
        ry -= 4.5*mm
    cy -= 24*mm

    # Figura
    fig1_h = COL_W * 0.50
    fig1_path = os.path.join(FIGURAS, 'fig6_normal_normal_posteriors.png')
    if os.path.exists(fig1_path):
        canv.drawImage(fig1_path, x2, cy-fig1_h, COL_W, fig1_h, preserveAspectRatio=True, mask='auto')
    else:
        box(x2, cy-fig1_h, COL_W, fig1_h, GRAY_LT, BORDER)
    canv.setFillColor(GRAY); canv.setFont('Helvetica-Oblique', 7)
    canv.drawCentredString(x2+COL_W/2, cy-fig1_h-4*mm,
        'Distribuciones posteriores de mu_k por grupo')
    cy -= fig1_h + 7*mm

    # Resultado destacado
    result_box(x2, cy-26*mm, COL_W, 26*mm, [
        'E[mu_Low - mu_High | datos] = 108.99 pts',
        'IC 95%: [101.95, 116.03]',
        'P(mu_High < mu_Low | datos) = 1.000000',
        '',
        'Certeza bayesiana total: el grupo de bajo',
        'riesgo supera al de alto riesgo en > 100 pts.',
        'Diferencia equivale a cambio de categoria FICO.',
    ], GREEN_LT, GREEN)
    cy -= 28*mm

    # Figura diferencia
    fig2_h = COL_W * 0.44
    fig2_path = os.path.join(FIGURAS, 'fig7_comparacion_grupos.png')
    if os.path.exists(fig2_path):
        canv.drawImage(fig2_path, x2, cy-fig2_h, COL_W, fig2_h, preserveAspectRatio=True, mask='auto')
    canv.setFillColor(GRAY); canv.setFont('Helvetica-Oblique', 7)
    canv.drawCentredString(x2+COL_W/2, cy-fig2_h-4*mm,
        'Posterior diferencia mu_Low - mu_High')

    # ──────────────────────────────────────────────
    # COLUMNA 3 — Modelo 2 MCMC-NUTS
    # ──────────────────────────────────────────────
    x3 = xs[2]; cy = BODY_TOP

    cy = sec_hdr('MODELO 2 — REGRESION BAYESIANA MCMC-NUTS', x3, cy, COL_W, HexColor('#1e40af'))
    box(x3, cy-18*mm, COL_W, 18*mm, GREEN_LT, GREEN, 3, lw=0.6)
    para([
        'Algoritmo: No-U-Turn Sampler (NUTS)  via PyMC v5',
        'Config.: 4 cadenas × 1 000 draw + 1 000 tune = 4 000 muestras',
        'R-hat max: 1.0013  |  ESS bulk min: 2 675  |  Divergencias: 0',
        'Todos los criterios de convergencia satisfechos',
    ], x3+4*mm, cy-5.5*mm, size=7.5, color=HexColor('#065f46'))
    cy -= 20*mm

    # Forest plot
    fig3_h = COL_W * 0.52
    fig3_path = os.path.join(FIGURAS, 'fig9_forest_plot_coeficientes.png')
    if os.path.exists(fig3_path):
        canv.drawImage(fig3_path, x3, cy-fig3_h, COL_W, fig3_h, preserveAspectRatio=True, mask='auto')
    else:
        box(x3, cy-fig3_h, COL_W, fig3_h, GRAY_LT, BORDER)
    canv.setFillColor(GRAY); canv.setFont('Helvetica-Oblique', 7)
    canv.drawCentredString(x3+COL_W/2, cy-fig3_h-4*mm,
        'Forest plot bayesiano — coeficientes con IC 95%')
    cy -= fig3_h + 7*mm

    # Tabla coeficientes clave
    box(x3, cy-30*mm, COL_W, 30*mm, GRAY_LT, BORDER, 2)
    canv.setFillColor(NAVY); canv.setFont('Helvetica-Bold', 7.5)
    cc = [x3+3*mm, x3+COL_W*0.46, x3+COL_W*0.68, x3+COL_W*0.87]
    canv.drawString(cc[0], cy-5.5*mm, 'Predictor')
    canv.drawString(cc[1], cy-5.5*mm, 'Beta')
    canv.drawString(cc[2], cy-5.5*mm, 'IC 95%')
    canv.drawString(cc[3], cy-5.5*mm, 'Sig.')
    canv.setStrokeColor(BORDER); canv.setLineWidth(0.3)
    canv.line(x3+2*mm, cy-7*mm, x3+COL_W-2*mm, cy-7*mm)
    coefs = [
        ('Ingreso anual (std)',   '+1.32',  '[-0.5,+3.2]', '-',  GRAY_LT),
        ('Edad (std)',            '+0.18',  '[-0.9,+1.3]', '-',  white),
        ('Pagos tardios (Si=1)', '-43.4',  '[-46.2,-40.8]','v', RED_LT),
        ('Student (vs Employed)','-88.6',  '[-93.1,-84.1]','v', RED_LT),
        ('Freelancer',           '-47.2',  '[-50.5,-43.8]','v', RED_LT),
        ('Unemployed',          '-133.9', '[-140.4,-127.4]','v',RED_LT),
    ]
    ry = cy-12*mm
    for (pr, bt, ic, sg, bg) in coefs:
        canv.setFillColor(bg)
        canv.rect(x3+2*mm, ry-1*mm, COL_W-4*mm, 4*mm, fill=1, stroke=0)
        canv.setFillColor(HexColor('#1e293b')); canv.setFont('Helvetica', 6.5)
        canv.drawString(cc[0], ry+2*mm, pr)
        canv.drawString(cc[1], ry+2*mm, bt)
        canv.drawString(cc[2], ry+2*mm, ic)
        fc = RED if sg == 'v' else GRAY
        canv.setFillColor(fc); canv.setFont('Helvetica-Bold', 7)
        canv.drawString(cc[3], ry+2*mm, '&#10003;' if sg == 'v' else '-')
        ry -= 4*mm
    cy -= 32*mm

    result_box(x3, cy-22*mm, COL_W, 22*mm, [
        'Unemployed: -133.9 pts  (IC: [-140.4, -127.4])',
        'Student:     -88.6 pts  (IC: [-93.1, -84.1])',
        'Freelancer:  -47.2 pts  (IC: [-50.5, -43.8])',
        'Pago tardio: -43.4 pts  (IC: [-46.2, -40.8])',
        '',
        'Variables continuas (ingreso, edad, prestamos):',
        'IC al 95% incluye el cero — NO significativas.',
    ], AMBER_LT, AMBER)
    cy -= 24*mm

    fig4_h = COL_W * 0.40
    fig4_path = os.path.join(FIGURAS, 'fig10_posterior_predictive.png')
    if os.path.exists(fig4_path):
        canv.drawImage(fig4_path, x3, cy-fig4_h, COL_W, fig4_h, preserveAspectRatio=True, mask='auto')
    canv.setFillColor(GRAY); canv.setFont('Helvetica-Oblique', 7)
    canv.drawCentredString(x3+COL_W/2, cy-fig4_h-4*mm,
        'Verificacion predictiva posterior (PPC)')

    # ──────────────────────────────────────────────
    # COLUMNA 4 — Modelo 3 Beta-Binomial + Conclusiones
    # ──────────────────────────────────────────────
    x4 = xs[3]; cy = BODY_TOP

    cy = sec_hdr('MODELO 3 — BETA-BINOMIAL (Conjugado)', x4, cy, COL_W, HexColor('#1e40af'))
    box(x4, cy-18*mm, COL_W, 18*mm, BLUE_LT, BLUE_MID, 3)
    para([
        'Verosimilitud: X_k | pi_k ~ Binomial(n_k, pi_k)',
        'Prior: pi_k ~ Beta(1, 1) — no informativo (uniforme)',
        'Posterior: pi_k | datos ~ Beta(1+X_k, 1+n_k-X_k)',
        'Metodo: Solucion analitica exacta (conjugado)',
    ], x4+4*mm, cy-5.5*mm, size=7.5)
    cy -= 20*mm

    # Tabla resultados
    box(x4, cy-24*mm, COL_W, 24*mm, GRAY_LT, BORDER, 2)
    canv.setFillColor(NAVY); canv.setFont('Helvetica-Bold', 7.5)
    cb = [x4+3*mm, x4+COL_W*0.40, x4+COL_W*0.66]
    canv.drawString(cb[0], cy-5.5*mm, 'Grupo')
    canv.drawString(cb[1], cy-5.5*mm, 'pi posterior')
    canv.drawString(cb[2], cy-5.5*mm, 'IC 95%')
    canv.setStrokeColor(BORDER); canv.setLineWidth(0.3)
    canv.line(x4+2*mm, cy-7*mm, x4+COL_W-2*mm, cy-7*mm)
    rows_bb = [
        ('Employed',  '15.0%', '[14.1%, 15.9%]', GREEN_LT),
        ('Freelancer','26.5%', '[24.3%, 28.7%]', GRAY_LT),
        ('Student',   '44.2%', '[42.0%, 46.4%]', AMBER_LT),
        ('Unemployed','61.0%', '[56.7%, 65.2%]', RED_LT),
    ]
    ry = cy-12.5*mm
    for (grp, pi, ic, bg) in rows_bb:
        canv.setFillColor(bg)
        canv.rect(x4+2*mm, ry-1*mm, COL_W-4*mm, 4.5*mm, fill=1, stroke=0)
        canv.setFillColor(HexColor('#1e293b')); canv.setFont('Helvetica', 7)
        canv.drawString(cb[0], ry+2.5*mm, grp)
        canv.drawString(cb[1], ry+2.5*mm, pi)
        canv.drawString(cb[2], ry+2.5*mm, ic)
        ry -= 4.5*mm
    cy -= 26*mm

    # Figura
    fig5_h = COL_W * 0.50
    fig5_path = os.path.join(FIGURAS, 'fig11_beta_posteriors.png')
    if os.path.exists(fig5_path):
        canv.drawImage(fig5_path, x4, cy-fig5_h, COL_W, fig5_h, preserveAspectRatio=True, mask='auto')
    else:
        box(x4, cy-fig5_h, COL_W, fig5_h, GRAY_LT, BORDER)
    canv.setFillColor(GRAY); canv.setFont('Helvetica-Oblique', 7)
    canv.drawCentredString(x4+COL_W/2, cy-fig5_h-4*mm,
        'Distribuciones posteriores Beta por grupo')
    cy -= fig5_h + 7*mm

    result_box(x4, cy-20*mm, COL_W, 20*mm, [
        'P(pi_Unemployed > pi_Employed) = 1.0000',
        'Diferencia: +0.460, IC 95%: [0.417, 0.503]',
        'P(pi_Student > pi_Employed)    = 1.0000',
        'P(pi_Freelancer > pi_Employed) = 1.0000',
        '',
        'Desempleados: tasa de pagos tardios 4x',
        'mayor que empleados formales (61% vs 15%).',
    ], RED_LT, RED)
    cy -= 22*mm

    # CONCLUSIONES
    cy = sec_hdr('CONCLUSIONES PRINCIPALES', x4, cy, COL_W, HexColor('#065f46'))
    box(x4, cy-48*mm, COL_W, 48*mm, GREEN_LT, GREEN, 3, lw=0.8)
    concl = [
        ('1.', 'Diferencia Low-High: 109 pts (P = 1.000000).'),
        ('',   'IC 95%: [101.95, 116.03]'),
        ('2.', 'Unemployed: -133.9 pts en Credit_Score.'),
        ('',   'Freelancer: -47.2 | Student: -88.6 pts'),
        ('3.', 'Pago tardio: -43.4 pts adicionales.'),
        ('4.', 'Desempleados: tasa pago tardio 4x mayor.'),
        ('',   '61% vs 15% en empleados (P = 1.0000)'),
        ('5.', 'Ingreso y edad NO significativos al'),
        ('',   'controlar por tipo de empleo.'),
        ('6.', 'Cadena causal validada con certeza'),
        ('',   'bayesiana en los 3 modelos.'),
    ]
    ry = cy - 5.5*mm
    for (num, txt_) in concl:
        canv.setFillColor(NAVY if num else HexColor('#374151'))
        canv.setFont('Helvetica-Bold' if num else 'Helvetica', 7.5 if num else 7)
        if num:
            canv.drawString(x4+4*mm, ry, num)
        canv.setFillColor(HexColor('#1e293b'))
        canv.setFont('Helvetica', 7.5)
        canv.drawString(x4+10*mm, ry, txt_)
        ry -= 4*mm
    cy -= 50*mm

    # IMPLICACIONES ETICAS (mini)
    cy = sec_hdr('CONSIDERACIONES ETICAS', x4, cy, COL_W, HexColor('#92400e'))
    box(x4, cy-16*mm, COL_W, 16*mm, AMBER_LT, AMBER_BD, 3)
    para([
        'Usar tipo de empleo en scoring puede excluir',
        'poblaciones laboralmente vulnerables. Los sistemas',
        'deben incorporar metricas de equidad (fairness)',
        'junto a la precision predictiva.',
    ], x4+4*mm, cy-5.5*mm, size=7)

    # ═══════════════════════════════════════════════
    # PIE DE PAGINA
    # ═══════════════════════════════════════════════
    canv.setStrokeColor(BORDER); canv.setLineWidth(0.4)
    canv.line(PAD, 8*mm, PW-PAD, 8*mm)
    canv.setFillColor(GRAY); canv.setFont('Helvetica', 7)
    canv.drawString(PAD, 4*mm, 'ESPOL  |  Estadistica Bayesiana  |  Termino 1 - 2026')
    canv.drawRightString(PW-PAD, 4*mm,
        'Parrales  |  Villegas  |  Paredes  |  Benitez')

    canv.showPage()
    canv.save()
    sz = os.path.getsize(out)/1024
    print(f'  poster_BNPL.pdf  ->  {sz:.0f} KB  (1 pagina)')
    return out


# =============================================================================
# DASHBOARD EVIDENCIA
# =============================================================================
# =============================================================================
# DASHBOARD EVIDENCIA
# =============================================================================
def build_dashboard_evidencia():
    out = os.path.join(ENTREGABLES, 'dashboard_evidencia.pdf')
    W, H = A4; ML=MR=22*mm; MT=MB=22*mm; CW=W-ML-MR

    doc = SimpleDocTemplate(out, pagesize=A4,
        leftMargin=ML, rightMargin=MR, topMargin=MT, bottomMargin=MB,
        title='Dashboard Interactivo BNPL - Evidencia Visual')

    def on_first_page(c, doc):
        draw_cover(c, W, H,
            ['Dashboard Interactivo', 'Analisis Bayesiano BNPL'],
            'Evidencia visual de los 5 paneles  |  Streamlit + Plotly + PyMC v5',
            'Levi Parrales | Jose Villegas | Alessandro Paredes | Diego Benitez',
            'Estadistica Bayesiana  |  I Semestre 2026',
            doc_type='EVIDENCIA DEL DASHBOARD INTERACTIVO')

    def on_later_pages(c, doc):
        c.saveState()
        c.setFillColor(GRAY); c.setFont('Helvetica', 7)
        c.drawString(ML, MB-6*mm, 'ESPOL  |  Estadistica Bayesiana  |  Dashboard BNPL')
        c.drawRightString(W-MR, MB-6*mm, f'Pag. {doc.page}')
        c.restoreState()

    def sec1(t): return [sp(4), P(t,'H1'), rule(CW,NAVY,1.5), sp(3)]
    def sec2(t): return [P(t,'H2'), sp(1)]

    story = [PageBreak()]
    story += sec1('Descripcion del Dashboard')
    story.append(P(
        'El dashboard interactivo fue desarrollado en <b>Streamlit</b> con visualizaciones '
        'en <b>Plotly</b> y calculos bayesianos en tiempo real usando NumPy/SciPy. '
        'La aplicacion carga automaticamente el dataset CSV y los coeficientes MCMC '
        'y permite explorar todos los resultados del analisis de forma interactiva. '
        'La navegacion se realiza mediante pestanas (5 paneles tematicos) y la sidebar '
        'lateral con filtros globales que actualizan todas las visualizaciones en tiempo real.'))
    story.append(sp(3))
    story.append(callout('Acceso al dashboard interactivo', [
        'URL: http://localhost:8501',
        'Comando: python -m streamlit run dashboard/app.py --server.port 8501',
        'Prerrequisitos: Streamlit, Plotly, PyMC, ArviZ, Matplotlib, SciPy instalados.',
    ], bg=AMBER_LT, bd=AMBER_BD, stripe=AMBER))
    story.append(sp(4))
    kpi_data = [
        [P('10 000','H1'), P('663.7','H1'), P('88.0%','H1'), P('20.6%','H1')],
        [P('Consumidores','Caption'), P('Credit Score media','Caption'),
         P('Bajo Riesgo','Caption'), P('Pagos Tardios','Caption')],
    ]
    t_kpi = Table(kpi_data, colWidths=[CW/4]*4)
    t_kpi.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),NAVY), ('TEXTCOLOR',(0,0),(-1,0),HexColor('#60a5fa')),
        ('TEXTCOLOR',(0,1),(-1,1),HexColor('#94a3b8')), ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'), ('TOPPADDING',(0,0),(-1,-1),8),
        ('BOTTOMPADDING',(0,0),(-1,-1),8), ('BOX',(0,0),(-1,-1),0.5,BLUE),
        ('INNERGRID',(0,0),(-1,-1),0.3,HexColor('#1e3a6e')),
    ]))
    story.append(KeepTogether([t_kpi,
        P('Panel 1 - Tarjetas KPI con indicadores clave del dataset.','Caption')]))
    story.append(PageBreak())
    story += sec1('Paneles del Dashboard')
    for i, (title, desc, f1, f2) in enumerate([
        ('Panel 1 - Panorama General (KPIs)',
         'Tarjetas KPI: n=10 000, Credit_Score media=663.7, 88% bajo riesgo, 20.6% pagos tardios. '
         'Distribuciones interactivas Plotly del Credit_Score y demas variables con selector. '
         'Graficos de barras para variables categoricas.', None, None),
        ('Panel 2 - Perfil del Consumidor',
         'Filtros interactivos por grupo de riesgo, estado laboral, rango de edad e ingreso. '
         'Los graficos se actualizan en tiempo real mostrando Credit_Score, Income_USD y '
         'Late_Payment para el subgrupo seleccionado.', None, None),
        ('Panel 3 - Analisis Bayesiano Normal-Normal',
         'Permite ajustar mu0 y tau0 del prior interactivamente. Muestra distribuciones '
         'prior, likelihood y posterior superpuestas por grupo de riesgo. '
         'Calcula P(mu_High &lt; mu_Low) en tiempo real.',
         'fig6_normal_normal_posteriors.png', 'fig7_comparacion_grupos.png'),
        ('Panel 4 - Comparacion Beta-Binomial',
         'Distribuciones posteriores Beta por grupo de empleo. '
         'Calcula probabilidades de superioridad via Monte Carlo (100 000 muestras). '
         'P(pi_Unemployed &gt; pi_Employed) = 1.0000.',
         'fig11_beta_posteriors.png', 'fig12_comparaciones_proporciones.png'),
        ('Panel 5 - Regresion MCMC y Predictor Interactivo',
         'Forest plot de coeficientes cargados desde tabla_coeficientes_regresion.csv. '
         'Predictor interactivo: sliders para empleo, ingreso, edad, prestamos, historial. '
         'Calcula Credit_Score predicho con distribucion de incertidumbre.',
         'fig9_forest_plot_coeficientes.png', 'fig10_posterior_predictive.png'),
    ], 1):
        story += sec2(title)
        story.append(P(desc))
        if f1 and f2:
            story.append(sp(2))
            ft = Table([[img(f1,CW*0.475,CW*0.27), img(f2,CW*0.475,CW*0.27)]],
                       colWidths=[CW*0.5, CW*0.5])
            ft.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),
                ('LEFTPADDING',(0,0),(-1,-1),2),('RIGHTPADDING',(0,0),(-1,-1),2)]))
            story.append(ft)
            story.append(P(f'Figuras del Panel {i} - reproduccion de las visualizaciones del analisis.','Caption'))
        story.append(sp(4))
    story.append(PageBreak())
    story += sec1('Verificacion de Funcionalidad')
    verif_data = [
        [P('Funcionalidad','TH'), P('Estado','TH'), P('Detalle','TH')],
        [P('Carga dataset CSV'), P('&#10003; Funcional'), P('10 000 filas, 11 columnas, NA gestionados')],
        [P('Panel 1 - KPIs'), P('&#10003; Funcional'), P('Selector de variable, graficos Plotly')],
        [P('Panel 2 - Filtros'), P('&#10003; Funcional'), P('Filtros en tiempo real: riesgo, empleo, edad, ingreso')],
        [P('Panel 3 - Normal-Normal'), P('&#10003; Funcional'), P('Prior ajustable, distribuciones superpuestas')],
        [P('Panel 4 - Beta-Binomial'), P('&#10003; Funcional'), P('Monte Carlo en tiempo real, diferencias')],
        [P('Panel 5 - MCMC + Predictor'), P('&#10003; Funcional'), P('CSV coeficientes, sliders interactivos')],
        [P('Graficos Plotly'), P('&#10003; Funcional'), P('Hover, zoom, exportacion PNG')],
        [P('Sidebar con filtros'), P('&#10003; Funcional'), P('Afectan todas las secciones del dashboard')],
        [P('Coherencia con informe'), P('&#10003; Verificada'), P('Mismos resultados en informe, poster y dashboard')],
    ]
    t_v = Table(verif_data, colWidths=[58*mm, 30*mm, CW-88*mm])
    ts_v = ts_base(); ts_v.add('BACKGROUND',(1,1),(1,-1),GREEN_LT)
    t_v.setStyle(ts_v)
    story.append(t_v)
    story.append(P('Tabla de verificacion funcional. Todos los paneles han sido validados.','Caption'))

    doc.build(story, onFirstPage=on_first_page, onLaterPages=on_later_pages)
    sz = os.path.getsize(out)/1024
    print(f'  dashboard_evidencia.pdf  ->  {sz:.0f} KB')
    return out


# =============================================================================
# MAIN
# =============================================================================
if __name__ == '__main__':
    print('='*60)
    print('GENERADOR DE PDFs v2 FINAL - PROYECTO BAYESIANO BNPL')
    print('='*60)
    import reportlab
    print(f'ReportLab {reportlab.Version}')

    for fn, label in [
        (build_informe,             'Informe academico'),
        (build_poster,              'Poster A1'),
        (build_dashboard_evidencia, 'Dashboard evidencia'),
    ]:
        print(f'\nGenerando: {label}...')
        try:
            fn()
        except Exception as e:
            import traceback
            print(f'  ERROR: {e}')
            traceback.print_exc()

    print('\n-- Archivos en ENTREGABLES/ --')
    for f in sorted(os.listdir(ENTREGABLES)):
        fp = os.path.join(ENTREGABLES, f)
        if os.path.isfile(fp):
            print(f'  {f:45s}  {os.path.getsize(fp)//1024:6d} KB')
    print('\nCompletado!')
