sequencia = []
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
    sequencia.append("mais")
def app_menos():
    sequencia.append("menos")

alterar_temp(md,nm)
print(sequencia)
#TIRA_OFORCOOWHILEPLS
while len(sequencia) >0:
    for "mais" in(sequencia):
        sequencia.pop()
        print(sequencia)
    for "menos" in(sequencia):
        sequencia.pop()
        print(sequencia)


# encaixa isso no arduino
#void loop() {
#  if (Serial.available() > 0) {
#    String comando = Serial.readStringUntil('\n');
#    comando.trim(); 
#  if (comando == "mais"){Serial.println("Recebi MAIS");}
# faz o mesmo com menos
