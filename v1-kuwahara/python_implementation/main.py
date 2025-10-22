"""
Filtro Kuwahara usando biblioteca pykuwahara
Lê imagens PGM formato P2, aplica o filtro e salva em P2
"""

import cv2
import numpy as np
from pykuwahara import kuwahara
import os


def read_pgm_p2(filepath):
    """Lê arquivo PGM formato P2 (ASCII)"""
    with open(filepath, 'r') as f:
        # Lê o número mágico
        magic = f.readline().strip()
        if magic != 'P2':
            raise ValueError(f"Formato esperado P2, encontrado {magic}")

        # Pula comentários
        line = f.readline().strip()
        while line.startswith('#'):
            line = f.readline().strip()

        # Lê dimensões
        width, height = map(int, line.split())

        # Lê o valor máximo
        maxval = int(f.readline().strip())

        # Lê pixels
        pixels = []
        for line in f:
            pixels.extend(map(int, line.split()))

        # Converte para numpy array
        image = np.array(pixels, dtype=np.uint8).reshape(height, width)
        return image


def write_pgm_p2(filepath, image):
    """Escreve arquivo PGM formato P2 (ASCII)"""
    height, width = image.shape

    with open(filepath, 'w') as f:
        f.write("P2\n")
        f.write("# Kuwahara filtered (pykuwahara library)\n")
        f.write(f"{width} {height}\n")
        f.write("255\n")

        # Escreve pixels (15 por linha)
        count = 0
        for y in range(height):
            for x in range(width):
                f.write(f"{int(image[y, x])} ")
                count += 1
                if count % 15 == 0:
                    f.write("\n")

        if count % 15 != 0:
            f.write("\n")


def main():
    # Lista de imagens para processar
    images = [
        "../imgs_original/mona_lisa.ascii.pgm",
        # "../imgs_original/pepper.ascii.pgm",
    ]

    # Tamanho da janela (radius no pykuwahara)
    window = 3
    radius = window // 2  # radius = 1 para window=3

    # Criar pasta de saída
    os.makedirs("imgs_filtered", exist_ok=True)

    for img_path in images:
        try:
            print(f"Processando: {img_path}")

            # Lê imagem P2
            image = read_pgm_p2(img_path)
            print(f"  Dimensões: {image.shape[1]}x{image.shape[0]}")

            # Aplica filtro Kuwahara usando pykuwahara
            print(
                f"  Aplicando filtro Kuwahara (window={window}, radius={radius})...")
            filtered = kuwahara(image, method='mean', radius=radius)

            # Garante que valores estão no range correto
            filtered = np.clip(filtered, 0, 255).astype(np.uint8)

            # Controi caminho de saída
            filename = os.path.basename(img_path)
            output_path = f"imgs_filtered/{filename}"

            # Salva em formato P2
            write_pgm_p2(output_path, filtered)

            print(f"  ✓ Salvo: {output_path}\n")

        except Exception as e:
            print(f"  ✗ Erro: {e}\n")


if __name__ == "__main__":
    main()
