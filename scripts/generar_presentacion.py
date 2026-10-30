"""
Script oficial de generación de la presentación ejecutiva para el Video Pitch de ELECTRO-VOLT (.pptx).
Estructura, tiempos de rúbrica, guiones cronometrados y diseño visual de maestría.
"""

from pathlib import Path
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# Definición de rutas base
BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_FILE = BASE_DIR / "ELECTRO-VOLT_Pitch_Presentacion.pptx"

# Rutas de figuras e imágenes
IMG_LOGO = BASE_DIR / "src" / "images" / "electrovolt-logotipo.png"
IMG_ISOTIPO = BASE_DIR / "src" / "images" / "electrovolt-isotipo.png"
FIG_DISTRIB_5 = BASE_DIR / "results" / "figures" / "distribucion_5_clases.png"
FIG_MATRIZ_CONF = BASE_DIR / "results" / "figures" / "matriz_confusion.png"
FIG_F1_COMP = BASE_DIR / "results" / "figures" / "f1_comparativa_modelos.png"
FIG_PDP = BASE_DIR / "results" / "figures" / "partial_dependence_plots.png"
FIG_SHAP_GLOBAL = BASE_DIR / "results" / "figures" / "shap_importancia_global.png"
FIG_SHAP_LOCAL = BASE_DIR / "results" / "figures" / "shap_explicacion_local.png"

# Paleta de Colores Corporativa / Ejecutiva
C_NAVY_DARK = RGBColor(11, 30, 54)       # #0B1E36 - Azul Profundo Corporativo
C_BLUE_ACCENT = RGBColor(37, 99, 235)    # #2563EB - Azul Eléctrico Tecnológico
C_CYAN_LIGHT = RGBColor(2, 132, 199)     # #0284C7 - Cian de Acento
C_BG_PAGE = RGBColor(248, 250, 252)      # #F8FAFC - Fondo Blanco Hueso Profesional
C_CARD_BG = RGBColor(255, 255, 255)      # Blanco puro para tarjetas
C_CARD_BG_ALT = RGBColor(241, 245, 249)  # #F1F5F9 - Gris perla suave
C_CARD_BG_BLUE = RGBColor(239, 246, 255) # #EFF6FF - Azul muy tenue
C_BORDER_LIGHT = RGBColor(226, 232, 240) # #E2E8F0 - Borde sutil
C_BORDER_BLUE = RGBColor(147, 197, 253)  # #93C5FD - Borde azul tenue
C_TEXT_DARK = RGBColor(15, 23, 42)       # #0F172A - Texto oscuro de alto contraste
C_TEXT_MUTED = RGBColor(71, 85, 105)     # #475569 - Texto secundario
C_GREEN_SUCCESS = RGBColor(5, 150, 105)  # #059669 - Verde éxito / métricas
C_AMBER_WARN = RGBColor(217, 119, 6)     # #D97706 - Ámbar advertencia


