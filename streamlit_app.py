import streamlit as st
import PyPDF2
import pandas as pd
import tempfile
import os

st.set_page_config(page_title="Analizador de PDFs", layout="centered")
st.title("📄 Analizador de PDFs Confidenciales")

st.markdown("Sube uno o más archivos PDF para analizar si contienen las frases 'en sentido POSITIVO' o 'en sentido NEGATIVO'. También se extraerá la frase 'Revisión practicada el día...'")

# Subir archivos
archivos_subidos = st.file_uploader("Selecciona los archivos PDF", type=["pdf"], accept_multiple_files=True)

if archivos_subidos:
    resultados = []

    for archivo in archivos_subidos:
        # Guardar archivo temporalmente
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(archivo.read())
            ruta_pdf = tmp.name

        # Leer PDF
        with open(ruta_pdf, 'rb') as f:
            lector = PyPDF2.PdfReader(f)
            texto_completo = ""
            for pagina in lector.pages:
                texto = pagina.extract_text()
                if texto:
                    texto_completo += texto.lower()

        # Revisar frases clave
        positivo = "en sentido positivo" in texto_completo
        negativo = "en sentido negativo" in texto_completo

        # Buscar frase de revisión
        texto_revision = ""
        clave_revision = "revisión practicada el día"
        if clave_revision in texto_completo:
            i = texto_completo.find(clave_revision)
            texto_revision = texto_completo[i:i+len(clave_revision)+30].strip()

        resultados.append({
            "Archivo": archivo.name,
            "Sentido POSITIVO": "Sí" if positivo else "No",
            "Sentido NEGATIVO": "Sí" if negativo else "No",
            "Texto Revisión": texto_revision
        })

        os.unlink(ruta_pdf)  # Borrar archivo temporal

    # Mostrar resultados
    df = pd.DataFrame(resultados)
    st.dataframe(df)

    # Descargar como Excel
    output = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    df.to_excel(output.name, index=False)
    with open(output.name, "rb") as f:
        st.download_button(
            label="📄 Descargar resumen en Excel",
            data=f.read(),
            file_name="resultado_revision.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
