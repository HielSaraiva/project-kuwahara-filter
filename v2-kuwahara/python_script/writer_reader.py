#!/usr/bin/env python3
"""
Script para enviar imagem PGM para STM32 via UART em duas fases.

Fase 1: Envia linhas 0-45 (primeiras 46 linhas) → STM32 processa 0-44
Fase 2: Envia linhas 44-89 (últimas 46 linhas) → STM32 processa 45-89

Overlap: Linha 44 é reenviada na FASE 2 para permitir que o filtro
         processe a linha 45 (que precisa ler linha 44 e 46)

Autor: Copilot Assistant
"""

import serial
import serial.tools.list_ports
import time
import sys
import os


def list_serial_ports():
    """Lista todas as portas seriais disponíveis."""
    ports = serial.tools.list_ports.comports()
    if not ports:
        print("Nenhuma porta serial encontrada!")
        return None

    print("\n=== Portas Seriais Disponíveis ===")
    for i, port in enumerate(ports):
        print(f"{i}: {port.device} - {port.description}")

    return ports


def select_port(ports):
    """Permite ao usuário selecionar uma porta serial."""
    if len(ports) == 1:
        print(f"\nUsando porta padrão: {ports[0].device}")
        return ports[0].device

    while True:
        try:
            choice = int(input("\nEscolha o número da porta: "))
            if 0 <= choice < len(ports):
                return ports[choice].device
            else:
                print("Número inválido!")
        except ValueError:
            print("Digite um número válido!")


def read_pgm_file(filepath):
    """
    Lê um arquivo PGM P2 (ASCII) e retorna os dados da imagem.

    Returns:
        tuple: (width, height, max_value, image_data)
        image_data é uma lista de listas [linha][coluna]
    """
    try:
        with open(filepath, 'r') as f:
            # Pula comentários e lê o cabeçalho
            lines = []
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    lines.append(line)

            # Verifica formato P2
            if lines[0] != 'P2':
                raise ValueError("Arquivo não é PGM P2 (ASCII)")

            # Lê dimensões
            dims = lines[1].split()
            width = int(dims[0])
            height = int(dims[1])
            max_value = int(lines[2])

            # Lê dados da imagem
            # CORREÇÃO: pixels podem estar espalhados em múltiplas linhas
            image_data = []
            data_lines = lines[3:]

            # Concatena todas as linhas de dados e divide em pixels
            all_pixels = []
            for line_str in data_lines:
                all_pixels.extend([int(p) for p in line_str.split()])

            # Verifica se temos exatamente width × height pixels
            expected_pixels = width * height
            if len(all_pixels) != expected_pixels:
                raise ValueError(
                    f"Número incorreto de pixels: {len(all_pixels)} != {expected_pixels}")

            # Divide em linhas de 'width' pixels cada
            for i in range(height):
                start_idx = i * width
                end_idx = start_idx + width
                image_data.append(all_pixels[start_idx:end_idx])

            print(
                f"\n✓ Arquivo PGM carregado: {width}x{height}, max_value={max_value}")
            return width, height, max_value, image_data

    except FileNotFoundError:
        print(f"ERRO: Arquivo não encontrado: {filepath}")
        sys.exit(1)
    except Exception as e:
        print(f"ERRO ao ler PGM: {e}")
        sys.exit(1)


def send_lines(ser, image_data, start_line, end_line):
    """
    Envia linhas da imagem via serial.

    Args:
        ser: Objeto serial
        image_data: Lista de listas com pixels
        start_line: Linha inicial (inclusive)
        end_line: Linha final (inclusive)
    """
    num_lines = end_line - start_line + 1
    print(f"\nEnviando linhas {start_line}-{end_line} ({num_lines} linhas)...")

    for i in range(start_line, end_line + 1):
        line = image_data[i]
        line_str = ' '.join(str(p) for p in line) + '\n'
        ser.write(line_str.encode('ascii'))

        # Feedback visual a cada 10 linhas
        if (i - start_line + 1) % 10 == 0 or i == end_line:
            print(
                f"  Enviadas {i - start_line + 1}/{num_lines} linhas", end='\r')

    print()  # Nova linha após o progresso
    ser.flush()
    print("✓ Envio concluído")


