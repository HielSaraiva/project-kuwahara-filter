import serial
import serial.tools.list_ports

# Lista as portas disponíveis
ports = list(serial.tools.list_ports.comports())
print("Portas disponíveis:")
for i, port in enumerate(ports):
    print(f"{i}: {port.device}")

idx = int(input("Digite o número da porta serial: "))
port_name = ports[idx].device

ser = serial.Serial(port_name, baudrate=38400, timeout=None)

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
            # Critério: 3 linhas de cabeçalho (P2, dimensões, maxval) + 90 linhas de pixels
            if len(pgm_lines) >= 3 + 90:
                # Verifica se tem 8100 valores nas linhas de pixels (linhas 3 a 92, índices 3 em diante)
                pixel_count = sum(len(l.split()) for l in pgm_lines[3:])

                print(
                    f"   Linhas capturadas: {len(pgm_lines)}, Pixels: {pixel_count}")

                if pixel_count >= 8100:
                    # Salva apenas as 93 primeiras linhas (3 cabeçalho + 90 pixels)
                    with open(f"saida_{imagem_num}.pgm", "w") as f:
                        f.writelines(pgm_lines[:93])
                    print(
                        f"Imagem {imagem_num} salva em 'saida_{imagem_num}.pgm'!")
                    imagem_num += 1
                    capturando = False
                elif len(pgm_lines) > 100:
                    # Se passou de 100 linhas e ainda não tem 8100 pixels, algo está errado
                    print(
                        f"Imagem {imagem_num} descartada: pixels incorretos ({pixel_count}/8100)")
                    imagem_num += 1
                    capturando = False
except KeyboardInterrupt:
    print("\nLeitura interrompida pelo usuário.")

ser.close()
print("Finalizado.")
