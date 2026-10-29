"""Módulo de exportación de reportes diagnósticos (Excel, PDF ReportLab, CSV)."""

from __future__ import annotations

import base64
import datetime
import io
from pathlib import Path
import sys

import pandas as pd
import streamlit as st

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import landscape, letter
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    REPORTLAB_DISPONIBLE = True
except ImportError:
    REPORTLAB_DISPONIBLE = False

from app.utils import render_html
from src.config import obtener_logger

logger = obtener_logger(__name__)


def generar_excel_diagnostico(df_res: pd.DataFrame) -> bytes:
    """Genera un archivo Excel (.xlsx) con los resultados del diagnóstico en lote."""
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df_res.to_excel(writer, index=False, sheet_name="Diagnostico_Lote")
    return buf.getvalue()


def generar_pdf_diagnostico(df_res: pd.DataFrame) -> bytes:
    """Genera un reporte PDF formal con metadata ejecutiva y tabla de eventos en lote."""
    if not REPORTLAB_DISPONIBLE:
        return b""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=landscape(letter),
        rightMargin=25,
        leftMargin=25,
        topMargin=25,
        bottomMargin=25,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        textColor=colors.HexColor("#002a69"),
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        textColor=colors.HexColor("#475569"),
        spaceAfter=10,
    )

    elements = []
    elements.append(Paragraph("ELECTROVOLT — REPORTE DE TELEMETRÍA Y DIAGNÓSTICO EN LOTE", title_style))
    fecha_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    volumen = len(df_res)
    anomalos = int((df_res["Diagnostico"] != "Normal").sum()) if "Diagnostico" in df_res.columns else 0
    tasa = (anomalos / volumen * 100) if volumen > 0 else 0

    meta_text = (
        f"<b>Fecha de emisión:</b> {fecha_str} | "
        f"<b>Total lecturas:</b> {volumen:,} | "
        f"<b>Eventos con anomalía/falla:</b> {anomalos:,} ({tasa:.1f}%) | "
        f"<b>Modelo:</b> Random Forest (5 clases)"
    )
    elements.append(Paragraph(meta_text, subtitle_style))

    # Columnas prioritarias para la tabla
    cols_prioritarias = ["Va", "Vb", "Vc", "Ia", "Ib", "Ic", "Diagnostico", "Confianza (%)"]
    cols_existentes = [c for c in cols_prioritarias if c in df_res.columns]
    if not cols_existentes:
        cols_existentes = list(df_res.columns[:8])

    df_sub = df_res[cols_existentes].head(120)

    encabezados = []
    for c in cols_existentes:
        if c.startswith("V") and len(c) <= 3:
            encabezados.append(f"{c} (p.u.)")
        elif c.startswith("I") and len(c) <= 3:
            encabezados.append(f"{c} (A)")
        else:
            encabezados.append(c)

    filas = [encabezados]
    for _, r in df_sub.iterrows():
        fila_str = []
        for c in cols_existentes:
            val = r[c]
            if isinstance(val, (float, int)):
                if c.startswith("V"):
                    fila_str.append(f"{val:.4f}")
                elif c.startswith("I"):
                    fila_str.append(f"{val:.2f}")
                else:
                    fila_str.append(str(val))
            else:
                fila_str.append(str(val))
        filas.append(fila_str)

    t = Table(filas, repeatRows=1)
    t.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#002a69")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 7.5),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 4),
            ("TOPPADDING", (0, 0), (-1, 0), 4),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 6.5),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ])
    )
    elements.append(t)

    if volumen > 120:
        elements.append(Spacer(1, 6))
        nota_limite = (
            f"<i>* Mostrando las primeras 120 filas de {volumen:,} registros totales analizados. "
            "Para el conjunto de datos completo descargue en formato CSV o XLSX.</i>"
        )
        elements.append(Paragraph(nota_limite, subtitle_style))

    doc.build(elements)
    return buf.getvalue()