def capture_filtered_lines(ser, expected_lines, phase_name):
    """
    Captura linhas filtradas que o STM32 está enviando via UART.

    Args:
        ser: Objeto serial
        expected_lines: Número de linhas esperadas
        phase_name: Nome da fase (para mensagens)

    Returns:
        list: Lista de strings com as linhas capturadas, ou None se erro
    """
    print(f"\n{'='*50}")
    print(f"CAPTURANDO RESULTADO DA {phase_name}")
    print(f"{'='*50}")

    lines_captured = []
    timeout_time = time.time() + 20  # 20 segundos timeout (margem de segurança)

    print(f"Aguardando {expected_lines} linhas filtradas...")

    while time.time() < timeout_time:
        if ser.in_waiting > 0:
            line = ser.readline().decode('ascii', errors='ignore').strip()

            if not line:
                continue

            # Pula linhas de erro/debug
            if line.startswith('ERROR'):
                print(f"  ⚠ STM32: {line}")
                continue

            # Captura linha de dados
            lines_captured.append(line)

            # Feedback a cada 10 linhas
            if len(lines_captured) % 10 == 0:
                print(
                    f"  Linha {len(lines_captured)}/{expected_lines} capturada", end='\r')

            # Verifica se capturou todas
            if len(lines_captured) >= expected_lines:
                print(f"\n✓ Todas as {expected_lines} linhas capturadas!")
                return lines_captured

    print(
        f"\n✗ Timeout! Capturadas apenas {len(lines_captured)}/{expected_lines} linhas")
    return None


def capture_pgm_header(ser):
    """
    Captura o cabeçalho PGM (P2, dimensões, max_value).

    Returns:
        dict: {'width': int, 'height': int, 'max_val': int} ou None
    """
    print("\nAguardando cabeçalho P2...")

    timeout_time = time.time() + 10
    header_found = False
    width = 0
    height = 0
    max_val = 0

    while time.time() < timeout_time:
        if ser.in_waiting > 0:
            line = ser.readline().decode('ascii', errors='ignore').strip()

            if not line:
                continue

            # Detecta P2
            if line == 'P2' and not header_found:
                print("✓ Cabeçalho P2 detectado!")
                header_found = True
                continue

            # Lê dimensões
            if header_found and width == 0:
                parts = line.split()
                if len(parts) == 2:
                    width = int(parts[0])
                    height = int(parts[1])
                    print(f"✓ Dimensões: {width}x{height}")
                continue

            # Lê max_value
            if header_found and max_val == 0 and width > 0:
                max_val = int(line)
                print(f"✓ Max value: {max_val}")
                return {'width': width, 'height': height, 'max_val': max_val}

    print("✗ Timeout ao aguardar cabeçalho!")
    return None


def save_pgm_file(image_dict, output_path):
    """
    Salva imagem capturada como arquivo PGM.

    Args:
        image_dict: Dicionário com width, height, max_val, data
        output_path: Caminho do arquivo de saída
    """
    try:
        with open(output_path, 'w') as f:
            f.write('P2\n')
            f.write(f"{image_dict['width']} {image_dict['height']}\n")
            f.write(f"{image_dict['max_val']}\n")
            for line in image_dict['data']:
                f.write(line + '\n')

        print(f"\n✓ Imagem salva em: {output_path}")
        return True
    except Exception as e:
        print(f"\n✗ Erro ao salvar arquivo: {e}")
        return False


