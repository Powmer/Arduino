import tkinter as tk
from tkinter import messagebox
import serial
import time
# ---------- Variáveis Globais ----------
arduino = None
modo_selecionado = None
cooldown = None
COOLDOWN_TIME = 5
radiobuttons = []
sequencia = []

md = "None"
nm = "None"

modo_temperatura = {
    "Açai": -10,
    "Sorvete": -20,
    "Bebidas": 5,
    "None": 0
}
# ---------- Funções ----------
def verificar_conexao_arduino():
    global arduino
    if arduino is not None and arduino.is_open:
        messagebox.showinfo("Conexão", "Arduino já conectado")
        return
    try:
        arduino = serial.Serial('COM3', 9600, timeout=1)
        time.sleep(2)
        messagebox.showinfo("Conexão", "Dispositivo Conectado")
    except serial.SerialException:
        messagebox.showerror("Erro", "Nenhum dispositivo conectado")

def enviar_para_arduino(valor):
    if arduino is None or not arduino.is_open and len(sequencia):
        return "Erro: Nenhuma conexão com o Arduino."
    try:
        arduino.write((valor + "\n").encode())
        start_time = time.time()
        while time.time() - start_time < 2:
            if arduino.in_waiting:
                resposta = arduino.readline().decode().strip()
                return resposta if resposta else "Sem resposta do Arduino"
        return "Sem resposta do Arduino"
    except Exception as e:
        return f"Erro: {e}"

def processar_sequencia():
    if sequencia:
        item = sequencia.pop(0)
        resposta = enviar_para_arduino(item)
        lbl_status.config(text=f"Enviado: {item} | Arduino: {resposta}")
        janela.after(500, processar_sequencia)

def trocar_modo(novo_modo):
    global md, nm, cooldown, modo_selecionado

    agora = time.time()
    if cooldown is not None:
        tempo_restante = COOLDOWN_TIME - int(agora - cooldown)
        if tempo_restante > 0:
            messagebox.showwarning("Cooldown", f"Tente novamente em {tempo_restante} segundos.")
            return

    nm = novo_modo
    modo_selecionado.set(nm)
    cooldown = agora

    dif = modo_temperatura[nm] - modo_temperatura[md]

    sequencia.clear()
    if dif > 0:
        sequencia.extend(["mais"] * dif)
    elif dif < 0:
        sequencia.extend(["menos"] * (-dif))

    processar_sequencia()
    md = nm

    for rb in radiobuttons:
        rb.config(state=tk.DISABLED)
    janela.after(COOLDOWN_TIME * 1000, lambda: [rb.config(state=tk.NORMAL) for rb in radiobuttons])

def checar_atividade():
    if modo_selecionado.get() == "":
        messagebox.showwarning("Modo", "Selecione um modo")
        return
    resposta = enviar_para_arduino(modo_selecionado.get())
    lbl_status.config(text=f"Arduino: {resposta}")

def reativar_modos():
    for rb in radiobuttons:
        rb.config(state=tk.NORMAL)
    modo_selecionado.set("None")
    lbl_status.config(text="Status: Nenhum modo selecionado")

def ler_temperatura():
    if arduino is not None and arduino.is_open:
        try:
            if arduino.in_waiting > 0:
                linha = arduino.readline().decode().strip()
                if linha:
                    lbl_arduino.config(text=f"Temperatura: {linha} °C")
        except:
            pass
    janela.after(1000, ler_temperatura)

def editar_configuracoes():
    def salvar():
        modo = entry_modo.get().strip()
        temp = entry_temp.get().strip()
        if not modo or not temp:
            messagebox.showwarning("Erro", "Preencha ambos os campos")
            return
        try:
            temp_val = int(temp)
            modo_temperatura[modo] = temp_val
            messagebox.showinfo("Sucesso", f"Modo '{modo}' salvo com {temp_val}°C")
            janela_edit.destroy()
            atualizar_radiobuttons()
        except:
            messagebox.showerror("Erro", "Temperatura inválida")

    janela_edit = tk.Toplevel(janela)
    janela_edit.title("Configurações")
    janela_edit.geometry("300x150")

    tk.Label(janela_edit, text="Nome do Modo:").pack(pady=5)
    entry_modo = tk.Entry(janela_edit)
    entry_modo.pack(pady=5)

    tk.Label(janela_edit, text="Temperatura:").pack(pady=5)
    entry_temp = tk.Entry(janela_edit)
    entry_temp.pack(pady=5)

    tk.Button(janela_edit, text="Salvar", command=salvar).pack(pady=10)

def atualizar_radiobuttons():
    global radiobuttons
    for rb in radiobuttons:
        rb.destroy()
    radiobuttons.clear()
    for modo in modo_temperatura.keys():
        if modo == "None":
            continue
        rb = tk.Radiobutton(main_widget, text=modo, font=("Arial", 9, "bold"),
                            variable=modo_selecionado, value=modo,
                            command=lambda m=modo: trocar_modo(m))
        rb.pack(pady=5)
        radiobuttons.append(rb)
# ---------- Frame Principal ----------
janela = tk.Tk()
janela.title("Controle Arduino")
janela.geometry("500x600")

modo_selecionado = tk.StringVar(value="None")

main_widget = tk.Frame(janela)
main_widget.pack(pady=20)

atualizar_radiobuttons()

tk.Button(main_widget, text="Verificar Conexão",
          font=("Arial", 12, "bold"), width=25,
          command=verificar_conexao_arduino).pack(pady=10)

tk.Button(main_widget, text="Temperatura Produtos",
          font=("Arial", 12, "bold"), width=25,
          command=checar_atividade).pack(pady=10)

tk.Button(main_widget, text="Reiniciar Modos",
          font=("Arial", 12, "bold"), width=25,
          command=reativar_modos).pack(pady=10)

tk.Button(main_widget, text="Configurações",
          font=("Arial", 12, "bold"), width=25,
          command=editar_configuracoes).pack(pady=10)

lbl_status = tk.Label(janela, text="Status: Nenhum modo selecionado", font=("Arial", 8, "bold"))
lbl_status.pack(pady=20)

lbl_arduino = tk.Label(janela, text="Temperatura: -- °C", font=("Arial", 10, "bold"))
lbl_arduino.pack(pady=20)

ler_temperatura()
janela.mainloop()
