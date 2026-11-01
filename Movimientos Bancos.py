import os
import sys
import pandas as pd
import streamlit as st

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

if st.button("🔄 Actualizar Datos", use_container_width=True):
    st.rerun()

# Título principal centrado
st.html(
    '<h2 style="text-align: center; font-size: 26px; font-weight: bold; margin-top: 10px; margin-bottom: 20px; color: #FFFFFF;">Movimientos: Austro y Jardín.</h2>'
)

EXCEL_URL_AUSTRO = "https://docs.google.com/spreadsheets/d/19aw00haXlThBf0AlHwMsYNabeFGAbbjw/export?format=xlsx"
EXCEL_URL_JARDIN = "https://docs.google.com/spreadsheets/d/1RLGdS04je773Qi0U2Z02A49VMrgF5ViH/export?format=xlsx"


@st.cache_data(ttl=60)
def cargar_todas_las_hojas(url):
    try:
        return pd.read_excel(url, sheet_name=None)
    except Exception:
        return {}


def obtener_hoja(dict_hojas, nombre_buscado):
    for key in dict_hojas.keys():
        if key.strip().lower() == nombre_buscado.strip().lower():
            return dict_hojas[key]
    for key in dict_hojas.keys():
        if nombre_buscado.strip().lower() in key.strip().lower():
            return dict_hojas[key]
    return pd.DataFrame()


def render_custom_table(df):
    css = """
    <style>
    .table-container {
        max-height: 420px;
        width: fit-content;
        max-width: 100%;
        overflow-x: auto;
        overflow-y: auto;
        padding: 0px;
        border: 2px solid #000000;
        border-radius: 8px;
        margin-bottom: 20px;
        background-color: #FFFFFF;
    }
    .custom-table {
        width: max-content;
        border-collapse: separate;
        border-spacing: 0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-size: 14px;
        color: #000000 !important;
    }
    .custom-table th {
        position: sticky !important;
        top: 0 !important;
        z-index: 20 !important;
        background-color: #FFEB3B !important;
        color: #000000 !important;
        text-align: center !important;
        padding: 10px 14px;
        font-weight: bold;
        white-space: nowrap;
        border-bottom: 1px solid #000000;
        border-right: 1px solid #000000;
        width: max-content !important;
    }
    .custom-table th.col-sticky {
        position: sticky !important;
        left: 0 !important;
        top: 0 !important;
        z-index: 50 !important;
        width: max-content !important;
        white-space: nowrap !important;
        background-color: #FFEB3B !important;
        color: #000000 !important;
        box-shadow: 2px 0 5px rgba(0,0,0,0.2);
    }
    .custom-table td {
        position: static !important;
        z-index: auto !important;
        text-align: center !important;
        padding: 10px 14px;
        white-space: nowrap;
        color: #000000 !important;
        font-weight: 600;
        border-bottom: 1px solid #000000;
        border-right: 1px solid #000000;
        width: max-content !important;
    }
    .custom-table td.col-sticky {
        position: sticky !important;
        left: 0 !important;
        z-index: 30 !important;
        width: max-content !important;
        white-space: nowrap !important;
        background-color: #FFEB3B !important;
        background-clip: padding-box !important;
        font-weight: bold;
        color: #000000 !important;
        box-shadow: 2px 0 5px rgba(0,0,0,0.2);
    }
    .row-even td:not(.col-sticky) { background-color: #E8F5E9 !important; }
    .row-odd td:not(.col-sticky) { background-color: #FFFDE7 !important; }
    </style>
    """

    html = css + '<div class="table-container"><table class="custom-table"><thead><tr>'

    for idx, col in enumerate(df.columns):
        sticky_class = ' class="col-sticky"' if idx == 0 else ""
        clean_col = str(col).replace(" ($)", "").replace("$", "")
        header_text = (
            clean_col.replace(" ", "<br>") if len(clean_col) > 10 else clean_col
        )
        html += f"<th{sticky_class}>{header_text}</th>"

    html += "</tr></thead><tbody>"

    for row_idx, row in df.iterrows():
        row_class = "row-even" if row_idx % 2 == 0 else "row-odd"
        html += f'<tr class="{row_class}">'
        for col_idx, val in enumerate(row):
            sticky_class = ' class="col-sticky"' if col_idx == 0 else ""
            if col_idx == 0:
                formatted_val = str(val)
            elif isinstance(val, (int, float)):
                col_name = str(df.columns[col_idx])
                if (
                    "Total" in col_name
                    or "Día" in col_name
                    or "Transferido" in col_name
                    or "Comprado" in col_name
                ):
                    formatted_val = f"${val:,.2f}"
                else:
                    formatted_val = f"{int(val):,}" if val == int(val) else f"{val:,}"
            else:
                formatted_val = str(val)
            html += f"<td{sticky_class}>{formatted_val}</td>"
        html += "</tr>"

    html += "</tbody></table></div>"
    return html


