import serial
import time

sequencia = []
md = -15
nm = -20
###botarVariaveis da interface
arduino = serial.Serial('COM4', 9600) 
time.sleep(2) 
def alterar_temp(md, nm):
    dif = nm - md
    if dif < 0:
        for i in range(-dif):
            app_menos()
    else:
        for i in range(dif):
            app_mais()

def app_mais():
    sequencia.append("mais")

def app_menos():
    sequencia.append("menos")

alterar_temp(md, nm)

while len(sequencia) > 0:
    item = sequencia.pop(0)
    arduino.write((item + "\n").encode())
    print("Enviado:", item)
    time.sleep(0.5)

#------------#
void setup() {
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    String comando = Serial.readStringUntil('\n');
    comando.trim();
    if (comando == "mais") {
      Serial.println("MAIS");
    } else if (comando == "menos") {
      Serial.println("MENOS");
    }
  }
}
