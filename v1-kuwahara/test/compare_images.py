"""
Script para comparar imagens PGM geradas pela implementação em C e Python.
Calcula métricas estatísticas de diferença entre as implementações.

Autor: Hiel Saraiva
Data: 17 de outubro de 2025
"""

import os
import numpy as np
from typing import Tuple, Dict


def read_pgm_p2(filepath: str) -> Tuple[np.ndarray, int, int, int]:
    """
    Lê arquivo PGM formato P2 (ASCII).

    Returns:
        tuple: (imagem como array numpy, largura, altura, maxval)
    """
    with open(filepath, 'r') as f:
        # Ler magic number
        magic = f.readline().strip()
        if magic != 'P2':
            raise ValueError(f"Formato esperado P2, encontrado {magic}")

        # Pular comentários
        line = f.readline().strip()
        while line.startswith('#'):
            line = f.readline().strip()

        # Ler dimensões
        width, height = map(int, line.split())

        # Ler maxval
        maxval = int(f.readline().strip())

        # Ler pixels
        pixels = []
        for line in f:
            pixels.extend(map(int, line.split()))

        # Converter para numpy array
        image = np.array(pixels, dtype=np.uint8).reshape(height, width)
        return image, width, height, maxval


def compare_images(img1_path: str, img2_path: str) -> Dict:
    """
    Compara duas imagens PGM e retorna métricas de diferença.

    Args:
        img1_path: Caminho para primeira imagem (C)
        img2_path: Caminho para segunda imagem (Python)

    Returns:
        dict: Dicionário com métricas de comparação
    """
    # Ler as imagens
    img1, w1, h1, maxval1 = read_pgm_p2(img1_path)
    img2, w2, h2, maxval2 = read_pgm_p2(img2_path)

    # Verificar se as dimensões são iguais
    if (w1, h1) != (w2, h2):
        return {
            'identical': False,
            'error': f'Dimensões diferentes: C({w1}x{h1}) vs Python({w2}x{h2})'
        }

    # Verificar identidade
    identical = np.array_equal(img1, img2)

    # Calcular diferenças COM SINAL (C - Python)
    diff_signed = img1.astype(int) - img2.astype(int)

    # Calcular diferenças ABSOLUTAS pixel a pixel
    diff_abs = np.abs(diff_signed)

    # ========== MÉTRICAS DE DIFERENÇA ABSOLUTA ==========

    # Diferença máxima entre pixels de mesma posição
    max_diff_position = np.unravel_index(np.argmax(diff_abs), diff_abs.shape)
    max_diff_value = int(diff_abs[max_diff_position])
    max_diff_c = int(img1[max_diff_position])
    max_diff_py = int(img2[max_diff_position])

    # Diferença média absoluta (MAE - Mean Absolute Error)
    mae = np.mean(diff_abs)

    # Erro Quadrático Médio (RMSE - Root Mean Square Error)
    rmse = np.sqrt(np.mean(diff_signed ** 2))

    # ========== MÉTRICAS DE DIFERENÇA COM SINAL ==========

    # Diferença média com sinal (indica bias: positivo = C maior, negativo = Python maior)
    mean_bias = np.mean(diff_signed)

    # Desvio padrão das diferenças (mede dispersão/variabilidade)
    std_diff = np.std(diff_signed, ddof=1) if len(
        diff_signed.flatten()) > 1 else 0.0

    # ========== PIXELS DIFERENTES ==========

    num_diff_pixels = np.count_nonzero(diff_abs)
    total_pixels = w1 * h1
    percent_diff = (num_diff_pixels / total_pixels) * 100

    # ========== ESTATÍSTICAS DAS IMAGENS ORIGINAIS ==========

    # Estatísticas da imagem C
    img_c_mean = np.mean(img1)
    img_c_std = np.std(img1, ddof=1)

    # Estatísticas da imagem Python
    img_py_mean = np.mean(img2)
    img_py_std = np.std(img2, ddof=1)

    # Diferenças entre estatísticas
    diff_means = img_c_mean - img_py_mean  # Agora com sinal
    diff_stds = img_c_std - img_py_std      # Agora com sinal

    # ========== MÉTRICAS DE SIMILARIDADE ==========

    # SSIM aproximado (correlação normalizada)
    # Valores próximos de 1 = muito similares, próximos de 0 = diferentes
    img1_norm = (img1 - img_c_mean) / (img_c_std + 1e-10)
    img2_norm = (img2 - img_py_mean) / (img_py_std + 1e-10)
    correlation = np.mean(img1_norm * img2_norm)

    # Similaridade percentual (pixels com diferença <= 1)
    tolerance_1 = np.count_nonzero(diff_abs <= 1)
    percent_similar_tol1 = (tolerance_1 / total_pixels) * 100

    # Similaridade percentual (pixels com diferença <= 5)
    tolerance_5 = np.count_nonzero(diff_abs <= 5)
    percent_similar_tol5 = (tolerance_5 / total_pixels) * 100

    return {
        'identical': identical,
        'dimensions': (w1, h1),
        'total_pixels': total_pixels,
        'different_pixels': num_diff_pixels,
        'identical_pixels': total_pixels - num_diff_pixels,
        'percent_different': percent_diff,
        'percent_identical': 100 - percent_diff,
        'max_diff_value': max_diff_value,
        'max_diff_position': max_diff_position,
        'max_diff_c': max_diff_c,
        'max_diff_py': max_diff_py,
        'mae': mae,
        'rmse': rmse,
        'mean_bias': mean_bias,
        'std_diff': std_diff,
        'img_c_mean': img_c_mean,
        'img_c_std': img_c_std,
        'img_py_mean': img_py_mean,
        'img_py_std': img_py_std,
        'diff_means': diff_means,
        'diff_stds': diff_stds,
        'correlation': correlation,
        'percent_similar_tol1': percent_similar_tol1,
        'percent_similar_tol5': percent_similar_tol5
    }


