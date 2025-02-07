# -*- coding: utf-8 -*-

from pdf2image import convert_from_path

# Ruta al archivo PDF
pdf_path = 'text.pdf'

# Ruta a la carpeta donde está instalado Poppler (modifica según tu sistema)
poppler_path = r'C:\Program Files\poppler-24.08.0\Library\bin'  # Cambia esto por la ruta correcta

# Convertir el PDF a imágenes (una imagen por cada página)
imagenes = convert_from_path(pdf_path, 300, poppler_path=poppler_path)

# Guardar las imágenes resultantes
for i, imagen in enumerate(imagenes):
    imagen.save(f'pagina_{i + 1}.png', 'PNG')