def render_kpi_card(titulo, valor_str, detalle_str=""):
    detalle_html = (
        f'<div style="color: #E2E8F0; font-size: 14px; margin-top: 6px; font-weight: 600;">{detalle_str}</div>'
        if detalle_str
        else ""
    )
    return f"""
    <div style="
        background-color: #0F172A;
        border: 2px solid #FFEB3B;
        border-radius: 10px;
        padding: 12px;
        text-align: center;
        margin-bottom: 12px;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.3);
    ">
        <div style="color: #FFEB3B; font-size: 13px; font-weight: 600; margin-bottom: 4px;">{titulo}</div>
        <div style="color: #FFFFFF; font-size: 20px; font-weight: bold;">{valor_str}</div>
        {detalle_html}
    </div>
    """


def dos_lineas_banco(nombre):
    nombre_str = str(nombre).strip()
    words = nombre_str.split()
    if len(words) == 2:
        return f"{words[0]}<br>{words[1]}"
    elif len(words) == 3 and words[1].lower() in ["de", "del", "la", "el"]:
        return f"{words[0]} {words[1]}<br>{words[2]}"
    elif len(words) > 1:
        mid = len(words) // 2
        return f"{' '.join(words[:mid])}<br>{' '.join(words[mid:])}"
    return nombre_str


# Carga de datos de ambas fuentes
hojas_austro = cargar_todas_las_hojas(EXCEL_URL_AUSTRO)
hojas_jardin = cargar_todas_las_hojas(EXCEL_URL_JARDIN)

# --- PROCESAMIENTO BANCO DEL AUSTRO ---
df_raw_retiros_a = obtener_hoja(hojas_austro, "Retiros")
df_retiros_a = pd.DataFrame()
if not df_raw_retiros_a.empty and "Fecha" in df_raw_retiros_a.columns and "Valor" in df_raw_retiros_a.columns:
    df_retiros_a = df_raw_retiros_a[["Fecha", "Valor"]].dropna().copy()
    df_retiros_a["Fecha_dt"] = pd.to_datetime(df_retiros_a["Fecha"], format="%d/%m/%Y", dayfirst=True, errors="coerce")
    df_retiros_a = df_retiros_a.dropna(subset=["Fecha_dt"]).sort_values("Fecha_dt")
    df_retiros_a["Año"] = df_retiros_a["Fecha_dt"].dt.year

df_raw_trans_a = obtener_hoja(hojas_austro, "Transferencias Interbancarias")
df_trans_fechas_a = pd.DataFrame()
df_trans_clean_a = pd.DataFrame()
df_trans_costo_a = pd.DataFrame()

if not df_raw_trans_a.empty and "Fecha" in df_raw_trans_a.columns and "Valor" in df_raw_trans_a.columns:
    df_trans_a_copy = df_raw_trans_a.copy()
    df_trans_a_copy["Fecha_dt"] = pd.to_datetime(df_trans_a_copy["Fecha"], format="%d/%m/%Y", dayfirst=True, errors="coerce")
    df_trans_a_copy["Valor"] = pd.to_numeric(df_trans_a_copy["Valor"], errors="coerce")
    df_trans_a_copy = df_trans_a_copy.dropna(subset=["Fecha_dt", "Valor"]).sort_values("Fecha_dt")
    df_trans_a_copy["Año"] = df_trans_a_copy["Fecha_dt"].dt.year
    df_trans_fechas_a = df_trans_a_copy

    # Excluir registros que contengan 'token' en la columna D o en la fila
    def es_token_row(row):
        if len(row) > 3 and "token" in str(row.iloc[3]).lower():
            return True
        for val in row.values:
            if "token" in str(val).lower():
                return True
        return False

    es_token_mask = df_trans_a_copy.apply(es_token_row, axis=1)
    df_trans_costo_a = df_trans_a_copy[~es_token_mask].copy()

if not df_raw_trans_a.empty and "Institución" in df_raw_trans_a.columns and "Valor" in df_raw_trans_a.columns:
    df_trans_clean_a = df_raw_trans_a[["Institución", "Valor"]].dropna().copy()
    df_trans_clean_a.loc[df_trans_clean_a["Institución"].str.contains("JARDIN AZUAYO|Jardín Azuayo", case=False, na=False), "Institución"] = "Jardin Azuayo"

df_raw_compras_a = obtener_hoja(hojas_austro, "Compras por internet")
def categorizar_descripcion(desc):
    desc_str = str(desc).upper()
    if "AMAZON" in desc_str or "AMZN" in desc_str: return "Amazon"
    elif "ALIEXPRESS" in desc_str or "ALIPAY" in desc_str: return "Aliexpress"
    elif "SHEIN" in desc_str: return "Shein"
    elif "EBAY" in desc_str: return "eBay"
    elif "TEMU" in desc_str: return "Temu"
    elif any(k in desc_str for k in ["TRANSEXPRES", "LAARBOX", "FLETE", "EXPRESSWEB", "TRANS EXPRESS"]): return "Flete Laarbox"
    elif "FARMASOL" in desc_str: return "Farmasol"
    else: return desc_str.strip()