def crear_presentacion():
    prs = pptx.Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # =========================================================================
    # FUNCIONES AUXILIARES DE DISEÑO
    # =========================================================================
    def set_slide_background(slide, color=C_BG_PAGE):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = color
        bg.line.fill.background()
        return bg

    def add_header(slide, badge_text, title_text, subtitle_text=""):
        header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(10.5), Inches(0.95))
        tf = header_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p_badge = tf.paragraphs[0]
        p_badge.text = badge_text.upper()
        p_badge.font.name = "Segoe UI"
        p_badge.font.size = Pt(9.5)
        p_badge.font.bold = True
        p_badge.font.color.rgb = C_BLUE_ACCENT
        p_badge.space_after = Pt(2)

        p_title = tf.add_paragraph()
        p_title.text = title_text
        p_title.font.name = "Segoe UI"
        p_title.font.size = Pt(19)
        p_title.font.bold = True
        p_title.font.color.rgb = C_NAVY_DARK

        if subtitle_text:
            p_sub = tf.add_paragraph()
            p_sub.text = subtitle_text
            p_sub.font.name = "Segoe UI"
            p_sub.font.size = Pt(10.5)
            p_sub.font.color.rgb = C_TEXT_MUTED

        if IMG_ISOTIPO.exists():
            slide.shapes.add_picture(str(IMG_ISOTIPO), Inches(11.8), Inches(0.4), height=Inches(0.75))

    def add_footer(slide, current_idx, total_slides=8):
        footer_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.05), Inches(11.733), Inches(0.35))
        tf = footer_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = f"ELECTRO-VOLT  |  Maestría en Inteligencia Artificial — UEES 2026  |  Jordan Vera & Jorge Estrella  •  Diapositiva {current_idx} de {total_slides}"
        p.font.name = "Segoe UI"
        p.font.size = Pt(9)
        p.font.color.rgb = RGBColor(148, 163, 184)

    def add_card(slide, left, top, width, height, bg_color=C_CARD_BG, border_color=C_BORDER_LIGHT, border_width=1):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        if border_color:
            card.line.color.rgb = border_color
            card.line.width = Pt(border_width)
        else:
            card.line.fill.background()
        return card

    def add_bullet_point(tf, title, desc, title_color=C_TEXT_DARK, pt_size=10.5, space_after=6):
        p = tf.add_paragraph()
        p.space_after = Pt(space_after)
        p.level = 0
        
        run_title = p.add_run()
        run_title.text = f"•  {title}: "
        run_title.font.name = "Segoe UI"
        run_title.font.size = Pt(pt_size)
        run_title.font.bold = True
        run_title.font.color.rgb = title_color

        run_desc = p.add_run()
        run_desc.text = desc
        run_desc.font.name = "Segoe UI"
        run_desc.font.size = Pt(pt_size)
        run_desc.font.color.rgb = C_TEXT_MUTED

    def add_notes(slide, notes_text):
        notes_slide = slide.notes_slide
        tf = notes_slide.notes_text_frame
        tf.text = notes_text

    # =========================================================================
    # DIAPOSITIVA 1: PORTADA EJECUTIVA
    # =========================================================================
    slide1 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide1, RGBColor(241, 245, 249))

    top_bar = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(0.18))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = C_BLUE_ACCENT
    top_bar.line.fill.background()

    # Contenedor Tarjeta Principal
    add_card(slide1, Inches(0.8), Inches(0.75), Inches(11.733), Inches(5.95), bg_color=C_CARD_BG, border_color=C_BORDER_BLUE, border_width=1.5)

    if IMG_LOGO.exists():
        slide1.shapes.add_picture(str(IMG_LOGO), Inches(1.3), Inches(1.15), height=Inches(1.25))

    title_box = slide1.shapes.add_textbox(Inches(1.3), Inches(2.65), Inches(10.7), Inches(1.8))
    tf1 = title_box.text_frame
    tf1.word_wrap = True
    
    p_badge = tf1.paragraphs[0]
    p_badge.text = "PROYECTO INTEGRADOR DE MAESTRÍA EN INTELIGENCIA ARTIFICIAL — UEES 2026"
    p_badge.font.name = "Segoe UI"
    p_badge.font.size = Pt(11)
    p_badge.font.bold = True
    p_badge.font.color.rgb = C_BLUE_ACCENT
    p_badge.space_after = Pt(4)

    p_main = tf1.add_paragraph()
    p_main.text = "ELECTRO-VOLT"
    p_main.font.name = "Segoe UI"
    p_main.font.size = Pt(36)
    p_main.font.bold = True
    p_main.font.color.rgb = C_NAVY_DARK
    p_main.space_after = Pt(4)

    p_sub = tf1.add_paragraph()
    p_sub.text = "Detección y Clasificación Multiclase de Fallos Eléctricos con Machine Learning e Inteligencia Artificial Explicable (XAI)"
    p_sub.font.name = "Segoe UI"
    p_sub.font.size = Pt(14)
    p_sub.font.color.rgb = C_TEXT_MUTED

    # Autores (2 Columnas)
    card_jordan = add_card(slide1, Inches(1.3), Inches(4.7), Inches(5.1), Inches(1.65), bg_color=C_CARD_BG_BLUE, border_color=C_BORDER_BLUE)
    tf_j = card_jordan.text_frame
    tf_j.word_wrap = True
    tf_j.margin_left = tf_j.margin_right = Inches(0.2)
    tf_j.margin_top = Inches(0.15)
    
    pj1 = tf_j.paragraphs[0]
    pj1.text = "Jordan Fabian Vera Coello"
    pj1.font.name = "Segoe UI"
    pj1.font.size = Pt(13)
    pj1.font.bold = True
    pj1.font.color.rgb = C_NAVY_DARK

    pj2 = tf_j.add_paragraph()
    pj2.text = "Product Owner, ML Engineer & Full-Stack Developer\nArquitectura modular (src/), ingeniería XAI (SHAP), interfaz web interactiva y despliegue cloud."
    pj2.font.name = "Segoe UI"
    pj2.font.size = Pt(9.5)
    pj2.font.color.rgb = C_TEXT_MUTED

    card_jorge = add_card(slide1, Inches(6.8), Inches(4.7), Inches(5.2), Inches(1.65), bg_color=C_CARD_BG_BLUE, border_color=C_BORDER_BLUE)
    tf_e = card_jorge.text_frame
    tf_e.word_wrap = True
    tf_e.margin_left = tf_e.margin_right = Inches(0.2)
    tf_e.margin_top = Inches(0.15)

    pe1 = tf_e.paragraphs[0]
    pe1.text = "Jorge Rafael Estrella Frere"
    pe1.font.name = "Segoe UI"
    pe1.font.size = Pt(13)
    pe1.font.bold = True
    pe1.font.color.rgb = C_NAVY_DARK

    pe2 = tf_e.add_paragraph()
    pe2.text = "Tech Lead, Data Scientist & Experto de Dominio Eléctrico\n22 años de experiencia en subestaciones y redes; análisis EDA, validación física de señales y modelado."
    pe2.font.name = "Segoe UI"
    pe2.font.size = Pt(9.5)
    pe2.font.color.rgb = C_TEXT_MUTED

    docente_box = slide1.shapes.add_textbox(Inches(0.8), Inches(6.8), Inches(11.733), Inches(0.4))
    tfd = docente_box.text_frame
    pd = tfd.paragraphs[0]
    pd.text = "Docente Evaluadora: Ph.D. Gladys Villegas Rugel  |  Universidad de Especialidades Espíritu Santo"
    pd.font.name = "Segoe UI"
    pd.font.size = Pt(10)
    pd.font.color.rgb = C_TEXT_MUTED
    pd.alignment = PP_ALIGN.CENTER

    add_notes(slide1, (
        "GUION DE PRESENTACIÓN - DIAPOSITIVA 1 (PORTADA / 5 SEG):\n"
        "[JORDAN]: Muy buenas tardes, estimada Ph.D. Gladys Villegas y tribunal evaluador. "
        "Somos Jordan Vera y Jorge Estrella, y a continuación presentamos ELECTRO-VOLT, nuestra plataforma "
        "inteligente para la detección y clasificación multiclase de fallos eléctricos con Machine Learning e IA Explicable."
    ))

    # =========================================================================
    # DIAPOSITIVA 2: 1. INTRODUCCIÓN Y PROBLEMA (30 SEGUNDOS)
    # =========================================================================
    slide2 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide2)
    add_header(slide2, "01. INTRODUCCIÓN Y PROBLEMA  •  TIEMPO: 30 SEGUNDOS",
               "El Desafío Operativo en Redes Eléctricas y Nuestra Propuesta de Valor",
               "Reducción radical de tiempos muertos y diagnóstico certero ante contingencias de potencia")
    add_footer(slide2, 2)

    col1 = add_card(slide2, Inches(0.8), Inches(1.6), Inches(3.7), Inches(5.1), bg_color=C_CARD_BG, border_color=C_BORDER_LIGHT)
    tf2_1 = col1.text_frame
    tf2_1.word_wrap = True
    tf2_1.margin_left = tf2_1.margin_right = tf2_1.margin_top = Inches(0.25)
    
    p = tf2_1.paragraphs[0]
    p.text = "1. El Problema Real"
    p.font.name = "Segoe UI"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_DARK
    p.space_after = Pt(12)

    add_bullet_point(tf2_1, "Cortes no programados", "Cortocircuitos y contactos a tierra que interrumpen el suministro eléctrico intempestivamente.")
    add_bullet_point(tf2_1, "Diagnóstico reactivo (~2h)", "El despacho de cuadrillas de campo y la inspección manual toman hasta 2 horas en localizar la avería.")
    add_bullet_point(tf2_1, "Impacto en SAIDI y SAIFI", "Deterioro de índices de continuidad del servicio, multas regulatorias y daño térmico a transformadores.")

    col2 = add_card(slide2, Inches(4.8), Inches(1.6), Inches(3.7), Inches(5.1), bg_color=C_CARD_BG, border_color=C_BORDER_LIGHT)
    tf2_2 = col2.text_frame
    tf2_2.word_wrap = True
    tf2_2.margin_left = tf2_2.margin_right = tf2_2.margin_top = Inches(0.25)

    p = tf2_2.paragraphs[0]
    p.text = "2. La Brecha Tecnológica"
    p.font.name = "Segoe UI"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_DARK
    p.space_after = Pt(12)

    add_bullet_point(tf2_2, "Relés tradicionales rígidos", "Operan por umbrales fijos de sobrecorriente: disparan la línea pero no clasifican la causa física.")
    add_bullet_point(tf2_2, "Cero explicación topológica", "El operador no sabe qué fases interactúan ni si hubo retorno a tierra de alta o baja impedancia.")
    add_bullet_point(tf2_2, "Incertidumbre en maniobra", "Riesgo de reconectar sobre una falla activa, elevando el peligro de explosión o arco eléctrico.")

    col3 = add_card(slide2, Inches(8.8), Inches(1.6), Inches(3.7), Inches(5.1), bg_color=C_CARD_BG_BLUE, border_color=C_BORDER_BLUE)
    tf2_3 = col3.text_frame
    tf2_3.word_wrap = True
    tf2_3.margin_left = tf2_3.margin_right = tf2_3.margin_top = Inches(0.25)

    p = tf2_3.paragraphs[0]
    p.text = "3. Solución ELECTRO-VOLT"
    p.font.name = "Segoe UI"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_BLUE_ACCENT
    p.space_after = Pt(12)

    add_bullet_point(tf2_3, "Inferencia en 16.8 ms", "Clasificación instantánea en subestación a partir de 6 lecturas de telemetría (Va, Vb, Vc, Ia, Ib, Ic).")
    add_bullet_point(tf2_3, "IA Explicable (SHAP)", "Desglose físico transparente del aporte de cada fase antes de ejecutar cualquier maniobra crítica.")
    add_bullet_point(tf2_3, "Costo Cero ($0 USD)", "Software 100% de código abierto para distribuidoras públicas sin presupuesto para software privativo.")
    add_bullet_point(tf2_3, "Reducción del 80%", "Meta proyectada de reducir el tiempo de localización y diagnóstico de horas a milisegundos.")

    add_notes(slide2, (
        "GUION DE PRESENTACIÓN - DIAPOSITIVA 2 (INTRODUCCIÓN Y PROBLEMA / 30 SEG):\n"
        "[JORGE - TECH LEAD & DOMAIN EXPERT]: En sistemas de distribución de energía, las fallas no programadas "
        "ocasionan apagones cuyo diagnóstico manual toma cerca de dos horas, deteriorando severamente los índices "
        "SAIDI y SAIFI y arriesgando activos críticos como transformadores de potencia.\n"
        "[JORDAN - PRODUCT OWNER & ML ENGINEER]: Los relés convencionales operan bajo umbrales fijos: "
        "disparan la protección pero no explican la naturaleza de la falla. "
        "ELECTRO-VOLT resuelve este gap: es una plataforma de costo cero ($0 USD) que procesa las 6 señales trifásicas "
        "en 16.8 milisegundos, clasifica con precisión la topología del fallo y entrega al operador una justificación física "
        "auditable con SHAP."
    ))

    # =========================================================================
    # DIAPOSITIVA 3: 2. DATOS Y METODOLOGÍA (1 MINUTO)
    # =========================================================================
    slide3 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide3)
    add_header(slide3, "02. DATOS Y METODOLOGÍA  •  TIEMPO: 1 MINUTO",
               "Pipeline de Datos, Física de Fallas y Arquitectura del Modelo",
               "Integración rigurosa de principios de ingeniería eléctrica con aprendizaje automático supervisado")
    add_footer(slide3, 3)

    card_metod = add_card(slide3, Inches(0.8), Inches(1.6), Inches(6.2), Inches(5.1), bg_color=C_CARD_BG, border_color=C_BORDER_LIGHT)
    tf3 = card_metod.text_frame
    tf3.word_wrap = True
    tf3.margin_left = tf3.margin_right = tf3.margin_top = Inches(0.25)

    p = tf3.paragraphs[0]
    p.text = "Pipeline Modular y Decisiones Técnicas"
    p.font.name = "Segoe UI"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_DARK
    p.space_after = Pt(10)

    add_bullet_point(tf3, "Dataset Trifásico (7,861 registros)", "Señales continuas simuladas en MATLAB/Simulink correspondientes a voltajes y corrientes instantáneas (Va, Vb, Vc, Ia, Ib, Ic).")
    add_bullet_point(tf3, "Preprocesamiento y Auditoría", "Cero valores nulos y cero duplicados. Partición 80/20 estratificada con barajado aleatorio (shuffle=True) para romper la correlación en bloques temporales.")
    add_bullet_point(tf3, "Unificación Física a 5 Clases", "Normal, Monofásica (LG), Bifásica (LL), Doble Línea a Tierra (LLG) y Trifásica. Se unificaron LLL y LLLG porque en fallas trifásicas simétricas la corriente neutra de retorno es In = 0 A, siendo físicamente indistinguibles para protecciones.")
    add_bullet_point(tf3, "Selección del Modelo", "Evaluación competitiva: Regresión Logística (baseline lineal), SVM RBF (fronteras no lineales) y Random Forest. Se seleccionó Random Forest por su inmunidad a multicolinealidad y rapidez de inferencia.")

    card_graph = add_card(slide3, Inches(7.3), Inches(1.6), Inches(5.2), Inches(5.1), bg_color=C_CARD_BG, border_color=C_BORDER_LIGHT)
    tf3_g = card_graph.text_frame
    tf3_g.word_wrap = True
    tf3_g.margin_left = tf3_g.margin_right = tf3_g.margin_top = Inches(0.2)

    p = tf3_g.paragraphs[0]
    p.text = "Validación de Clases y Balance Físico"
    p.font.name = "Segoe UI"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = C_BLUE_ACCENT
    p.space_after = Pt(4)

    if FIG_DISTRIB_5.exists():
        slide3.shapes.add_picture(str(FIG_DISTRIB_5), Inches(7.5), Inches(2.15), width=Inches(4.8))

    callout = add_card(slide3, Inches(7.5), Inches(4.8), Inches(4.8), Inches(1.65), bg_color=C_CARD_BG_BLUE, border_color=C_BORDER_BLUE)
    tfc = callout.text_frame
    tfc.word_wrap = True
    tfc.margin_left = tfc.margin_right = Inches(0.18)
    tfc.margin_top = Inches(0.12)
    pc = tfc.paragraphs[0]
    pc.text = "Criterio de Dominio Eléctrico:"
    pc.font.name = "Segoe UI"
    pc.font.size = Pt(10.5)
    pc.font.bold = True
    pc.font.color.rgb = C_NAVY_DARK
    pc.space_after = Pt(2)
    pc2 = tfc.add_paragraph()
    pc2.text = "Al fundir LLL y LLLG, el espacio de clasificación se alinea con la teoría de componentes simétricas de Fortescue. Forzar al modelo a distinguir tierra en una falla trifásica simétrica generaba sobreajuste por ruido numérico, pues físicamente la corriente neutra es cero."
    pc2.font.name = "Segoe UI"
    pc2.font.size = Pt(9.5)
    pc2.font.color.rgb = C_TEXT_MUTED

    add_notes(slide3, (
        "GUION DE PRESENTACIÓN - DIAPOSITIVA 3 (DATOS Y METODOLOGÍA / 60 SEG):\n"
        "[JORGE]: Para este desarrollo partimos de un dataset de 7,861 observaciones trifásicas obtenidas mediante simulación física "
        "en MATLAB/Simulink, que capturan voltajes y corrientes instantáneas.\n"
        "[JORDAN]: En el preprocesamiento auditamos la integridad total: cero valores nulos y cero duplicados. "
        "Realizamos una partición 80/20 estratificada con barajado aleatorio para evitar que el orden temporal del dataset sesgara las métricas.\n"
        "[JORGE]: Una decisión técnica fundamental de dominio eléctrico fue unificar las 6 clases originales en 5 estados físicos. "
        "En una falla trifásica balanceada, el sistema de vectores se mantiene simétrico y la corriente por el neutro es cero. Por tanto, "
        "las fallas LLL y LLLG son físicamente idénticas; separarlas forzaba al algoritmo a memorizar ruido numérico de simulación.\n"
        "[JORDAN]: Evaluamos Regresión Logística, SVM con kernel RBF y Random Forest. Seleccionamos Random Forest por su capacidad "
        "para capturar relaciones de fase fuertemente no lineales, manteniendo una inferencia ultrarrápida de 16.8 milisegundos."
    ))

    # =========================================================================
    # DIAPOSITIVA 4: 3. DESARROLLO Y OPTIMIZACIÓN (45 SEGUNDOS)
    # =========================================================================
    slide4 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide4)
    add_header(slide4, "03. DESARROLLO Y OPTIMIZACIÓN  •  TIEMPO: 45 SEGUNDOS",
               "Superación del Sesgo de Simulación y Sensibilidad de Hiperparámetros",
               "Alineación rotacional trifásica y ajuste estructural del ensamble Random Forest")
    add_footer(slide4, 4)

    card_opt = add_card(slide4, Inches(0.8), Inches(1.6), Inches(6.2), Inches(5.1), bg_color=C_CARD_BG, border_color=C_BORDER_LIGHT)
    tf4 = card_opt.text_frame
    tf4.word_wrap = True
    tf4.margin_left = tf4.margin_right = tf4.margin_top = Inches(0.25)

    p = tf4.paragraphs[0]
    p.text = "Desafíos Superados y Optimización (S5)"
    p.font.name = "Segoe UI"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_DARK
    p.space_after = Pt(10)

    add_bullet_point(tf4, "Desafío: Sesgo de Fase A en Kaggle", "El dataset original concentraba las fallas monofásicas casi exclusivamente en la Fase A, cuando en una red real las 3 fases tienen idéntica probabilidad de falla a 120°.")
    add_bullet_point(tf4, "Solución: Invarianza Rotacional (C3)", "Diseño de validación con simetría cíclica C3 y cálculo de retorno por neutro (In = Ia + Ib + Ic) para desacoplar el modelo del sesgo topológico.")
    add_bullet_point(tf4, "Validación Cruzada Estratificada (k=5)", "5 pliegues barajados para garantizar que el ajuste no dependiera de particiones favorables y asegurar robustez estadística.")
    add_bullet_point(tf4, "Ranking de Sensibilidad", "max_depth resultó el hiperparámetro crítico (#1, con 5.85% de impacto en F1). class_weight='balanced' (#2) garantizó recall > 99.5% en la clase minoritaria LLG. n_estimators se estabilizó en 100 árboles.")

    card_pdp = add_card(slide4, Inches(7.3), Inches(1.6), Inches(5.2), Inches(5.1), bg_color=C_CARD_BG, border_color=C_BORDER_LIGHT)
    tf4_g = card_pdp.text_frame
    tf4_g.word_wrap = True
    tf4_g.margin_left = tf4_g.margin_right = tf4_g.margin_top = Inches(0.2)

    p = tf4_g.paragraphs[0]
    p.text = "Validación Marginal: Dependencia Parcial"
    p.font.name = "Segoe UI"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = C_BLUE_ACCENT
    p.space_after = Pt(4)

    if FIG_PDP.exists():
        slide4.shapes.add_picture(str(FIG_PDP), Inches(7.5), Inches(2.15), width=Inches(4.8))

    callout4 = add_card(slide4, Inches(7.5), Inches(5.15), Inches(4.8), Inches(1.3), bg_color=C_CARD_BG_BLUE, border_color=C_BORDER_BLUE)
    tfc4 = callout4.text_frame
    tfc4.word_wrap = True
    tfc4.margin_left = tfc4.margin_right = Inches(0.18)
    tfc4.margin_top = Inches(0.1)
    pc4 = tfc4.paragraphs[0]
    pc4.text = "Comportamiento Físico Internalizado:"
    pc4.font.name = "Segoe UI"
    pc4.font.size = Pt(10.5)
    pc4.font.bold = True
    pc4.font.color.rgb = C_NAVY_DARK
    pc4.space_after = Pt(2)
    pc4_2 = tfc4.add_paragraph()
    pc4_2.text = "Las curvas PDP demuestran que la probabilidad predicha de falla monofásica (LG) solo se dispara cuando |Ia| supera 400 A y Va decae a 0 p.u., confirmando estricto apego a las leyes de Kirchhoff."
    pc4_2.font.name = "Segoe UI"
    pc4_2.font.size = Pt(9.5)
    pc4_2.font.color.rgb = C_TEXT_MUTED

    add_notes(slide4, (
        "GUION DE PRESENTACIÓN - DIAPOSITIVA 4 (DESARROLLO Y OPTIMIZACIÓN / 45 SEG):\n"
        "[JORDAN]: Durante el desarrollo nos enfrentamos a un reto metodológico severo: el dataset de simulación "
        "concentraba las fallas monofásicas casi exclusivamente sobre la Fase A.\n"
        "[JORGE]: Físicamente el sistema trifásico es simétrico a 120°. Para solucionar este sesgo, formulamos "
        "la invariancia rotacional mediante el grupo cíclico C3 y el cálculo del vector de corriente neutra, asegurando "
        "que el algoritmo responda con idéntica precisión sin importar qué fase toque tierra.\n"
        "[JORDAN]: En el Workshop S5 ejecutamos la optimización sistemática con validación cruzada estratificada de 5 pliegues. "
        "El análisis de sensibilidad identificó que la profundidad máxima (max_depth) es el hiperparámetro más crítico, "
        "con una variación del 5.85% en F1. El peso balanceado de clases fue crucial para elevar el recall en fallas bifásicas a tierra "
        "a más del 99.5%."
    ))

    # =========================================================================
    # DIAPOSITIVA 5: 4. VIDEO DEMOSTRATIVO DE LA APP (1 MINUTO)
    # =========================================================================
    slide5 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide5, C_NAVY_DARK)
    
    top_bar5 = slide5.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(0.2))
    top_bar5.fill.solid()
    top_bar5.fill.fore_color.rgb = C_BLUE_ACCENT
    top_bar5.line.fill.background()

    if IMG_ISOTIPO.exists():
        slide5.shapes.add_picture(str(IMG_ISOTIPO), Inches(5.9), Inches(1.05), height=Inches(1.5))

    center_box = slide5.shapes.add_textbox(Inches(1.5), Inches(2.65), Inches(10.333), Inches(1.3))
    tf5 = center_box.text_frame
    tf5.word_wrap = True
    
    p = tf5.paragraphs[0]
    p.text = "04. DEMOSTRACIÓN EN VIVO  •  DURACIÓN: 1 MINUTO"
    p.font.name = "Segoe UI"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = RGBColor(96, 165, 250)
    p.alignment = PP_ALIGN.CENTER
    p.space_after = Pt(4)

    p2 = tf5.add_paragraph()
    p2.text = "Plataforma Web Operativa ELECTRO-VOLT"
    p2.font.name = "Segoe UI"
    p2.font.size = Pt(28)
    p2.font.bold = True
    p2.font.color.rgb = RGBColor(255, 255, 255)
    p2.alignment = PP_ALIGN.CENTER
    p2.space_after = Pt(4)

    p3 = tf5.add_paragraph()
    p3.text = "[ Transición al navegador web para interactuar con la aplicación desplegada en vivo ]"
    p3.font.name = "Segoe UI"
    p3.font.size = Pt(13)
    p3.font.bold = True
    p3.font.color.rgb = RGBColor(253, 224, 71)
    p3.alignment = PP_ALIGN.CENTER

    demo_card = add_card(slide5, Inches(1.8), Inches(4.3), Inches(9.733), Inches(2.2), bg_color=RGBColor(15, 23, 42), border_color=RGBColor(30, 58, 138), border_width=1.5)
    tf5_d = demo_card.text_frame
    tf5_d.word_wrap = True
    tf5_d.margin_left = tf5_d.margin_right = Inches(0.4)
    tf5_d.margin_top = Inches(0.2)

    pd1 = tf5_d.paragraphs[0]
    pd1.text = "Puntos Clave del Flujo Operativo en Consola:"
    pd1.font.name = "Segoe UI"
    pd1.font.size = Pt(13)
    pd1.font.bold = True
    pd1.font.color.rgb = RGBColor(147, 197, 253)
    pd1.space_after = Pt(8)

    add_bullet_point(tf5_d, "1. Diagnóstico Individual Instantáneo", "Ingreso de señales trifásicas, probabilidad por clase, nivel de confianza y semáforo de criticidad.", title_color=RGBColor(255, 255, 255))
    add_bullet_point(tf5_d, "2. Auditoría Física con XAI (SHAP)", "Gráfico de cascada local que explica el aporte numérico de cada voltaje y corriente en la decisión del modelo.", title_color=RGBColor(255, 255, 255))
    add_bullet_point(tf5_d, "3. Telemetría Masiva por Lote", "Carga de CSV con telemetría de subestación, matriz diagnóstica en tiempo real y descarga de reporte ejecutivo.", title_color=RGBColor(255, 255, 255))

    add_notes(slide5, (
        "GUION DE PRESENTACIÓN - DIAPOSITIVA 5 (VIDEO DEMOSTRATIVO DE LA APP / 60 SEG):\n"
        "[JORDAN]: En este momento realizamos la transición de pantalla para demostrar en tiempo real "
        "el funcionamiento de la aplicación web ELECTRO-VOLT desarrollada con Streamlit.\n"
        "[PASE A LA APP STREAMLIT (1 MINUTO)]:\n"
        "1. Jordan muestra la interfaz ejecutiva, el switch de modo claro/oscuro y el selector de modo de diagnóstico.\n"
        "2. En el 'Diagnóstico Individual', Jorge ingresa lecturas de falla monofásica a tierra (LG) y bifásica (LL).\n"
        "3. Se aprecia la respuesta inmediata (< 17 ms), el semáforo rojo de criticidad y las recomendaciones operativas precisas.\n"
        "4. Jordan hace zoom en el gráfico de explicabilidad local SHAP, evidenciando cómo la corriente excesiva de la fase en cortocircuito aportó positivamente a la predicción.\n"
        "5. Pasan a 'Diagnóstico por Lote', cargan 'ejemplos_prueba.csv', procesan múltiples contingencias en milisegundos y exportan el reporte ejecutivo para despacho de cuadrillas."
    ))

    # =========================================================================
    # DIAPOSITIVA 6: 5. EVALUACIÓN Y RESULTADOS (45 SEGUNDOS)
    # =========================================================================
    slide6 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide6)
    add_header(slide6, "05. EVALUACIÓN Y RESULTADOS  •  TIEMPO: 45 SEGUNDOS",
               "Métricas SMART, Comparativa vs. Baselines y Casos Límite",
               "Rendimiento del modelo final evaluado sobre el conjunto de prueba independiente (1,573 muestras)")
    add_footer(slide6, 6)

    kpi_defs = [
        ("99.94%", "Accuracy Global", "1,572 de 1,573 aciertos", C_GREEN_SUCCESS),
        ("99.91%", "F1-Score Macro", "CV 5-Fold: 0.999 ± 0.001", C_BLUE_ACCENT),
        ("99.56%", "Recall Mínimo", "Clase crítica LLG", C_BLUE_ACCENT),
        ("16.8 ms", "Latencia Inferencia", "Throughput: 70k m/s", C_NAVY_DARK),
    ]

    for idx, (val, label, sublabel, color) in enumerate(kpi_defs):
        x = Inches(0.8 + idx * 2.98)
        kpi_card = add_card(slide6, x, Inches(1.5), Inches(2.78), Inches(1.15), bg_color=C_CARD_BG, border_color=C_BORDER_LIGHT)
        tf_k = kpi_card.text_frame
        tf_k.word_wrap = True
        tf_k.margin_left = tf_k.margin_right = Inches(0.15)
        tf_k.margin_top = Inches(0.08)

        p = tf_k.paragraphs[0]
        p.text = val
        p.font.name = "Segoe UI"
        p.font.size = Pt(21)
        p.font.bold = True
        p.font.color.rgb = color

        p2 = tf_k.add_paragraph()
        p2.text = label
        p2.font.name = "Segoe UI"
        p2.font.size = Pt(9.5)
        p2.font.bold = True
        p2.font.color.rgb = C_NAVY_DARK

        p3 = tf_k.add_paragraph()
        p3.text = sublabel
        p3.font.name = "Segoe UI"
        p3.font.size = Pt(8.5)
        p3.font.color.rgb = C_TEXT_MUTED

    # Fila Inferior Izquierda (Comparativa vs Baselines)
    card_eval = add_card(slide6, Inches(0.8), Inches(2.8), Inches(6.4), Inches(4.0), bg_color=C_CARD_BG, border_color=C_BORDER_LIGHT)
    tf6 = card_eval.text_frame
    tf6.word_wrap = True
    tf6.margin_left = tf6.margin_right = tf6.margin_top = Inches(0.2)

    p = tf6.paragraphs[0]
    p.text = "Comparativa vs. Baselines y Casos Límite"
    p.font.name = "Segoe UI"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_DARK
    p.space_after = Pt(8)

    add_bullet_point(tf6, "Superación del Baseline", "Random Forest (99.94%) pulveriza al clasificador aleatorio (20%) y supera drásticamente a Regresión Logística (72.8%) y SVM RBF (98.4%).")
    add_bullet_point(tf6, "Desempeño Perfecto", "100% de precisión y recall en estados Normal, Monofásica a Tierra (LG), Bifásica (LL) y Trifásica.")
    add_bullet_point(tf6, "Único Caso Límite (1 en 1,573)", "Un caso de LLG se clasificó como LL por una resistencia de puesta a tierra simulada muy elevada, que atenuó la corriente de retorno neutro.")
    add_bullet_point(tf6, "Protección Fuera de Distribución (OOD)", "Lecturas anómalas por pérdida de señal o ceros absolutos son detectadas y bloqueadas antes de la inferencia por el validador de integridad física.")

    # Fila Inferior Derecha (Matriz de Confusión)
    card_cm = add_card(slide6, Inches(7.5), Inches(2.8), Inches(5.0), Inches(4.0), bg_color=C_CARD_BG, border_color=C_BORDER_LIGHT)
    tf6_cm = card_cm.text_frame
    tf6_cm.word_wrap = True
    tf6_cm.margin_left = tf6_cm.margin_right = tf6_cm.margin_top = Inches(0.15)

    p = tf6_cm.paragraphs[0]
    p.text = "Matriz de Confusión en Test (1,573 casos)"
    p.font.name = "Segoe UI"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = C_BLUE_ACCENT

    if FIG_MATRIZ_CONF.exists():
        # Ajuste exacto de altura a 3.15 pulgadas para dejar margen perfecto arriba y abajo
        slide6.shapes.add_picture(str(FIG_MATRIZ_CONF), Inches(7.85), Inches(3.25), height=Inches(3.25))

    add_notes(slide6, (
        "GUION DE PRESENTACIÓN - DIAPOSITIVA 6 (EVALUACIÓN Y RESULTADOS / 45 SEG):\n"
        "[JORDAN]: En la evaluación independiente sobre 1,573 muestras de prueba, ELECTRO-VOLT alcanzó "
        "una exactitud global del 99.94% y un F1-score macro del 99.91%, superando holgadamente los umbrales SMART del 90%.\n"
        "[JORGE]: La matriz de confusión evidencia una diagonal dominante casi perfecta: 1,572 clasificaciones correctas "
        "y un solo error en una falla doble línea a tierra clasificada como bifásica simple, atribuible a una alta resistencia "
        "de contacto a tierra simulada que atenuó el retorno neutro.\n"
        "[JORDAN]: En eficiencia operativa, el modelo responde en apenas 16.8 milisegundos y procesa más de 70,000 muestras por segundo. "
        "Adicionalmente, incorporamos validadores físicos que bloquean datos anómalos fuera de distribución antes de predecir."
    ))

    # =========================================================================
    # DIAPOSITIVA 7: 6. CONSIDERACIONES ÉTICAS (45 SEGUNDOS) - OBLIGATORIO
    # =========================================================================
    slide7 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide7)
    add_header(slide7, "06. CONSIDERACIONES ÉTICAS Y GOBERNANZA  •  TIEMPO: 45 SEGUNDOS (OBLIGATORIO)",
               "Gobernanza Ciberfísica, Mitigación de Sesgos y Seguridad Humana",
               "Garantía de auditoría, trazabilidad física y el principio inquebrantable de Humano en el Bucle")
    add_footer(slide7, 7)

    # 4 Cuadrantes Éticos
    c1 = add_card(slide7, Inches(0.8), Inches(1.6), Inches(5.7), Inches(2.4), bg_color=C_CARD_BG, border_color=C_BORDER_LIGHT)
    tf7_1 = c1.text_frame
    tf7_1.word_wrap = True
    tf7_1.margin_left = tf7_1.margin_right = tf7_1.margin_top = Inches(0.2)
    p = tf7_1.paragraphs[0]
    p.text = "1. Sesgos Identificados"
    p.font.name = "Segoe UI"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_DARK
    p.space_after = Pt(4)
    add_bullet_point(tf7_1, "Sesgo Sim-to-Real", "Entrenamiento sobre simulaciones sintéticas que no incluyen armónicos industriales ni transitorios de capacitores.")
    add_bullet_point(tf7_1, "Sesgo de fase inicial", "Sobrerrepresentación de fase A en el dataset base, mitigado mediante invariancia de permutación de fases.")

    c2 = add_card(slide7, Inches(6.8), Inches(1.6), Inches(5.7), Inches(2.4), bg_color=C_CARD_BG, border_color=C_BORDER_LIGHT)
    tf7_2 = c2.text_frame
    tf7_2.word_wrap = True
    tf7_2.margin_left = tf7_2.margin_right = tf7_2.margin_top = Inches(0.2)
    p = tf7_2.paragraphs[0]
    p.text = "2. Impacto Social y Humano"
    p.font.name = "Segoe UI"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = C_GREEN_SUCCESS
    p.space_after = Pt(4)
    add_bullet_point(tf7_2, "Seguridad de linieros", "Previene electrocuciones y arcos eléctricos al identificar con exactitud si una línea tiene contacto con tierra.")
    add_bullet_point(tf7_2, "Servicios críticos", "Restablecimiento expedito del fluido eléctrico en hospitales, centros de salud y estaciones de bombeo de agua.")
    add_bullet_point(tf7_2, "Costo Cero ($0 USD)", "Tecnología abierta para distribuidoras públicas sin presupuesto para licencias privativas.")

    c3 = add_card(slide7, Inches(0.8), Inches(4.2), Inches(5.7), Inches(2.6), bg_color=C_CARD_BG_BLUE, border_color=C_BORDER_BLUE)
    tf7_3 = c3.text_frame
    tf7_3.word_wrap = True
    tf7_3.margin_left = tf7_3.margin_right = tf7_3.margin_top = Inches(0.2)
    p = tf7_3.paragraphs[0]
    p.text = "3. Medidas de Mitigación Técnicas"
    p.font.name = "Segoe UI"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = C_BLUE_ACCENT
    p.space_after = Pt(4)
    add_bullet_point(tf7_3, "Explicabilidad XAI (SHAP)", "Apertura total de la caja negra. El operador de consola audita la contribución de cada fase en milisegundos.")
    add_bullet_point(tf7_3, "Validación neutra (|In| > 20 A)", "Cálculo obligatorio de corriente neutra para evitar falsos negativos en fallas con riesgo mortal a tierra.")
    add_bullet_point(tf7_3, "Módulo OOD robusto", "Detección y rechazo de lecturas imposibles o sensores descalibrados antes de ejecutar el modelo.")

    c4 = add_card(slide7, Inches(6.8), Inches(4.2), Inches(5.7), Inches(2.6), bg_color=C_CARD_BG, border_color=C_BORDER_LIGHT)
    tf7_4 = c4.text_frame
    tf7_4.word_wrap = True
    tf7_4.margin_left = tf7_4.margin_right = tf7_4.margin_top = Inches(0.2)
    p = tf7_4.paragraphs[0]
    p.text = "4. Limitaciones Éticas y Frontera de Decisión"
    p.font.name = "Segoe UI"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = C_AMBER_WARN
    p.space_after = Pt(4)
    add_bullet_point(tf7_4, "Soporte estrictamente consultivo", "El sistema NUNCA dispara ni reconecta interruptores de potencia automáticamente.")
    add_bullet_point(tf7_4, "Humano en el Bucle obligatorio", "La potestad jurídica y operativa de maniobra recae invariablemente en el operador certificado.")
    add_bullet_point(tf7_4, "No reemplaza al relé de protección", "La protección de sobrecorriente convencional continúa siendo la primera línea de despeje ante contingencias.")

    add_notes(slide7, (
        "GUION DE PRESENTACIÓN - DIAPOSITIVA 7 (CONSIDERACIONES ÉTICAS / 45 SEG - OBLIGATORIO):\n"
        "[JORGE]: En sistemas ciberfísicos críticos, la ética constituye una condición fundamental de seguridad humana. "
        "Un falso negativo que no clasifique una falla a tierra representa un riesgo mortal de electrocución o arco eléctrico "
        "para las cuadrillas que intervienen los alimentadores.\n"
        "[JORDAN]: Reconocemos con total honestidad el sesgo de simulación (Sim-to-Real gap), dado que el modelo fue entrenado "
        "sobre señales ideales de simulación. "
        "Para mitigarlo, implementamos explicabilidad obligatoria con SHAP y una regla de dominio eléctrico que exige alertar "
        "siempre que la corriente neutra calculada supere los 20 amperios.\n"
        "[JORGE]: Finalmente, establecemos una frontera ética inviolable: ELECTRO-VOLT es una herramienta de soporte consultivo "
        "con Humano en el Bucle (Human-in-the-Loop). El sistema no ejecuta disparos físicos autónomos; la autorización "
        "de cualquier maniobra en la subestación recae siempre en el operador humano de turno."
    ))

    # =========================================================================
    # DIAPOSITIVA 8: 7. CIERRE Y TRABAJO FUTURO (15 SEGUNDOS)
    # =========================================================================
    slide8 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide8)
    add_header(slide8, "07. CIERRE Y TRABAJO FUTURO  •  TIEMPO: 15 SEGUNDOS",
               "Logro Principal, Hoja de Ruta Tecnológica y Código Abierto",
               "De un proyecto de maestría a una herramienta transferible para el sector eléctrico")
    add_footer(slide8, 8)

    card_cierre = add_card(slide8, Inches(0.8), Inches(1.6), Inches(6.2), Inches(5.1), bg_color=C_CARD_BG, border_color=C_BORDER_LIGHT)
    tf8 = card_cierre.text_frame
    tf8.word_wrap = True
    tf8.margin_left = tf8.margin_right = tf8.margin_top = Inches(0.25)

    p = tf8.paragraphs[0]
    p.text = "Logro Principal y Hoja de Ruta"
    p.font.name = "Segoe UI"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_DARK
    p.space_after = Pt(10)

    add_bullet_point(tf8, "Logro Consolidado", "Plataforma web end-to-end con 99.94% de exactitud y 16.8 ms de respuesta que une la teoría de sistemas de potencia con IA explicable a costo cero.")
    add_bullet_point(tf8, "Integración IEC 61850", "Ingesta en tiempo real de mensajes GOOSE y Sampled Values para conexión directa con IEDs y relés de subestación.")
    add_bullet_point(tf8, "Despliegue en el Borde (Edge)", "Contenerización en Docker para ejecución local dentro de la red privada de subestación, garantizando ciberseguridad sin internet público.")
    add_bullet_point(tf8, "Piloto con Oscilografías Reales", "Calibración con registros COMTRADE de fallas históricas de distribuidoras eléctricas locales (CNEL EP / EEQ).")

    card_repo = add_card(slide8, Inches(7.3), Inches(1.6), Inches(5.2), Inches(5.1), bg_color=C_CARD_BG_BLUE, border_color=C_BORDER_BLUE)
    tf8_r = card_repo.text_frame
    tf8_r.word_wrap = True
    tf8_r.margin_left = tf8_r.margin_right = tf8_r.margin_top = Inches(0.25)

    p = tf8_r.paragraphs[0]
    p.text = "Código Abierto y Repositorio Oficial"
    p.font.name = "Segoe UI"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_BLUE_ACCENT
    p.space_after = Pt(10)

    add_bullet_point(tf8_r, "Repositorio GitHub", "Código modular, limpio y reproducible bajo estándares de calidad PEP 8.")
    add_bullet_point(tf8_r, "Pruebas Unitarias al 100%", "Suite de pytest cubriendo integridad de datos, límites físicos OOD, inferencia y explicabilidad SHAP.")
    add_bullet_point(tf8_r, "Documentación Integral", "Reporte de optimización (Workshop S5), arquitectura y consideraciones éticas disponibles en docs/.")

    gh_box = add_card(slide8, Inches(7.6), Inches(4.9), Inches(4.6), Inches(1.45), bg_color=C_NAVY_DARK, border_color=None)
    tf_gh = gh_box.text_frame
    tf_gh.word_wrap = True
    tf_gh.margin_left = tf_gh.margin_right = Inches(0.2)
    tf_gh.margin_top = Inches(0.12)
    
    pgh1 = tf_gh.paragraphs[0]
    pgh1.text = "Repositorio Oficial del Proyecto en GitHub:"
    pgh1.font.name = "Segoe UI"
    pgh1.font.size = Pt(10)
    pgh1.font.color.rgb = RGBColor(147, 197, 253)

    pgh2 = tf_gh.add_paragraph()
    pgh2.text = "https://github.com/fabianvcf/ELECTRO-VOLT"
    pgh2.font.name = "Segoe UI"
    pgh2.font.size = Pt(11.5)
    pgh2.font.bold = True
    pgh2.font.color.rgb = RGBColor(255, 255, 255)
    pgh2.space_after = Pt(4)

    pgh3 = tf_gh.add_paragraph()
    pgh3.text = "¡Muchas gracias por su atención!  •  Preguntas y Respuestas"
    pgh3.font.name = "Segoe UI"
    pgh3.font.size = Pt(9.5)
    pgh3.font.color.rgb = RGBColor(203, 213, 225)

    add_notes(slide8, (
        "GUION DE PRESENTACIÓN - DIAPOSITIVA 8 (CIERRE / 15 SEG):\n"
        "[JORDAN]: En conclusión, ELECTRO-VOLT demuestra cómo la inteligencia artificial explicable "
        "transforma un proceso manual de dos horas en un diagnóstico físico de milisegundos a costo cero.\n"
        "[JORGE]: Como trabajo futuro proyectamos la integración con el estándar IEC 61850 y pruebas piloto con oscilografías de campo. "
        "Todo nuestro código, pruebas unitarias y documentación técnica están abiertos en nuestro repositorio de GitHub. ¡Muchas gracias!"
    ))

    prs.save(str(OUTPUT_FILE))
    print(f"[OK] Presentacion generada exitosamente en: {OUTPUT_FILE}")
    print(f"[OK] Total diapositivas generadas: {len(prs.slides)}")


if __name__ == "__main__":
    crear_presentacion()
