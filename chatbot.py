import tkinter as tk
from tkinter import messagebox
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage

# Función para actualizar el historial en la interfaz
def actualizar_historial(pregunta, respuesta):
    historial.config(state=tk.NORMAL)
    historial.insert(tk.END, f"Pregunta: {pregunta}\n")
    historial.insert(tk.END, f"Respuesta: {respuesta}\n")
    historial.insert(tk.END, "-" * 50 + "\n")
    historial.config(state=tk.DISABLED)  # Para que el historial sea solo lectura
    historial.see(tk.END)  # Desplazarse al final automáticamente

# Función para obtener la respuesta
def obtener_respuesta():
    try:
        # Leer la API key
        with open('apikeycash.txt', 'r') as f:
            api_key = f.read().strip()
        
        # Crear el modelo
        chat = ChatOpenAI(openai_api_key=api_key)
        
        # Obtener el contenido de la entrada
        pregunta = entrada.get("1.0", tk.END).strip()
        
        if not pregunta:
            messagebox.showerror("Error", "Por favor, ingresa una pregunta.")
            return
        
        # Llamar al modelo
        resultado = chat.invoke([HumanMessage(content=pregunta)])
        respuesta = resultado.content
        
        # Mostrar la respuesta en el área de salida
        salida.delete("1.0", tk.END)
        salida.insert(tk.END, respuesta)
        
        # Actualizar el historial
        actualizar_historial(pregunta, respuesta)
    
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un problema: {e}")

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Asistente de Preguntas")
ventana.geometry("600x500")

# Etiqueta de entrada
etiqueta_entrada = tk.Label(ventana, text="Hazme una pregunta:", font=("Arial", 12))
etiqueta_entrada.pack(pady=10)

# Área de entrada
entrada = tk.Text(ventana, height=5, width=60, font=("Arial", 12))
entrada.pack(pady=10)

# Botón para enviar
boton_enviar = tk.Button(ventana, text="Enviar", command=obtener_respuesta, font=("Arial", 12))
boton_enviar.pack(pady=10)

# Etiqueta de salida
etiqueta_salida = tk.Label(ventana, text="Respuesta:", font=("Arial", 12))
etiqueta_salida.pack(pady=10)

# Área de salida
salida = tk.Text(ventana, height=5, width=60, font=("Arial", 12))
salida.pack(pady=10)

# Etiqueta de historial
etiqueta_historial = tk.Label(ventana, text="Historial de Conversación:", font=("Arial", 12))
etiqueta_historial.pack(pady=10)

# Área de historial
historial = tk.Text(ventana, height=10, width=60, font=("Arial", 12), state=tk.DISABLED)
historial.pack(pady=10)

# Ejecutar la ventana principal
ventana.mainloop()
