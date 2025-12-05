import tkinter as tk
from tkinter import messagebox
import serial
import time
import threading

# ---------- VARIÁVEIS GLOBAIS ----------
arduino = None
modo_selecionado = None
cooldown = None
COOLDOWN_TIME = 0.3
radiobuttons = []
sequencia = []

md = "None"  
nm = "None" 
modo_simulacao = False
temperatura_atual = 0  

modo_temperatura = {
    "Açai": -10,
    "Sorvete": -20,
    "Bebidas": 5,
    "Torta": 10,
    "None": 0
}

atualizando_sequencia = False 

# ---------- FUNÇÕES ----------
def verificar_conexao_arduino():
    global arduino
    try:
        arduino = serial.Serial('COM6', 9600, timeout=1)
        time.sleep(2)
        messagebox.showinfo("Conexão", "Arduino Conectado")
        iniciar_leitura_thread()
    except:
        messagebox.showerror("Erro", "Nenhum dispositivo conectado")

# ---------- ENVIO ----------
def enviar_para_arduino(valor):
    if arduino is None or not arduino.is_open:
        return
    try:
        arduino.write((valor + "\n").encode())
    except:
        pass

# ---------- PROCESSAR SEQUÊNCIA ----------
def processar_sequencia():
    global md, atualizando_sequencia, temperatura_atual
    if sequencia:
        atualizando_sequencia = True
        item = sequencia.pop(0)
        enviar_para_arduino(item)
        janela.after(350, processar_sequencia)
    else:
     
        temperatura_atual = modo_temperatura.get(nm, 0)
        lbl_arduino.config(text=f"Temperatura: {temperatura_atual} °C")
        md = nm 
        atualizando_sequencia = False

# ---------- TROCAR MODO ----------
def trocar_modo(novo_modo):
    global nm, cooldown, sequencia

    agora = time.time()
    if cooldown is not None and agora - cooldown < COOLDOWN_TIME:
        return

    nm = novo_modo
    modo_selecionado.set(nm)
    cooldown = agora

   
    dif = modo_temperatura[nm] - temperatura_atual

    sequencia.clear()
    if dif > 0:
        sequencia.extend(["mais"] * dif)
    elif dif < 0:
        sequencia.extend(["menos"] * abs(dif))

    processar_sequencia()

# ---------- LEITURA EM TEMPO REAL (THREAD) ----------
def iniciar_leitura_thread():
    thread = threading.Thread(target=ler_dados_arduino, daemon=True)
    thread.start()

def ler_dados_arduino():
    global arduino
    while True:
        if arduino and arduino.is_open:
            try:
                linha = arduino.readline().decode().strip()
                if linha in ["MAIS", "MENOS"]:
                    janela.after(0, lambda: lbl_status.config(
                        text=f"Status: Servo executou {linha}"
                    ))
            except:
                pass
        time.sleep(0.05)

# ---------- RESET ----------
def reativar_modos():
    global md, nm, temperatura_atual, atualizando_sequencia
    modo_selecionado.set("None")
    md = "None"
    nm = "None"
    temperatura_atual = 0
    atualizando_sequencia = False
    lbl_status.config(text="Status: Resetado")
    lbl_arduino.config(text="Temperatura: -- °C")

# ---------- CONFIGURAÇÕES ----------
def editar_configuracoes():
    def salvar():
        modo = entry_modo.get().strip()
        temp = entry_temp.get().strip()
        try:
            modo_temperatura[modo] = int(temp)
            atualizar_radiobuttons()
            janela_edit.destroy()
        except:
            messagebox.showerror("Erro", "Dados inválidos")

    janela_edit = tk.Toplevel(janela)
    janela_edit.title("Configurações")

    tk.Label(janela_edit, text="Modo").pack()
    entry_modo = tk.Entry(janela_edit)
    entry_modo.pack()

    tk.Label(janela_edit, text="Temperatura").pack()
    entry_temp = tk.Entry(janela_edit)
    entry_temp.pack()

    tk.Button(janela_edit, text="Salvar", command=salvar).pack(pady=10)

# ---------- ATUALIZAR BOTÕES ----------
def atualizar_radiobuttons():
    global radiobuttons
    for rb in radiobuttons:
        rb.destroy()
    radiobuttons.clear()

    for modo, temp in modo_temperatura.items():
        if modo == "None":
            continue
        texto = f"{modo} ({temp}°C)"
        rb = tk.Radiobutton(
            main_widget,
            text=texto,
            variable=modo_selecionado,
            value=modo,
            command=lambda m=modo: trocar_modo(m)
        )
        rb.pack(pady=5)
        radiobuttons.append(rb)

# ---------- SIMULADOR ----------
def abrir_simulador():
    global temperatura_atual

    def mudar(valor):
        global temperatura_atual
        temperatura_atual += valor
        lbl_arduino.config(text=f"Temperatura: {temperatura_atual} °C")

    sim = tk.Toplevel(janela)
    sim.title("Simulação de Temperatura")
    sim.geometry("250x280")

    tk.Label(sim, text="Simulação de Sensor", font=("Arial", 12, "bold")).pack(pady=10)

    tk.Button(sim, text="+1 °C", width=15, command=lambda: mudar(1)).pack(pady=5)
    tk.Button(sim, text="-1 °C", width=15, command=lambda: mudar(-1)).pack(pady=5)
    tk.Button(sim, text="+5 °C", width=15, command=lambda: mudar(5)).pack(pady=5)
    tk.Button(sim, text="-5 °C", width=15, command=lambda: mudar(-5)).pack(pady=5)

# ---------- SIMULAÇÃO ON/OFF ----------
def alternar_simulacao():
    global modo_simulacao
    modo_simulacao = not modo_simulacao
    if modo_simulacao:
        lbl_status.config(text="Status: MODO SIMULAÇÃO ATIVADO")
        lbl_arduino.config(text=f"Temperatura: {temperatura_atual} °C")
    else:
        lbl_status.config(text="Status: MODO REAL ATIVADO")

# ---------- INTERFACE ----------
janela = tk.Tk()
janela.title("Controle Arduino")
janela.geometry("450x650")

modo_selecionado = tk.StringVar(value="None")

main_widget = tk.Frame(janela)
main_widget.pack(pady=20)

atualizar_radiobuttons()

tk.Button(main_widget, text="Verificar Conexão", width=25,
          command=verificar_conexao_arduino).pack(pady=10)


tk.Button(main_widget, text="Configurações", width=25,
          command=editar_configuracoes).pack(pady=10)

tk.Button(main_widget, text="Simulador de Temperatura", width=25,
          command=abrir_simulador).pack(pady=10)

tk.Button(main_widget, text="Ativar / Desativar Simulação", width=25,
          command=alternar_simulacao).pack(pady=10)

lbl_status = tk.Label(janela, text="Status: Modo real ativo")
lbl_status.pack(pady=20)

lbl_arduino = tk.Label(janela, text="Temperatura: -- °C")
lbl_arduino.pack(pady=10)

janela.mainloop()
