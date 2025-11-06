import serial
import serial.tools.list_ports

# Lista as portas disponíveis
ports = list(serial.tools.list_ports.comports())
print("Portas disponíveis:")
for i, port in enumerate(ports):
    print(f"{i}: {port.device}")

idx = int(input("Digite o número da porta serial: "))
port_name = ports[idx].device

ser = serial.Serial(port_name, baudrate=38400, timeout=2)

print("Aguardando início da imagem (P2)...")
pgm_lines = []
capturando = False
imagem_num = 1

try:
    while True:
        line = ser.readline().decode("utf-8", errors="ignore")
        if line.strip() == "P2":
            pgm_lines = [line]
            capturando = True
            print(f"\nIniciando captura da imagem {imagem_num}...")
        elif capturando:
            pgm_lines.append(line)
            # Critério: 4 linhas de cabeçalho + 90 linhas de pixels
            if len(pgm_lines) == 3 + 90:
                # Verifica se tem 8100 valores
                pixel_count = sum(len(l.split()) for l in pgm_lines[4:])
                if pixel_count == 8100:
                    with open(f"saida_{imagem_num}.pgm", "w") as f:
                        f.writelines(pgm_lines)
                    print(f"Imagem {imagem_num} salva!")
                else:
                    print(
                        f"Imagem {imagem_num} ignorada: quantidade de pixels ({pixel_count}) incorreta!")
                imagem_num += 1
                capturando = False
except KeyboardInterrupt:
    print("\nLeitura interrompida pelo usuário.")

ser.close()
print("Finalizado.")