df_compras_a = pd.DataFrame()
if not df_raw_compras_a.empty and "Descripción" in df_raw_compras_a.columns and "Valor" in df_raw_compras_a.columns:
    df_compras_a = df_raw_compras_a.copy()
    df_compras_a["Establecimiento"] = df_compras_a["Descripción"].apply(categorizar_descripcion)
    df_compras_a["Valor"] = pd.to_numeric(df_compras_a["Valor"], errors="coerce")
    df_compras_a = df_compras_a.dropna(subset=["Valor"])
    if "Fecha" in df_compras_a.columns:
        df_compras_a["Fecha_dt"] = pd.to_datetime(df_compras_a["Fecha"], format="%d/%m/%Y", dayfirst=True, errors="coerce")
        df_compras_a = df_compras_a.dropna(subset=["Fecha_dt"])
        df_compras_a["Año"] = df_compras_a["Fecha_dt"].dt.year

df_raw_swift_a = obtener_hoja(hojas_austro, "Swift")
df_swift_a = pd.DataFrame()
if not df_raw_swift_a.empty and "Valor" in df_raw_swift_a.columns:
    df_swift_a = df_raw_swift_a.copy()
    df_swift_a["Valor"] = pd.to_numeric(df_swift_a["Valor"], errors="coerce")
    df_swift_a = df_swift_a.dropna(subset=["Valor"])
    if "Fecha" in df_swift_a.columns:
        df_swift_a["Fecha_dt"] = pd.to_datetime(df_swift_a["Fecha"], format="%d/%m/%Y", dayfirst=True, errors="coerce")
        df_swift_a = df_swift_a.dropna(subset=["Fecha_dt"])
        df_swift_a["Año"] = df_swift_a["Fecha_dt"].dt.year

# --- PROCESAMIENTO JARDÍN AZUAYO ---
df_raw_retiros_j = obtener_hoja(hojas_jardin, "Retiros")
df_retiros_j = pd.DataFrame()
if not df_raw_retiros_j.empty and "Fecha" in df_raw_retiros_j.columns and "Valor" in df_raw_retiros_j.columns:
    df_retiros_j = df_raw_retiros_j[["Fecha", "Valor"]].dropna().copy()
    df_retiros_j["Fecha_dt"] = pd.to_datetime(df_retiros_j["Fecha"], format="%d/%m/%Y", dayfirst=True, errors="coerce")
    df_retiros_j = df_retiros_j.dropna(subset=["Fecha_dt"]).sort_values("Fecha_dt")
    df_retiros_j["Año"] = df_retiros_j["Fecha_dt"].dt.year

df_raw_trans_j = obtener_hoja(hojas_jardin, "Transferencias Interbancarias")
df_trans_fechas_j = pd.DataFrame()
if not df_raw_trans_j.empty and "Fecha" in df_raw_trans_j.columns and "Valor" in df_raw_trans_j.columns:
    df_trans_fechas_j = df_raw_trans_j[["Fecha", "Valor"]].dropna().copy()
    df_trans_fechas_j["Fecha_dt"] = pd.to_datetime(df_trans_fechas_j["Fecha"], format="%d/%m/%Y", dayfirst=True, errors="coerce")
    df_trans_fechas_j = df_trans_fechas_j.dropna(subset=["Fecha_dt"]).sort_values("Fecha_dt")
    df_trans_fechas_j["Año"] = df_trans_fechas_j["Fecha_dt"].dt.year


# Filtro principal en lista desplegable
banco_seleccionado = st.selectbox(
    "Seleccionar Entidad / Vista:",
    ["Banco del Austro", "Jardín Azuayo", "Todos"],
    index=0,
    key="selector_banco_principal",
)