def render_barra_descargas(df_res: pd.DataFrame):
    """Renderiza una barra con label 'Descargar resultados en:' y 3 botones con iconos redondeados para CSV, XLSX y PDF."""
    buf_csv = io.StringIO()
    df_res.to_csv(buf_csv, index=False)
    b64_csv = base64.b64encode(buf_csv.getvalue().encode("utf-8")).decode()

    # XLSX
    try:
        xlsx_bytes = generar_excel_diagnostico(df_res)
        b64_xlsx = base64.b64encode(xlsx_bytes).decode()
    except Exception as err:
        logger.warning(f"No se pudo generar el archivo XLSX para exportación: {err}")
        b64_xlsx = ""

    # PDF
    try:
        pdf_bytes = generar_pdf_diagnostico(df_res)
        b64_pdf = base64.b64encode(pdf_bytes).decode()
    except Exception as err:
        logger.warning(f"No se pudo generar el archivo PDF para exportación: {err}")
        b64_pdf = ""

    svg_csv = (
        '<svg style="width: 22px; height: 22px;" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">'
        '<path d="M14 2H6C4.89543 2 4 2.89543 4 4V20C4 21.1046 4.89543 22 6 22H18C19.1046 22 20 21.1046 20 20V8L14 2Z" fill="#F0F9FF" stroke="#0284C7" stroke-width="1.8" stroke-linejoin="round"/>'
        '<path d="M14 2V8H20" stroke="#0284C7" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'
        '<rect x="6.5" y="12" width="11" height="6.5" rx="1.5" fill="#0284C7"/>'
        '<text x="12" y="16.8" font-family="\'JetBrains Mono\', Arial, sans-serif" font-size="4.2" font-weight="800" fill="#FFFFFF" text-anchor="middle" letter-spacing="0.3">CSV</text>'
        '</svg>'
    )

    svg_xlsx = (
        '<svg style="width: 22px; height: 22px;" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">'
        '<path d="M14 2H6C4.89543 2 4 2.89543 4 4V20C4 21.1046 4.89543 22 6 22H18C19.1046 22 20 21.1046 20 20V8L14 2Z" fill="#F0FDF4" stroke="#16A34A" stroke-width="1.8" stroke-linejoin="round"/>'
        '<path d="M14 2V8H20" stroke="#16A34A" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'
        '<rect x="6" y="12" width="12" height="6.5" rx="1.5" fill="#16A34A"/>'
        '<text x="12" y="16.8" font-family="\'JetBrains Mono\', Arial, sans-serif" font-size="3.8" font-weight="800" fill="#FFFFFF" text-anchor="middle" letter-spacing="0.2">XLSX</text>'
        '</svg>'
    )

    svg_pdf = (
        '<svg style="width: 22px; height: 22px;" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">'
        '<path d="M14 2H6C4.89543 2 4 2.89543 4 4V20C4 21.1046 4.89543 22 6 22H18C19.1046 22 20 21.1046 20 20V8L14 2Z" fill="#FEF2F2" stroke="#DC2626" stroke-width="1.8" stroke-linejoin="round"/>'
        '<path d="M14 2V8H20" stroke="#DC2626" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'
        '<rect x="6.5" y="12" width="11" height="6.5" rx="1.5" fill="#DC2626"/>'
        '<text x="12" y="16.8" font-family="\'JetBrains Mono\', Arial, sans-serif" font-size="4.2" font-weight="800" fill="#FFFFFF" text-anchor="middle" letter-spacing="0.3">PDF</text>'
        '</svg>'
    )

    link_xlsx = (
        f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64_xlsx}" download="diagnostico_subestacion_lote.xlsx" class="download-icon-btn">'
        '<span class="btn-tooltip">Descargar en .xlsx</span>'
        f'{svg_xlsx}</a>'
        if b64_xlsx else ''
    )

    link_pdf = (
        f'<a href="data:application/pdf;base64,{b64_pdf}" download="diagnostico_subestacion_lote.pdf" class="download-icon-btn">'
        '<span class="btn-tooltip">Descargar en .pdf</span>'
        f'{svg_pdf}</a>'
        if b64_pdf else ''
    )

    html_bar = f"""
    <div class="download-action-bar">
        <span class="download-action-label">Descargar resultados en:</span>
        <div class="download-icon-group">
            <a href="data:text/csv;base64,{b64_csv}" download="diagnostico_subestacion_lote.csv" class="download-icon-btn">
                <span class="btn-tooltip">Descargar en .csv</span>
                {svg_csv}
            </a>
            {link_xlsx}
            {link_pdf}
        </div>
    </div>
    """
    render_html(html_bar)
