import fitz  # PyMuPDF
import hashlib
import tkinter as tk
from tkinter import filedialog

def es_pagina_casi_blanca(pagina, tolerancia=0.97): #tolerancia maneja que tan vacia debe estar la pagina para borrarla

    pix = pagina.get_pixmap(matrix=fitz.Matrix(0.1, 0.1), colorspace=fitz.csGRAY)
    
    muestras = pix.samples
    total_pixeles = len(muestras)

    pixeles_blancos = sum(1 for p in muestras if p > 240)
    
    proporcion_blanco = pixeles_blancos / total_pixeles
    
    return proporcion_blanco >= tolerancia

def limpiar_pdf():
    root = tk.Tk()
    root.withdraw() 
    
    print("Please select a file...")
    input_pdf = filedialog.askopenfilename(
        title="Select PDF",
        filetypes=[("Archivos PDF", "*.pdf")]
    )
    
    if not input_pdf:
        print("No file selected.")
        return

    output_pdf = input_pdf.replace(".pdf", " (Clean).pdf")
    
    try:
        doc = fitz.open(input_pdf)
        hashes_vistos = set()
        indices_a_eliminar = []
        
        blancas_cont = 0
        duplicadas_cont = 0
        total_paginas = len(doc)

        print("-" * 50)
        print(f"Starting analysis of {total_paginas} pages...")
        print("-" * 50)

        for num_pag in range(total_paginas):
            pagina = doc[num_pag]
            
            prefijo = f"[Page {num_pag + 1}/{total_paginas}]"

            # 1. Detección de "Casi Blancas" con tolerancia a manchas
            if es_pagina_casi_blanca(pagina):
                indices_a_eliminar.append(num_pag)
                blancas_cont += 1
                print(f"{prefijo} -> Blank")
                continue

            # 2. Detección de Duplicados
            texto = pagina.get_text().strip().encode("utf-8")
            
            if not texto:
                pix = pagina.get_pixmap(matrix=fitz.Matrix(0.1, 0.1)) 
                hash_actual = hashlib.md5(pix.samples).hexdigest()
            else:
                hash_actual = hashlib.md5(texto).hexdigest()

            if hash_actual in hashes_vistos:
                indices_a_eliminar.append(num_pag)
                duplicadas_cont += 1
                print(f"{prefijo} -> Repeated")
            else:
                hashes_vistos.add(hash_actual)
                print(f"{prefijo} -> Unique")

        print("-" * 50)
        print("Analysis completed! Saving File...")

        if indices_a_eliminar:
            for indice in sorted(indices_a_eliminar, reverse=True):
                doc.delete_page(indice)
            
            doc.save(output_pdf, garbage=4, deflate=True)
            
            print(f"\nDone!")
            print(f"{len(indices_a_eliminar)} pages deleted:")
            print(f"- {duplicadas_cont} duplicates")
            print(f"- {blancas_cont} blank")
            print(f"\nFile saved as:\n{output_pdf}")
        else:
            print("\nNo duplicated or blank pages found.")

        doc.close()

    except Exception as e:
        print(f"\nERROR: Something happened: {e}")

if __name__ == "__main__":
    limpiar_pdf()
    print("\n" + "=" * 50)
    input("Press ENTER to close window...")