def main():
    """Função principal."""
    # Verifica argumentos
    if len(sys.argv) < 2:
        print("Uso: python3 writer_reader.py <caminho_para_imagem.pgm>")
        print("\nExemplo:")
        print(
            "  python3 writer_reader.py ../../v1-kuwahara/imgs_original/mona_lisa.ascii.pgm")
        sys.exit(1)

    pgm_file = sys.argv[1]

    # Verifica se arquivo existe
    if not os.path.exists(pgm_file):
        print(f"ERRO: Arquivo não encontrado: {pgm_file}")
        sys.exit(1)

    # Lê a imagem PGM
    width, height, max_value, image_data = read_pgm_file(pgm_file)

    # Verifica dimensões (deve ser 90x90 para este projeto)
    EXPECTED_SIZE = 90
    BUFFER_SIZE = 46

    if width != EXPECTED_SIZE or height != EXPECTED_SIZE:
        print(
            f"AVISO: Tamanho esperado {EXPECTED_SIZE}x{EXPECTED_SIZE}, recebido {width}x{height}")
        response = input("Continuar mesmo assim? (s/n): ")
        if response.lower() != 's':
            sys.exit(0)

    # Seleciona porta serial
    ports = list_serial_ports()
    if not ports:
        sys.exit(1)

    port = select_port(ports)

    # Abre conexão serial
    try:
        print(f"\n=== Conectando em {port} (38400 baud) ===")
        ser = serial.Serial(
            port=port,
            baudrate=38400,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1
        )
        time.sleep(2)  # Aguarda estabilização
        print("✓ Conexão estabelecida\n")

        # FASE 1: Envia linhas 0-45 (primeiras 46 linhas)
        print("=" * 50)
        print("FASE 1: Enviando primeiras 46 linhas (0-45)")
        print("        STM32 processará linhas 0-44")
        print("=" * 50)
        send_lines(ser, image_data, 0, BUFFER_SIZE - 1)

        # Aguarda um pouco para STM32 começar processar
        time.sleep(0.5)

        # Captura cabeçalho PGM (enviado pelo STM32 após receber FASE 1)
        header = capture_pgm_header(ser)
        if not header:
            print("\n✗ Erro ao capturar cabeçalho PGM!")
            ser.close()
            sys.exit(1)

        # Captura primeiras 45 linhas filtradas (0-44)
        phase1_lines = capture_filtered_lines(ser, 45, "FASE 1")
        if not phase1_lines:
            print("\n✗ Erro ao capturar linhas da FASE 1!")
            ser.close()
            sys.exit(1)

        # FASE 2: Envia linhas 44-89 (últimas 46 linhas, com overlap)
        print("\n" + "=" * 50)
        print("FASE 2: Enviando últimas 46 linhas (44-89)")
        print("        STM32 processará linhas 45-89")
        print("        (Linha 44 reenviada para contexto do filtro)")
        print("=" * 50)
        send_lines(ser, image_data, 44, height - 1)

        # Aguarda STM32 começar processar
        time.sleep(0.5)

        # Captura últimas 45 linhas filtradas (45-89)
        phase2_lines = capture_filtered_lines(ser, 45, "FASE 2")
        if not phase2_lines:
            print("\n✗ Erro ao capturar linhas da FASE 2!")
            ser.close()
            sys.exit(1)

        print("\n" + "=" * 50)
        print("✓ PROCESSAMENTO COMPLETO")
        print("=" * 50)

        # Combina todas as linhas (45 + 45 = 90)
        all_lines = phase1_lines + phase2_lines

        # Monta dicionário da imagem
        filtered_image = {
            'width': header['width'],
            'height': header['height'],
            'max_val': header['max_val'],
            'data': all_lines
        }

        # Gera nome do arquivo com timestamp
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_filename = f"filtered_{timestamp}.pgm"
        output_path = os.path.join(os.path.dirname(pgm_file), output_filename)

        # Salva arquivo
        if save_pgm_file(filtered_image, output_path):
            print(f"\n{'='*50}")
            print("🎉 PROCESSAMENTO CONCLUÍDO COM SUCESSO!")
            print(f"{'='*50}")
            print(f"Imagem original: {pgm_file}")
            print(f"Imagem filtrada: {output_path}")
            print(f"Total de linhas: {len(all_lines)}")
        else:
            print("\n⚠ Erro ao salvar arquivo.")

        ser.close()

    except serial.SerialException as e:
        print(f"\nERRO na comunicação serial: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nInterrompido pelo usuário!")
        if 'ser' in locals() and ser.is_open:
            ser.close()
        sys.exit(0)


if __name__ == "__main__":
    main()