# ==============================================================================
# VISTA: BANCO DEL AUSTRO
# ==============================================================================
if banco_seleccionado == "Banco del Austro":
    if not df_retiros_a.empty:
        ultimo_retiro_row = df_retiros_a.iloc[-1]
        txt_ultimo_retiro = f"{ultimo_retiro_row['Fecha_dt'].strftime('%d/%m/%Y')} — ${ultimo_retiro_row['Valor']:,.2f}"
    else:
        txt_ultimo_retiro = "N/A"

    tabla_anos = (
        df_retiros_a.groupby("Año")["Valor"]
        .agg(N_Retiros="count", Total_USD="sum")
        .reset_index()
        if not df_retiros_a.empty else pd.DataFrame()
    )

    if not tabla_anos.empty:
        tabla_anos["Retiro_Dia"] = tabla_anos["Total_USD"] / 365
        tabla_anos["Año"] = tabla_anos["Año"].astype(str)
        tabla_anos.columns = ["Año", "Nº Retiros", "Total", "Retiro / Día"]
    else:
        tabla_anos = pd.DataFrame(columns=["Año", "Nº Retiros", "Total", "Retiro / Día"])

    if not df_trans_clean_a.empty:
        tabla_trans = (
            df_trans_clean_a.groupby("Institución")["Valor"]
            .agg(N_Trans="count", Total_USD="sum")
            .reset_index()
            .sort_values("Total_USD", ascending=False)
        )
        tabla_trans.columns = ["Entidad Financiera", "Nº Transferencias", "Total Transferido"]
    else:
        tabla_trans = pd.DataFrame(columns=["Entidad Financiera", "Nº Transferencias", "Total Transferido"])

    if not tabla_trans.empty:
        tabla_trans["Entidad Financiera"] = tabla_trans["Entidad Financiera"].apply(dos_lineas_banco)

    if not df_trans_fechas_a.empty:
        ultima_trans_row = df_trans_fechas_a.iloc[-1]
        txt_ultima_trans = f"{ultima_trans_row['Fecha_dt'].strftime('%d/%m/%Y')} — ${ultima_trans_row['Valor']:,.2f}"
        tabla_trans_anos = df_trans_fechas_a.groupby("Año")["Valor"].sum().reset_index()
        tabla_trans_anos["Año"] = tabla_trans_anos["Año"].astype(str)
        tabla_trans_anos.columns = ["Año", "Total Transferido"]
    else:
        txt_ultima_trans = "N/A"
        tabla_trans_anos = pd.DataFrame(columns=["Año", "Total Transferido"])

    if not df_compras_a.empty:
        tabla_compras = (
            df_compras_a.groupby("Establecimiento", as_index=False)["Valor"]
            .agg(N_Compras="count", Total_USD="sum")
            .sort_values("Total_USD", ascending=False)
            .reset_index(drop=True)
        )
        tabla_compras.columns = ["Establecimiento", "Nº Compras", "Total Comprado"]
    else:
        tabla_compras = pd.DataFrame(columns=["Establecimiento", "Nº Compras", "Total Comprado"])

    anos_set_austro = set()
    for df_temp in [df_retiros_a, df_trans_fechas_a, df_compras_a, df_swift_a]:
        if "Año" in df_temp.columns:
            anos_set_austro.update(df_temp["Año"].dropna().unique())

    anos_disponibles_austro = ["Todos"] + [str(int(y)) for y in sorted(anos_set_austro)]

    subtab1, subtab2, subtab3 = st.tabs(
        ["Retiros por Año", "Transferencias Interbancarias", "Compras por Internet"]
    )

    with subtab1:
        st.html(render_custom_table(tabla_anos))
        st.html(render_kpi_card("Último Retiro (Fecha y Valor)", txt_ultimo_retiro))

    with subtab2:
        st.html(render_custom_table(tabla_trans))
        st.html(render_custom_table(tabla_trans_anos))
        st.html(render_kpi_card("Última Transferencia (Fecha y Valor)", txt_ultima_trans))

    with subtab3:
        st.html(render_custom_table(tabla_compras))

    st.markdown("---")
    st.subheader("Indicadores Clave (KPIs) - Banco del Austro")

    filtro_ano_austro = st.selectbox(
        "Filtrar por Año (Austro):",
        anos_disponibles_austro,
        index=0,
        key="filtro_austro",
    )

    if filtro_ano_austro == "Todos":
        total_kpi_retiros = df_retiros_a["Valor"].sum() if not df_retiros_a.empty else 0.0
        if not df_retiros_a.empty:
            min_fecha = df_retiros_a["Fecha_dt"].min()
            max_fecha = df_retiros_a["Fecha_dt"].max()
            dias_totales_rango = (max_fecha - min_fecha).days if pd.notnull(min_fecha) and pd.notnull(max_fecha) else 1
            kpi_retiro_dia = total_kpi_retiros / (dias_totales_rango if dias_totales_rango > 0 else 1)
        else:
            kpi_retiro_dia = 0.0

        total_kpi_trans = df_trans_fechas_a["Valor"].sum() if not df_trans_fechas_a.empty else 0.0
        n_trans_costo_a = len(df_trans_costo_a) if not df_trans_costo_a.empty else 0
        costo_total_trans_a = n_trans_costo_a * 0.41

        if not df_trans_fechas_a.empty:
            min_f_trans = df_trans_fechas_a["Fecha_dt"].min()
            max_f_trans = df_trans_fechas_a["Fecha_dt"].max()
            dias_periodo_trans = (max_f_trans - min_f_trans).days
            anos_periodo_trans = dias_periodo_trans / 365.25
        else:
            anos_periodo_trans = 0.0

        total_kpi_compras = df_compras_a["Valor"].sum() if not df_compras_a.empty else 0.0
        total_kpi_swift = df_swift_a["Valor"].sum() if not df_swift_a.empty else 0.0

        lbl_total_retiros = "Total Retiros (Todos los Años)"
        lbl_retiro_dia = "Retiro / Día (Todos los Años)"
        lbl_trans = "Total Transferencias"
        lbl_costo_trans = "Costo Total Transferencias"
        lbl_compras = "Total Compras por Internet"
        lbl_swift = "Total Swift"
    else:
        ano_sel = int(filtro_ano_austro)
        if not df_retiros_a.empty and "Año" in df_retiros_a.columns:
            df_retiros_f = df_retiros_a[df_retiros_a["Año"] == ano_sel]
            total_kpi_retiros = df_retiros_f["Valor"].sum()
            kpi_retiro_dia = total_kpi_retiros / 365
        else:
            total_kpi_retiros = 0.0
            kpi_retiro_dia = 0.0

        df_trans_fa_sel = df_trans_fechas_a[df_trans_fechas_a["Año"] == ano_sel] if not df_trans_fechas_a.empty and "Año" in df_trans_fechas_a.columns else pd.DataFrame()
        total_kpi_trans = df_trans_fa_sel["Valor"].sum() if not df_trans_fa_sel.empty else 0.0

        if not df_trans_costo_a.empty and "Año" in df_trans_costo_a.columns:
            n_trans_costo_a = len(df_trans_costo_a[df_trans_costo_a["Año"] == ano_sel])
        else:
            n_trans_costo_a = 0
        costo_total_trans_a = n_trans_costo_a * 0.41

        if not df_trans_fa_sel.empty:
            min_f_trans = df_trans_fa_sel["Fecha_dt"].min()
            max_f_trans = df_trans_fa_sel["Fecha_dt"].max()
            dias_periodo_trans = (max_f_trans - min_f_trans).days
            anos_periodo_trans = dias_periodo_trans / 365.25
        else:
            anos_periodo_trans = 0.0

        total_kpi_compras = df_compras_a[df_compras_a["Año"] == ano_sel]["Valor"].sum() if not df_compras_a.empty and "Año" in df_compras_a.columns else 0.0
        total_kpi_swift = df_swift_a[df_swift_a["Año"] == ano_sel]["Valor"].sum() if not df_swift_a.empty and "Año" in df_swift_a.columns else 0.0

        lbl_total_retiros = f"Total Retiros ({filtro_ano_austro})"
        lbl_retiro_dia = f"Retiro / Día ({filtro_ano_austro})"
        lbl_trans = f"Total Transferencias ({filtro_ano_austro})"
        lbl_costo_trans = f"Costo Total Transferencias ({filtro_ano_austro})"
        lbl_compras = f"Total Compras por Internet ({filtro_ano_austro})"
        lbl_swift = f"Total Swift ({filtro_ano_austro})"

    txt_det_costo_trans = f"Nº Transferencias con Costo: {n_trans_costo_a:,} | Período: {anos_periodo_trans:.2f} años"

    col1, col2 = st.columns(2)
    with col1:
        st.html(render_kpi_card(lbl_total_retiros, f"${total_kpi_retiros:,.2f}"))
        st.html(render_kpi_card(lbl_retiro_dia, f"${kpi_retiro_dia:,.2f}"))
        st.html(render_kpi_card(lbl_compras, f"${total_kpi_compras:,.2f}"))
    with col2:
        st.html(render_kpi_card(lbl_trans, f"${total_kpi_trans:,.2f}"))
        st.html(render_kpi_card(lbl_costo_trans, f"${costo_total_trans_a:,.2f}", txt_det_costo_trans))
        st.html(render_kpi_card(lbl_swift, f"${total_kpi_swift:,.2f}"))

