#!/usr/bin/env python3
import os
import re
import tkinter as tk
from tkinter import messagebox


def ruta_escritorio():
    home = os.path.expanduser("~")
    for nombre in ("Desktop", "Escritorio"):
        ruta = os.path.join(home, nombre)
        if os.path.isdir(ruta):
            return ruta
    return home


def extraer_url(texto):
    # Primero la URL del src de un <img>, si no hay, el primer href
    m = re.search(r'<img[^>]+src="([^"]+)"', texto)
    if m:
        return m.group(1)
    m = re.search(r'href="(https?://[^"]+)"', texto)
    return m.group(1) if m else None


def limpiar_url(url):
    # Quita parámetros de tamaño existentes (/w640-h480/, /s320/, /s320-c/)
    url = re.sub(r'/[wW][0-9]+(-[hH][0-9]+)?/', '/', url)
    url = re.sub(r'/s[0-9]+(-c)?/', '/', url)
    return url


def url_con_tamano(url_limpia, tamano):
    # Inserta el tamaño antes del nombre del archivo
    return re.sub(r'/([^/]+)$', rf'/{tamano}/\1', url_limpia)


def generar_html(url_original, descripcion):
    base = limpiar_url(url_original)
    s1600 = url_con_tamano(base, "s1600")
    s400 = url_con_tamano(base, "s400")
    s736 = url_con_tamano(base, "s736")
    s980 = url_con_tamano(base, "s980")
    return f'''<div class="separator" style="clear: both; text-align: center;">
  <a href="{s1600}" style="margin-left: 1em; margin-right: 1em;">
    <img
      alt="{descripcion}"
      title="{descripcion}"
      src="{s1600}"
      srcset="
        {s400} 400w,
        {s736} 736w,
        {s980} 980w"
      sizes="(max-width: 400px) 100vw,
             (max-width: 736px) 100vw,
             980px"
      style="display:block; width:100%; height:auto; object-fit:cover;" />
  </a>
</div>'''


class Portador(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Portador")
        self.geometry("420x170")
        self.resizable(False, False)

        tk.Label(self, text="Texto descriptivo para la imagen:").pack(
            anchor="w", padx=15, pady=(15, 5))
        self.entrada = tk.Entry(self)
        self.entrada.pack(fill="x", padx=15)
        self.entrada.focus()
        self.entrada.bind("<Return>", lambda e: self.procesar())

        tk.Button(self, text="Generar y copiar", command=self.procesar).pack(
            pady=12)

        self.estado = tk.Label(self, text="", wraplength=390, justify="left")
        self.estado.pack(padx=15)

    def procesar(self):
        try:
            contenido = self.clipboard_get()
        except tk.TclError:
            contenido = ""

        if not contenido.strip():
            messagebox.showerror(
                "Error",
                "No se encontró contenido en el portapapeles.\n"
                "Copiá primero la imagen o el código HTML en Blogger.")
            return

        url = extraer_url(contenido)
        if not url:
            messagebox.showerror(
                "Error",
                "No se pudo detectar ninguna imagen válida de Blogger "
                "en el texto copiado.")
            return

        descripcion = self.entrada.get().strip() or "Imagen de portada"
        html = generar_html(url, descripcion)

        salida = os.path.join(ruta_escritorio(), "portada.txt")
        with open(salida, "w", encoding="utf-8") as f:
            f.write(html + "\n")

        self.clipboard_clear()
        self.clipboard_append(html)
        self.update()

        self.estado.config(
            text=f"¡Listo! Guardado en {salida} y copiado al portapapeles. "
                 "Pegalo en Blogger antes de cerrar esta ventana.")


if __name__ == "__main__":
    Portador().mainloop()