def print_comparison_result(filename: str, result: Dict):
    """Imprime os resultados da comparação de forma formatada."""
    print(f"\n{'='*70}")
    print(f"Arquivo: {filename}")
    print(f"{'='*70}")

    if 'error' in result:
        print(f"[X] ERRO: {result['error']}")
        return

    if result['identical']:
        print("Imagens IDÊNTICAS")
        print(f"\nInformações Gerais:")
        print(
            f"   Dimensões: {result['dimensions'][0]}x{result['dimensions'][1]}")
        print(f"   Total de pixels: {result['total_pixels']}")
        return

    print(f"\nInformações Gerais:")
    print(f"   Dimensões: {result['dimensions'][0]}x{result['dimensions'][1]}")
    print(f"   Total de pixels: {result['total_pixels']}")
    print(
        f"   Pixels diferentes: {result['different_pixels']} ({result['percent_different']:.2f}%)")
    print(
        f"   Pixels idênticos: {result['identical_pixels']} ({result['percent_identical']:.2f}%)")

    print(f"\nMétricas de Erro/Diferença:")
    y, x = result['max_diff_position']
    print(f"   Diferença máxima absoluta (mesma posição):")
    print(f"      └─ Valor: {result['max_diff_value']} pixels")
    print(f"      └─ Posição: linha {y}, coluna {x}")
    print(
        f"      └─ Valor C: {result['max_diff_c']}, Valor Python: {result['max_diff_py']}")

    print(f"   EMA (Erro Médio Absoluto): {result['mae']:.4f} pixels")

    print(f"\nMétricas de Similaridade:")
    print(f"   Correlação normalizada: {result['correlation']:.4f}")

    # Calcular quantidade de pixels para tolerância
    tolerance_1_count = int(
        result['total_pixels'] * result['percent_similar_tol1'] / 100)
    tolerance_5_count = int(
        result['total_pixels'] * result['percent_similar_tol5'] / 100)

    print(
        f"   Pixels com diferença ≤ 1: {result['percent_similar_tol1']:.2f}% ({tolerance_1_count}/{result['total_pixels']} pixels)")
    print(
        f"   Pixels com diferença ≤ 5: {result['percent_similar_tol5']:.2f}% ({tolerance_5_count}/{result['total_pixels']} pixels)")

    print(f"\nEstatísticas da Imagem C:")
    print(f"   Média dos pixels: {result['img_c_mean']:.2f}")
    print(f"   Desvio padrão (amostral): {result['img_c_std']:.2f}")

    print(f"\nEstatísticas da Imagem Python:")
    print(f"   Média dos pixels: {result['img_py_mean']:.2f}")
    print(f"   Desvio padrão (amostral): {result['img_py_std']:.2f}")

    print(f"\nDiferença entre Estatísticas:")
    print(f"   Diferença nas médias (C - Python): {result['diff_means']:+.2f}")
    print(
        f"   Diferença nos desvios padrão (C - Python): {result['diff_stds']:+.2f}")


def main():
    """Função principal que executa os testes de comparação."""
    # Definir caminhos
    c_filtered_dir = "../imgs_filtered"
    python_filtered_dir = "../python_implementation/imgs_filtered"

    # Verificar se os diretórios existem
    if not os.path.exists(c_filtered_dir):
        print(f"[X] Diretório não encontrado: {c_filtered_dir}")
        print("Execute primeiro o programa em C para gerar as imagens filtradas.")
        return

    if not os.path.exists(python_filtered_dir):
        print(f"[X] Diretório não encontrado: {python_filtered_dir}")
        print("Execute primeiro o programa Python para gerar as imagens filtradas.")
        return

    # Listar arquivos .pgm do diretório C
    c_files = [f for f in os.listdir(c_filtered_dir) if f.endswith('.pgm')]

    if not c_files:
        print("[X] Nenhuma imagem filtrada encontrada no diretório C.")
        return

    print(f"\n{'='*70}")
    print(f"COMPARAÇÃO DE IMAGENS: Implementação C vs Python")
    print(f"{'='*70}")

    # Comparar cada arquivo
    for filename in sorted(c_files):
        c_path = os.path.join(c_filtered_dir, filename)
        python_path = os.path.join(python_filtered_dir, filename)

        if not os.path.exists(python_path):
            print(f"\n[X] Arquivo {filename} não encontrado na versão Python")
            continue

        try:
            result = compare_images(c_path, python_path)
            print_comparison_result(filename, result)
        except Exception as e:
            print(f"\n[X] Erro ao comparar {filename}: {e}")


if __name__ == "__main__":
    main()