# ==============================================================================
# VISTA: JARDÍN AZUAYO
# ==============================================================================
elif banco_seleccionado == "Jardín Azuayo":
    if not df_retiros_j.empty:
        ultimo_retiro_j = df_retiros_j.iloc[-1]
        txt_ultimo_retiro_j = f"{ultimo_retiro_j['Fecha_dt'].strftime('%d/%m/%Y')} — ${ultimo_retiro_j['Valor']:,.2f}"
    else:
        txt_ultimo_retiro_j = "N/A"

    tabla_anos_j = (
        df_retiros_j.groupby("Año")["Valor"]
        .agg(N_Retiros="count", Total_USD="sum")
        .reset_index()
        if not df_retiros_j.empty else pd.DataFrame()
    )

    if not tabla_anos_j.empty:
        tabla_anos_j["Retiro_Dia"] = tabla_anos_j["Total_USD"] / 365
        tabla_anos_j["Año"] = tabla_anos_j["Año"].astype(str)
        tabla_anos_j.columns = ["Año", "Nº Retiros", "Total", "Retiro / Día"]
    else:
        tabla_anos_j = pd.DataFrame(columns=["Año", "Nº Retiros", "Total", "Retiro / Día"])

    if not df_trans_fechas_j.empty:
        ultima_trans_j = df_trans_fechas_j.iloc[-1]
        txt_ultima_trans_j = f"{ultima_trans_j['Fecha_dt'].strftime('%d/%m/%Y')} — ${ultima_trans_j['Valor']:,.2f}"
        tabla_trans_j_anos = (
            df_trans_fechas_j.groupby("Año")["Valor"]
            .agg(N_Trans="count", Total_USD="sum")
            .reset_index()
        )
        tabla_trans_j_anos["Año"] = tabla_trans_j_anos["Año"].astype(str)
        tabla_trans_j_anos.columns = ["Año", "Nº Transferencias", "Total Transferido"]
    else:
        txt_ultima_trans_j = "N/A"
        tabla_trans_j_anos = pd.DataFrame(columns=["Año", "Nº Transferencias", "Total Transferido"])

    anos_set_jardin = set()
    for df_temp in [df_retiros_j, df_trans_fechas_j]:
        if "Año" in df_temp.columns:
            anos_set_jardin.update(df_temp["Año"].dropna().unique())

    anos_disponibles_jardin = ["Todos"] + [str(int(y)) for y in sorted(anos_set_jardin)]

    subtab_j1, subtab_j2 = st.tabs(
        ["Retiros por Año", "Transferencias Interbancarias"]
    )

    with subtab_j1:
        st.html(render_custom_table(tabla_anos_j))
        st.html(render_kpi_card("Último Retiro (Fecha y Valor)", txt_ultimo_retiro_j))

    with subtab_j2:
        st.html(render_custom_table(tabla_trans_j_anos))
        st.html(render_kpi_card("Última Transferencia (Fecha y Valor)", txt_ultima_trans_j))

    st.markdown("---")
    st.subheader("Indicadores Clave (KPIs) - Jardín Azuayo")

    filtro_ano_jardin = st.selectbox(
        "Filtrar por Año (Jardín Azuayo):",
        anos_disponibles_jardin,
        index=0,
        key="filtro_jardin",
    )

    if filtro_ano_jardin == "Todos":
        total_kpi_retiros_j = df_retiros_j["Valor"].sum() if not df_retiros_j.empty else 0.0
        if not df_retiros_j.empty:
            min_fecha_j = df_retiros_j["Fecha_dt"].min()
            max_fecha_j = df_retiros_j["Fecha_dt"].max()
            dias_totales_j = (max_fecha_j - min_fecha_j).days if pd.notnull(min_fecha_j) and pd.notnull(max_fecha_j) else 1
            kpi_retiro_dia_j = total_kpi_retiros_j / (dias_totales_j if dias_totales_j > 0 else 1)
        else:
            kpi_retiro_dia_j = 0.0

        total_kpi_trans_j = df_trans_fechas_j["Valor"].sum() if not df_trans_fechas_j.empty else 0.0

        lbl_total_retiros_j = "Total Retiros (Todos los Años)"
        lbl_retiro_dia_j = "Retiro / Día (Todos los Años)"
        lbl_trans_j = "Total Transferencias"
    else:
        ano_sel_j = int(filtro_ano_jardin)
        if not df_retiros_j.empty and "Año" in df_retiros_j.columns:
            df_retiros_fj = df_retiros_j[df_retiros_j["Año"] == ano_sel_j]
            total_kpi_retiros_j = df_retiros_fj["Valor"].sum()
            kpi_retiro_dia_j = total_kpi_retiros_j / 365
        else:
            total_kpi_retiros_j = 0.0
            kpi_retiro_dia_j = 0.0

        total_kpi_trans_j = df_trans_fechas_j[df_trans_fechas_j["Año"] == ano_sel_j]["Valor"].sum() if not df_trans_fechas_j.empty and "Año" in df_trans_fechas_j.columns else 0.0

        lbl_total_retiros_j = f"Total Retiros ({filtro_ano_jardin})"
        lbl_retiro_dia_j = f"Retiro / Día ({filtro_ano_jardin})"
        lbl_trans_j = f"Total Transferencias ({filtro_ano_jardin})"

    col1_j, col2_j = st.columns(2)
    with col1_j:
        st.html(render_kpi_card(lbl_total_retiros_j, f"${total_kpi_retiros_j:,.2f}"))
        st.html(render_kpi_card(lbl_retiro_dia_j, f"${kpi_retiro_dia_j:,.2f}"))
    with col2_j:
        st.html(render_kpi_card(lbl_trans_j, f"${total_kpi_trans_j:,.2f}"))

