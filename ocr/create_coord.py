# -*- coding: utf-8 -*-

import pytesseract
from PIL import Image
import csv

# Ruta de la imagen generada
image_path = 'pagina_1.png'  # Cambia esto para cada p?gina

# Cargar la imagen con PIL
imagen = Image.open(image_path)

# Realizar el OCR para obtener las coordenadas de las palabras
datos = pytesseract.image_to_data(imagen, lang='spa', output_type=pytesseract.Output.DICT)

# Abrir un archivo CSV para guardar los resultados
with open('coordenadas_palabras.csv', mode='w', newline='', encoding='utf-8') as archivo_csv:
    writer = csv.writer(archivo_csv)
    
    # Escribir el encabezado del CSV
    writer.writerow(['char', 'char_x_center', 'char_y_center', 'char_xmax', 'char_xmin',
                     'char_ymax', 'char_ymin', 'trial_id', 'assigned_line'])
    
    # ID del trial (puedes modificarlo seg?n sea necesario)
    trial_id = 1
    
    # Lista para asignar l?neas
    lineas = []
    line_number = 1
    
    # Escribir las coordenadas de cada palabra en el CSV
    for i in range(len(datos['text'])):
        palabra = datos['text'][i]
        if palabra.strip():  # Solo mostrar palabras no vac?as
            x_min = datos['left'][i]
            y_min = datos['top'][i]
            ancho = datos['width'][i]
            alto = datos['height'][i]
            x_max = x_min + ancho
            y_max = y_min + alto
            x_center = x_min + (ancho / 2)
            y_center = y_min + (alto / 2)
            
            # Determinar la l?nea asignada
            asignada = False
            for j, ref_y in enumerate(lineas):
                if abs(y_center - ref_y) <= 150:
                    assigned_line = j + 1
                    asignada = True
                    break
            
            if not asignada:
                lineas.append(y_center)
                assigned_line = len(lineas)
            
            writer.writerow([palabra, x_center, y_center, x_max, x_min, y_max, y_min, trial_id, assigned_line])

print("Coordenadas guardadas en 'coordenadas_palabras.csv'")
