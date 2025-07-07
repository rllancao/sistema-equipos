import streamlit as st
from fpdf import FPDF
from datetime import datetime
import tempfile
import os

# --- Clase PDF personalizada ---
class PDF(FPDF):
    def header(self):
        """
        Define la cabecera del documento PDF.
        Añade un logo en la esquina superior izquierda y un título centrado.
        """
        # Añadir logo en la esquina superior izquierda, si el archivo existe.
        # NOTA: El archivo 'Logo.png' debe estar en la misma carpeta que el script.
        logo_path = 'Logo.png'
        if os.path.exists(logo_path):
            # Coordenadas x, y, y ancho de la imagen. La altura se ajusta automáticamente.
            self.image(logo_path, x=10, y=8, w=40)
        
        # Mover la posición del cursor para el título para que no se superponga.
        self.set_y(15)
        
        # Título del documento.
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Ficha de Traslado de Equipamiento', 0, 1, 'C')
        
        # Salto de línea para empezar el contenido principal.
        self.ln(15)

    def chapter_title(self, title):
        """
        Añade un título de capítulo/sección.
        """
        
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(4)

    def create_table_section(self, title, data):
        """
        Crea una sección con formato de tabla a partir de un diccionario.
        """
        if title:
            self.chapter_title(title)
        
        # Ancho de las columnas
        key_width = 100
        value_width = self.w - self.l_margin - self.r_margin - key_width
        
        # Altura de línea base
        line_height = 8

        self.set_font('Arial', '', 11)
        
        for key, value in data.items():
            # Guarda la posición del cursor
            x = self.get_x()
            y = self.get_y()

            # Dibuja la celda de la clave (con borde)
            self.set_font('Arial', 'B', 11)
            self.multi_cell(key_width, line_height, f'{key}:', border=1, align='L')

            # Mueve el cursor a la derecha para la celda del valor
            self.set_xy(x + key_width, y)
            
            # Dibuja la celda del valor (con borde)
            self.set_font('Arial', '', 11)
            self.multi_cell(value_width, line_height, str(value), border=1, align='L')
            
        self.ln(5) # Espacio después de la tabla


    def add_side_by_side_images(self, title1, image_file1, title2, image_file2):
        """
        Añade dos imágenes una al lado de la otra con sus títulos.
        """
        if not image_file1 and not image_file2:
            return

        page_width = self.w - self.l_margin - self.r_margin
        col_width = (page_width / 2) - 5
        
        y_before_titles = self.get_y()
        
        temp_paths = {}
        if image_file1:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_image:
                temp_image.write(image_file1.getvalue())
                temp_paths[1] = temp_image.name
        if image_file2:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_image:
                temp_image.write(image_file2.getvalue())
                temp_paths[2] = temp_image.name
        
        self.set_font('Arial', 'B', 11)
        if temp_paths.get(1):
            self.cell(col_width, 10, title1, 0, 0, 'C')
        
        self.set_xy(self.l_margin + col_width + 10, y_before_titles)
        
        if temp_paths.get(2):
            self.cell(col_width, 10, title2, 0, 0, 'C')
            
        self.ln(12)
        
        y_for_images = self.get_y()
        
        if temp_paths.get(1):
            self.image(temp_paths[1], x=self.l_margin, y=y_for_images, w=col_width)
        if temp_paths.get(2):
            self.image(temp_paths[2], x=self.l_margin + col_width + 10, y=y_for_images, w=col_width)
            
        self.ln(65)

        for path in temp_paths.values():
            os.remove(path)


    def add_single_image_section(self, title, image_file):
        """
        Añade una sola imagen centrada con un título.
        """
        if image_file:
            self.chapter_title(title)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_image:
                temp_image.write(image_file.getvalue())
                temp_image_path = temp_image.name
            
            self.image(temp_image_path, w=80, x=self.w/2 - 40)
            self.ln(50)
            os.remove(temp_image_path)

def generate_pdf(data):
    """
    Función principal para generar el documento PDF completo.
    """
    pdf = PDF()
    pdf.add_page()
    
    # --- Sección Equipo ---
    equipo_data = {
        "Nombre del Equipo": data["nombre_equipo"],
        "Marca": data["marca"],
        "Modelo": data["modelo"],
        "N° de serie": data["n_serie"],
        "Accesorios incluidos": data["accesorios"]
    }
    pdf.create_table_section('EQUIPO', equipo_data)

    # --- Imágenes (Lado a Lado) ---
    pdf.add_side_by_side_images(
        'Fotografía del Equipo', data["foto_equipo"],
        'Fotografía del Embalaje', data["foto_embalaje"]
    )

    # --- Sección Datos del Traslado ---
    pdf.chapter_title('DATOS DEL TRASLADO')

    # Centro de origen
    origen_data = {
        "Sede": data["sede_origen"],
        "Sala": data["sala_origen"],
        "N° de piso": data["piso_origen"],
        "Fecha traslado": data["fecha_traslado"],
        "Motivo del traslado": data["motivo_traslado"],
        "Responsable que autoriza el traslado": data["responsable_autoriza"]
    }
    pdf.create_table_section("1. Centro de origen", origen_data)
    
    # Centro de destino
    destino_data = {
        "Sede": data["sede_destino"],
        "Sala": data["sala_destino"],
        "N° de piso": data["piso_destino"],
        "Fecha de recepción": data["fecha_recepcion"],
        "Responsable que recibirá el equipo": data["responsable_recibe"]
    }
    pdf.create_table_section("2. Centro de destino", destino_data)

    # Datos del transporte
    transporte_data = {
        "Medio de transporte": data["medio_transporte"],
        "Empresa/ persona encargada del traslado": data["empresa_transporte"],
        "Patente del vehículo si aplica": data["patente"],
        "Hora de salida y estimada de llegada": data["horas_transporte"]
    }
    pdf.create_table_section("3. Datos del transporte", transporte_data)
    
    # Observaciones
    observaciones_data = {
        "Observaciones sobre embalaje": data["obs_embalaje"]
    }
    pdf.create_table_section("4. Observaciones", observaciones_data)

    # Voucher (una sola imagen)
    pdf.add_single_image_section('Foto del Voucher del transporte', data["foto_voucher"])
    
    # --- Firma ---
    if pdf.get_y() > 220: # Añadir nueva página si no hay espacio para la firma
        pdf.add_page()
    pdf.ln(20)
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 10, data["responsable_origen_firma"], 0, 1, 'C')
    pdf.cell(0, 10, "____________________________________", 0, 1, 'C')
    pdf.cell(0, 10, "Nombre y Rut del responsable del centro de origen", 0, 1, 'C')

    # Guarda el PDF en un stream de bytes
    pdf_output = pdf.output(dest='S').encode('latin-1')
    return pdf_output