# ==============================================================================
# VISTA: TODOS (CONSOLIDADO - SUMA DE AMBOS BANCOS)
# ==============================================================================
else:
    # 1. Retiros Consolidados (Austro + Jardín Azuayo)
    df_retiros_todos = pd.concat([df_retiros_a, df_retiros_j], ignore_index=True) if not (df_retiros_a.empty and df_retiros_j.empty) else pd.DataFrame()

    tabla_anos_todos = (
        df_retiros_todos.groupby("Año")["Valor"]
        .agg(N_Retiros="count", Total_USD="sum")
        .reset_index()
        if not df_retiros_todos.empty else pd.DataFrame()
    )

    if not tabla_anos_todos.empty:
        tabla_anos_todos["Retiro_Dia"] = tabla_anos_todos["Total_USD"] / 365
        tabla_anos_todos["Año"] = tabla_anos_todos["Año"].astype(str)
        tabla_anos_todos.columns = ["Año", "Nº Retiros", "Total", "Retiro / Día"]
    else:
        tabla_anos_todos = pd.DataFrame(columns=["Año", "Nº Retiros", "Total", "Retiro / Día"])

    if not df_retiros_todos.empty:
        df_retiros_todos_sorted = df_retiros_todos.sort_values("Fecha_dt")
        ultimo_retiro_t = df_retiros_todos_sorted.iloc[-1]
        txt_ultimo_retiro_t = f"{ultimo_retiro_t['Fecha_dt'].strftime('%d/%m/%Y')} — ${ultimo_retiro_t['Valor']:,.2f}"
    else:
        txt_ultimo_retiro_t = "N/A"

    # 2. Transferencias Interbancarias Consolidadas (Austro + Jardín Azuayo)
    df_trans_todos = pd.concat([df_trans_fechas_a, df_trans_fechas_j], ignore_index=True) if not (df_trans_fechas_a.empty and df_trans_fechas_j.empty) else pd.DataFrame()

    tabla_trans_todos_anos = (
        df_trans_todos.groupby("Año")["Valor"]
        .agg(N_Trans="count", Total_USD="sum")
        .reset_index()
        if not df_trans_todos.empty else pd.DataFrame()
    )

    if not tabla_trans_todos_anos.empty:
        tabla_trans_todos_anos["Año"] = tabla_trans_todos_anos["Año"].astype(str)
        tabla_trans_todos_anos.columns = ["Año", "Nº Transferencias", "Total Transferido"]
    else:
        tabla_trans_todos_anos = pd.DataFrame(columns=["Año", "Nº Transferencias", "Total Transferido"])

    if not df_trans_todos.empty:
        df_trans_todos_sorted = df_trans_todos.sort_values("Fecha_dt")
        ultima_trans_t = df_trans_todos_sorted.iloc[-1]
        txt_ultima_trans_t = f"{ultima_trans_t['Fecha_dt'].strftime('%d/%m/%Y')} — ${ultima_trans_t['Valor']:,.2f}"
    else:
        txt_ultima_trans_t = "N/A"

    anos_set_todos = set()
    for df_temp in [df_retiros_todos, df_trans_todos, df_compras_a, df_swift_a]:
        if "Año" in df_temp.columns:
            anos_set_todos.update(df_temp["Año"].dropna().unique())

    anos_disponibles_todos = ["Todos"] + [str(int(y)) for y in sorted(anos_set_todos)]

    subtab_t1, subtab_t2 = st.tabs(
        ["Retiros por Año (Consolidado)", "Transferencias Interbancarias (Consolidado)"]
    )

    with subtab_t1:
        st.html(render_custom_table(tabla_anos_todos))
        st.html(render_kpi_card("Último Retiro Consolidado (Fecha y Valor)", txt_ultimo_retiro_t))

    with subtab_t2:
        st.html(render_custom_table(tabla_trans_todos_anos))
        st.html(render_kpi_card("Última Transferencia Consolidada (Fecha y Valor)", txt_ultima_trans_t))

    st.markdown("---")
    st.subheader("Indicadores Clave (KPIs) - Consolidado (Ambas Entidades)")

    filtro_ano_todos = st.selectbox(
        "Filtrar por Año (Consolidado):",
        anos_disponibles_todos,
        index=0,
        key="filtro_todos",
    )

    if filtro_ano_todos == "Todos":
        total_retiros_a_f = df_retiros_a["Valor"].sum() if not df_retiros_a.empty else 0.0
        total_retiros_j_f = df_retiros_j["Valor"].sum() if not df_retiros_j.empty else 0.0
        total_kpi_retiros_t = total_retiros_a_f + total_retiros_j_f

        if not df_retiros_a.empty:
            min_a = df_retiros_a["Fecha_dt"].min()
            max_a = df_retiros_a["Fecha_dt"].max()
            dias_a = (max_a - min_a).days if pd.notnull(min_a) and pd.notnull(max_a) else 1
            kpi_retiro_dia_a = total_retiros_a_f / (dias_a if dias_a > 0 else 1)
        else:
            kpi_retiro_dia_a = 0.0

        if not df_retiros_j.empty:
            min_j = df_retiros_j["Fecha_dt"].min()
            max_j = df_retiros_j["Fecha_dt"].max()
            dias_j = (max_j - min_j).days if pd.notnull(min_j) and pd.notnull(max_j) else 1
            kpi_retiro_dia_j = total_retiros_j_f / (dias_j if dias_j > 0 else 1)
        else:
            kpi_retiro_dia_j = 0.0

        if not df_retiros_todos.empty:
            min_fecha_t = df_retiros_todos["Fecha_dt"].min()
            max_fecha_t = df_retiros_todos["Fecha_dt"].max()
            dias_totales_t = (max_fecha_t - min_fecha_t).days if pd.notnull(min_fecha_t) and pd.notnull(max_fecha_t) else 1
            kpi_retiro_dia_t = total_kpi_retiros_t / (dias_totales_t if dias_totales_t > 0 else 1)
        else:
            kpi_retiro_dia_t = 0.0

        total_trans_a_f = df_trans_fechas_a["Valor"].sum() if not df_trans_fechas_a.empty else 0.0
        total_trans_j_f = df_trans_fechas_j["Valor"].sum() if not df_trans_fechas_j.empty else 0.0
        total_kpi_trans_t = total_trans_a_f + total_trans_j_f

        total_kpi_compras_t = df_compras_a["Valor"].sum() if not df_compras_a.empty else 0.0
        total_kpi_swift_t = df_swift_a["Valor"].sum() if not df_swift_a.empty else 0.0

        lbl_total_retiros_t = "Total Retiros Consolidados (Todos los Años)"
        lbl_retiro_dia_t = "Retiro / Día Consolidado (Todos los Años)"
        lbl_trans_t = "Total Transferencias Consolidadas"
        lbl_compras_t = "Total Compras por Internet"
        lbl_swift_t = "Total Swift"
    else:
        ano_sel_t = int(filtro_ano_todos)

        df_retiros_fa = df_retiros_a[df_retiros_a["Año"] == ano_sel_t] if (not df_retiros_a.empty and "Año" in df_retiros_a.columns) else pd.DataFrame()
        total_retiros_a_f = df_retiros_fa["Valor"].sum() if not df_retiros_fa.empty else 0.0
        kpi_retiro_dia_a = total_retiros_a_f / 365

        df_retiros_fj = df_retiros_j[df_retiros_j["Año"] == ano_sel_t] if (not df_retiros_j.empty and "Año" in df_retiros_j.columns) else pd.DataFrame()
        total_retiros_j_f = df_retiros_fj["Valor"].sum() if not df_retiros_fj.empty else 0.0
        kpi_retiro_dia_j = total_retiros_j_f / 365

        total_kpi_retiros_t = total_retiros_a_f + total_retiros_j_f
        kpi_retiro_dia_t = total_kpi_retiros_t / 365

        df_trans_fa = df_trans_fechas_a[df_trans_fechas_a["Año"] == ano_sel_t] if (not df_trans_fechas_a.empty and "Año" in df_trans_fechas_a.columns) else pd.DataFrame()
        total_trans_a_f = df_trans_fa["Valor"].sum() if not df_trans_fa.empty else 0.0

        df_trans_fj = df_trans_fechas_j[df_trans_fechas_j["Año"] == ano_sel_t] if (not df_trans_fechas_j.empty and "Año" in df_trans_fechas_j.columns) else pd.DataFrame()
        total_trans_j_f = df_trans_fj["Valor"].sum() if not df_trans_fj.empty else 0.0

        total_kpi_trans_t = total_trans_a_f + total_trans_j_f

        total_kpi_compras_t = df_compras_a[df_compras_a["Año"] == ano_sel_t]["Valor"].sum() if not df_compras_a.empty and "Año" in df_compras_a.columns else 0.0
        total_kpi_swift_t = df_swift_a[df_swift_a["Año"] == ano_sel_t]["Valor"].sum() if not df_swift_a.empty and "Año" in df_swift_a.columns else 0.0

        lbl_total_retiros_t = f"Total Retiros Consolidados ({filtro_ano_todos})"
        lbl_retiro_dia_t = f"Retiro / Día Consolidado ({filtro_ano_todos})"
        lbl_trans_t = f"Total Transferencias Consolidadas ({filtro_ano_todos})"
        lbl_compras_t = f"Total Compras por Internet ({filtro_ano_todos})"
        lbl_swift_t = f"Total Swift ({filtro_ano_todos})"

    txt_det_total_retiros = f"Austro: ${total_retiros_a_f:,.2f} | Jardín: ${total_retiros_j_f:,.2f}"
    txt_det_retiro_dia = f"Austro: ${kpi_retiro_dia_a:,.2f} | Jardín: ${kpi_retiro_dia_j:,.2f}"
    txt_det_trans = f"Austro: ${total_trans_a_f:,.2f} | Jardín: ${total_trans_j_f:,.2f}"

    col1_t, col2_t = st.columns(2)

    with col1_t:
        st.html(render_kpi_card(lbl_total_retiros_t, f"${total_kpi_retiros_t:,.2f}", txt_det_total_retiros))
        st.html(render_kpi_card(lbl_retiro_dia_t, f"${kpi_retiro_dia_t:,.2f}", txt_det_retiro_dia))
        st.html(render_kpi_card(lbl_compras_t, f"${total_kpi_compras_t:,.2f}"))

    with col2_t:
        st.html(render_kpi_card(lbl_trans_t, f"${total_kpi_trans_t:,.2f}", txt_det_trans))
        st.html(render_kpi_card(lbl_swift_t, f"${total_kpi_swift_t:,.2f}"))

if __name__ == "__main__":
    if "streamlit" not in sys.argv[0]:
        os.system(f'streamlit run "{__file__}" --server.port 8501')