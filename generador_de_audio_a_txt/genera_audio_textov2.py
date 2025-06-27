#!/usr/bin/env python3
"""
Interfaz gráfica para generar transcripciones TXT usando Whisper,
con soporte para procesamiento por lotes.
"""
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import whisper
import threading
import os
from pathlib import Path


def generate_txt(audio_path: str, output_dir: str, model_size: str = "base") -> str:
    """
    Transcribe el audio y guarda la transcripción en un archivo TXT.
    """
    model = whisper.load_model(model_size)
    result = model.transcribe(audio_path)

    # Generar archivo TXT con el mismo nombre que el audio
    audio_name = Path(audio_path).stem
    txt_path = os.path.join(output_dir, f"{audio_name}.txt")
    
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(result["text"].strip())

    return txt_path


def process_files(audio_files, output_dir, progress_callback=None):
    success_count = 0
    errors = []
    
    for i, audio_path in enumerate(audio_files, 1):
        try:
            txt_path = generate_txt(audio_path, output_dir)
            success_count += 1
        except Exception as e:
            errors.append(f"{os.path.basename(audio_path)}: {str(e)}")
        
        if progress_callback:
            progress_callback(i, len(audio_files), errors)
    
    return success_count, errors


def start_generation():
    audio_paths = listbox_audio.get(0, tk.END)
    output_dir = entry_output.get()
    
    if not audio_paths:
        messagebox.showwarning("Atención", "Por favor, selecciona al menos un archivo de audio.")
        return
    
    if not output_dir:
        messagebox.showwarning("Atención", "Por favor, selecciona la carpeta de destino.")
        return

    btn_generate.config(state=tk.DISABLED)
    btn_add_audio.config(state=tk.DISABLED)
    btn_clear.config(state=tk.DISABLED)
    progress_bar['value'] = 0
    label_status.config(text="Procesando archivos...")
    progress_label.config(text="0/0")

    def update_progress(current, total, errors=None):
        progress = (current / total) * 100
        progress_bar['value'] = progress
        progress_label.config(text=f"{current}/{total}")
        if current == total:
            btn_generate.config(state=tk.NORMAL)
            btn_add_audio.config(state=tk.NORMAL)
            btn_clear.config(state=tk.NORMAL)
            
            if errors:
                error_msg = f"Proceso completado con {len(errors)} errores.\n\nErrores:\n" + "\n".join(errors)
                messagebox.showwarning("Proceso completado con errores", error_msg)
            else:
                messagebox.showinfo("Éxito", f"Se procesaron {total} archivos correctamente.")
            label_status.config(text=f"Procesados {total} archivos")

    def task():
        try:
            success_count, errors = process_files(audio_paths, output_dir, update_progress)
        except Exception as e:
            messagebox.showerror("Error crítico", f"Ocurrió un error inesperado:\n{str(e)}")
            label_status.config(text="Error durante el procesamiento")
        finally:
            btn_generate.config(state=tk.NORMAL)
            btn_add_audio.config(state=tk.NORMAL)
            btn_clear.config(state=tk.NORMAL)

    threading.Thread(target=task, daemon=True).start()


def add_audio_files():
    files = filedialog.askopenfilenames(
        filetypes=[("Archivos de audio", "*.mp3 *.wav *.m4a *.ogg *.flac *.opus")]
    )
    if files:
        listbox_audio.delete(0, tk.END)
        for file in files:
            listbox_audio.insert(tk.END, file)
        label_status.config(text=f"{len(files)} archivos cargados")


def clear_files():
    listbox_audio.delete(0, tk.END)
    label_status.config(text="Listo")


# --- Interfaz Tkinter ---
root = tk.Tk()
root.title("Generador TXT con Whisper - Procesamiento por lotes")
root.geometry("650x400")

# Frame principal
main_frame = tk.Frame(root, padx=10, pady=10)
main_frame.pack(fill=tk.BOTH, expand=True)

# Lista de archivos de audio
lbl_audio = tk.Label(main_frame, text="Archivos de audio:")
lbl_audio.pack(anchor="w")

listbox_frame = tk.Frame(main_frame)
listbox_frame.pack(fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(listbox_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

listbox_audio = tk.Listbox(
    listbox_frame, 
    yscrollcommand=scrollbar.set,
    selectmode=tk.EXTENDED,
    height=6
)
listbox_audio.pack(fill=tk.BOTH, expand=True)
scrollbar.config(command=listbox_audio.yview)

# Botones para archivos
button_frame = tk.Frame(main_frame)
button_frame.pack(fill=tk.X, pady=5)

btn_add_audio = tk.Button(
    button_frame, 
    text="Añadir archivos...",
    command=add_audio_files
)
btn_add_audio.pack(side=tk.LEFT, padx=2)

btn_clear = tk.Button(
    button_frame, 
    text="Limpiar lista",
    command=clear_files
)
btn_clear.pack(side=tk.LEFT, padx=2)

# Carpeta de destino
lbl_output = tk.Label(main_frame, text="Carpeta de destino:")
lbl_output.pack(anchor="w", pady=(10,0))

output_frame = tk.Frame(main_frame)
output_frame.pack(fill=tk.X)

entry_output = tk.Entry(output_frame)
entry_output.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))

btn_browse_output = tk.Button(
    output_frame, 
    text="Examinar...",
    command=lambda: (entry_output.delete(0, tk.END), entry_output.insert(0, filedialog.askdirectory()))
)
btn_browse_output.pack(side=tk.LEFT)

# Barra de progreso
progress_frame = tk.Frame(main_frame)
progress_frame.pack(fill=tk.X, pady=(15,5))

progress_label = tk.Label(progress_frame, text="0/0")
progress_label.pack(side=tk.RIGHT)

progress_bar = ttk.Progressbar(
    progress_frame, 
    orient=tk.HORIZONTAL, 
    length=100, 
    mode='determinate'
)
progress_bar.pack(fill=tk.X, expand=True)

# Botón de generar
btn_generate = tk.Button(
    main_frame, 
    text="Generar TXT para todos los archivos", 
    command=start_generation
)
btn_generate.pack(pady=10)

# Estado
label_status = tk.Label(main_frame, text="Listo")
label_status.pack()

root.mainloop()