# --- Interfaz de Streamlit (sin cambios) ---
st.title("Generador de Informes de Traslado 📄")

st.header("Datos del Equipo")
nombre_equipo = st.text_input("Nombre del Equipo", value="Monitor de presin arterial digital")
marca = st.text_input("Marca", value="Omron")
modelo = st.text_input("Modelo", value="M3")
n_serie = st.text_input("N° de serie")
accesorios = st.text_area("Accesorios incluidos", value="Incluye manguito.")

col1, col2 = st.columns(2)
with col1:
    foto_equipo = st.file_uploader("Fotografía del Equipo", type=['png', 'jpg', 'jpeg'])
with col2:
    foto_embalaje = st.file_uploader("Fotografía del Embalaje", type=['png', 'jpg', 'jpeg'])

st.markdown("---")

st.header("DATOS DEL TRASLADO")

st.subheader("1. Centro de origen")
sede_origen = st.text_input("Sede (Origen)", value="Santiago")
sala_origen = st.text_input("Sala (Origen)")
piso_origen = st.text_input("N° de piso (Origen)", value="6")
fecha_traslado = st.date_input("Fecha traslado", value=datetime.strptime("26-06-2025", "%d-%m-%Y"))
motivo_traslado = st.text_area("Motivo del traslado", value="Se envia equipo ya que monitor hemodinámico esta presentando fallas. Y Cardiomedics debe enviar back up.")
responsable_autoriza = st.text_input("Responsable que autoriza el traslado", value="Paulina Aedo")

st.subheader("2. Centro de destino")
sede_destino = st.text_input("Sede (Destino)", value="Rancagua")
sala_destino = st.text_input("Sala (Destino)")
piso_destino = st.text_input("N° de piso (Destino)")
fecha_recepcion = st.date_input("Fecha de recepción", value=datetime.strptime("26-06-2025", "%d-%m-%Y"))
responsable_recibe = st.text_input("Responsable que recibirá el equipo", value="Leonardo Bez")

st.subheader("3. Datos del transporte")
medio_transporte = st.text_input("Medio de transporte", value="terrestre")
empresa_transporte = st.text_input("Empresa/ persona encargada del traslado", value="Soserval")
patente = st.text_input("Patente del vehículo si aplica", value="variable")
horas_transporte = st.text_input("Hora de salida y estimada de llegada", value="variable")

st.subheader("4. Observaciones")
obs_embalaje = st.text_area("Observaciones sobre embalaje", value="Fragil")
foto_voucher = st.file_uploader("Foto del Voucher del transporte", type=['png', 'jpg', 'jpeg'])

st.markdown("---")

st.header("Firma")
responsable_origen_firma = st.text_input("Nombre y Rut del responsable del centro de origen", value="Paulina Aedo Muñoz 17.877.873-0")

if st.button("Generar Informe PDF 🚀"):
    # Recopilar todos los datos
    form_data = {
        "nombre_equipo": nombre_equipo,
        "marca": marca,
        "modelo": modelo,
        "n_serie": n_serie,
        "accesorios": accesorios,
        "foto_equipo": foto_equipo,
        "foto_embalaje": foto_embalaje,
        "sede_origen": sede_origen,
        "sala_origen": sala_origen,
        "piso_origen": piso_origen,
        "fecha_traslado": fecha_traslado.strftime("%d-%m-%Y"),
        "motivo_traslado": motivo_traslado,
        "responsable_autoriza": responsable_autoriza,
        "sede_destino": sede_destino,
        "sala_destino": sala_destino,
        "piso_destino": piso_destino,
        "fecha_recepcion": fecha_recepcion.strftime("%d-%m-%Y"),
        "responsable_recibe": responsable_recibe,
        "medio_transporte": medio_transporte,
        "empresa_transporte": empresa_transporte,
        "patente": patente,
        "horas_transporte": horas_transporte,
        "obs_embalaje": obs_embalaje,
        "foto_voucher": foto_voucher,
        "responsable_origen_firma": responsable_origen_firma
    }
    
    pdf_bytes = generate_pdf(form_data)
    
    st.success("¡Informe PDF generado con éxito!")
    
    st.download_button(
        label="Descargar PDF",
        data=pdf_bytes,
        file_name=f"Ficha_Traslado_{nombre_equipo.replace(' ', '_')}.pdf",
        mime="application/pdf"
    )
