# -*- coding: utf-8 -*-

from pdf2image import convert_from_path

# Ruta al archivo PDF
pdf_path = 'text.pdf'

# Ruta a la carpeta donde est� instalado Poppler (modifica seg�n tu sistema)
poppler_path = r'C:\Program Files\poppler-24.08.0\Library\bin'  # Cambia esto por la ruta correcta

# Convertir el PDF a im�genes (una imagen por cada p�gina)
imagenes = convert_from_path(pdf_path, 300, poppler_path=poppler_path)

# Guardar las im�genes resultantes
for i, imagen in enumerate(imagenes):
    imagen.save(f'pagina_{i + 1}.png', 'PNG')
