import tkinter as tk
from tkinter import messagebox
import serial
import time

# ---------- Variáveis Globais ----------
arduino = None
modo_selecionado = None
cooldown = None
COOLDOWN_TIME = 0  # segundos
radiobuttons = []  # lista para armazenar os radiobuttons

# ---------- Funções ----------
def verificar_conexao_arduino():
    global arduino
    try:
        arduino = serial.Serial('COM3', 9600, timeout=1)
        time.sleep(2)  # espera Arduino resetar
        messagebox.showinfo("Conexão", "Dispositivo Conectado")
    except serial.SerialException:
        messagebox.showerror("Erro", "Nenhum dispositivo conectado")

def enviar_para_arduino(valor):
    if arduino is None or not arduino.is_open:
        return "Erro: Nenhuma conexão com o Arduino."
    try:
        arduino.write((valor + "\n").encode())
        resposta = arduino.readline().decode().strip()
        return resposta if resposta else "Sem resposta do Arduino"
    except Exception as e:
        return f"Erro: {e}"

def trocar_modo(nm):
    global cooldown, modo_selecionado

    agora = time.time()
    if cooldown is not None:
        tempo_restante = COOLDOWN_TIME - int(agora - cooldown)
        if tempo_restante > 0:
            messagebox.showwarning(
                "Cooldown",
                f"Tente novamente em {tempo_restante} segundos."
            )
            return

    modo_selecionado.set(nm)
    cooldown = agora
    resposta = enviar_para_arduino(nm)
    lbl_status.config(text=f"Modo: {nm} | Arduino: {resposta}")

    # Desabilitar todos os Radiobuttons após seleção
    for rb in radiobuttons:
        rb.config(state=tk.DISABLED)

def checar_atividade():
    if modo_selecionado.get() == "":
        messagebox.showwarning("Modo", "Selecione um modo")
        return
    resposta = enviar_para_arduino(modo_selecionado.get())
    lbl_status.config(text=f"Arduino: {resposta}")

def reativar_modos():
    # Reativar todos os Radiobuttons (se quiser uma função para reativar)
    for rb in radiobuttons:
        rb.config(state=tk.NORMAL)
    modo_selecionado.set("None")
    lbl_status.config(text="Status: Nenhum modo selecionado")

# ---------- Interface ----------
janela = tk.Tk()
janela.title("Controle Arduino")
janela.geometry("500x450")

modo_selecionado = tk.StringVar(value="None")  # valor inicial vazio

# ---------- Frame Principal ----------
main_widget = tk.Frame(janela)
main_widget.pack(pady=20)


# Radiobuttons (armazenando referências)
rb1 = tk.Radiobutton(main_widget, text="Açai", font=("Arial", 9, "bold"),
                     variable=modo_selecionado, value="Açai",
                     command=lambda: trocar_modo("Açai"))
rb1.pack(pady=5)

rb2 = tk.Radiobutton(main_widget, text="Sorvete", font=("Arial", 9, "bold"),
                     variable=modo_selecionado, value="Sorvete",
                     command=lambda: trocar_modo("Sorvete"))
rb2.pack(pady=5)

rb3 = tk.Radiobutton(main_widget, text="Bebidas", font=("Arial", 9, "bold"),
                     variable=modo_selecionado, value="Bebidas",
                     command=lambda: trocar_modo("Bebidas"))
rb3.pack(pady=5)

# Adicionando à lista de radiobuttons
radiobuttons = [rb1, rb2, rb3]

# ---------- Botões dentro do Main Widget ----------
tk.Button(main_widget, text="Temperatura Produtos",
          font=("Arial", 12, "bold"), width=20,
          command=checar_atividade).pack(pady=10)

tk.Button(main_widget, text="Verificar Conexão",
          font=("Arial", 12, "bold"), width=20,
          command=verificar_conexao_arduino).pack(pady=10)

# Botão para reativar modos (opcional)
tk.Button(main_widget, text="Reiniciar Modos",
          font=("Arial", 12, "bold"), width=20,
          command=reativar_modos).pack(pady=10)

# Label de status
lbl_status = tk.Label(janela, text="Status: Nenhum modo selecionado", font=("Arial", 8, "bold"))
lbl_status.pack(pady=20)

lbl_arduino = tk.Label(janela, text="Temperatura: -- °C", font=("Arial", 10, "bold"))
lbl_arduino.pack(pady=20)

def ler_temperatura():
    if arduino is not None and arduino.is_open:
        try:
            linha = arduino.readline().decode().strip()
            if linha:
                lbl_arduino.config(text=f"Temperatura: {linha} °C")
        except:
            pass
    janela.after(1000, ler_temperatura)

# inicia leitura automática
ler_temperatura()

janela.mainloop()

