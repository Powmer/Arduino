barco = []
md=-15
nm=-20
def alterar_temp(md,nm):
    dif = -1*(md - nm)
    print(dif)
    if dif<0:
        for i in range(-1*(dif)):
            app_menos()
    else:
        for i in range(dif):
            app_mais()


def app_mais():
    barco.append("mais")
def app_menos():
    barco.append("menos")0
alterar_temp(md,nm)
print(barco)

while barco.len() >0:
    for "mais" in(barco):
        digital.write(90)
        barco.pop()
        print(barco)
    for "menos" in(barco):
        digital.write(90)
        barco.pop()
        print(barco)
# encaixa isso no arduino
#void loop() {
#  if (Serial.available() > 0) {
#    String comando = Serial.readStringUntil('\n');
#    comando.trim(); 
#  if (comando == "mais"){Serial.println("Recebi MAIS");}
# faz o mesmo com menos
