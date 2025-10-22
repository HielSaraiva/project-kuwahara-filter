"""
Script para comparar imagens PGM geradas pela implementação em C e Python.
Calcula métricas estatísticas de diferença entre as implementações.

Autor: Hiel Saraiva
Data: 17 de outubro de 2025
"""

from typing import Tuple, Dict
from matplotlib.colors import ListedColormap, BoundaryNorm
import matplotlib.pyplot as plt
import os
import numpy as np
import matplotlib
# Usar backend sem interface gráfica para evitar erro de Tkinter
matplotlib.use('Agg')


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


def plot_difference_heatmap(img1_path: str, img2_path: str, output_path: str):
    """
    Gera um heatmap mostrando as diferenças entre duas imagens.
    Usa categorias de cores discretas para melhor visualização.

    Args:
        img1_path: Caminho para primeira imagem (C)
        img2_path: Caminho para segunda imagem (Python)
        output_path: Caminho para salvar o gráfico
    """
    # Ler as imagens
    img1, _, _, _ = read_pgm_p2(img1_path)
    img2, _, _, _ = read_pgm_p2(img2_path)

    # Calcular diferenças absolutas
    diff_abs = np.abs(img1.astype(int) - img2.astype(int))

    # Definir categorias de diferença
    # 0: Idêntico (preto)
    # 1: Diff = 1 (azul escuro)
    # 2: Diff = 2-3 (azul claro)
    # 3: Diff = 4-5 (verde)
    # 4: Diff = 6-10 (amarelo)
    # 5: Diff > 10 (vermelho)

    diff_categorized = np.zeros_like(diff_abs, dtype=int)
    diff_categorized[diff_abs == 0] = 0  # Idêntico
    diff_categorized[diff_abs == 1] = 1  # Diff = 1
    diff_categorized[(diff_abs >= 2) & (diff_abs <= 3)] = 2  # Diff 2-3
    diff_categorized[(diff_abs >= 4) & (diff_abs <= 5)] = 3  # Diff 4-5
    diff_categorized[(diff_abs >= 6) & (diff_abs <= 10)] = 4  # Diff 6-10
    diff_categorized[diff_abs > 10] = 5  # Diff > 10

    # Cores personalizadas
    colors = [
        '#000000',  # 0: Preto (idêntico)
        '#1f77b4',  # 1: Azul escuro (diff=1)
        '#17becf',  # 2: Azul ciano (diff 2-3)
        '#2ca02c',  # 3: Verde (diff 4-5)
        '#ff7f0e',  # 4: Laranja (diff 6-10)
        '#d62728'   # 5: Vermelho (diff >10)
    ]
    cmap = ListedColormap(colors)
    bounds = [0, 1, 2, 3, 4, 5, 6]
    norm = BoundaryNorm(bounds, cmap.N)

    # Criar figura com 3 subplots
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    # Subplot 1: Imagem C
    axes[0].imshow(img1, cmap='gray', vmin=0, vmax=255)
    axes[0].set_title('Implementação C', fontsize=12, fontweight='bold')
    axes[0].axis('off')

    # Subplot 2: Imagem Python
    axes[1].imshow(img2, cmap='gray', vmin=0, vmax=255)
    axes[1].set_title('Implementação Python', fontsize=12, fontweight='bold')
    axes[1].axis('off')

    # Subplot 3: Heatmap de diferenças categorizadas
    im = axes[2].imshow(diff_categorized, cmap=cmap, norm=norm)
    axes[2].set_title('Mapa de Diferenças (Categorizado)',
                      fontsize=12, fontweight='bold')

    # Adicionar eixos com medições de pixels
    height, width = diff_categorized.shape

    # Configurar eixo X (horizontal - largura)
    x_ticks = np.arange(0, width, 10)
    axes[2].set_xticks(x_ticks)
    axes[2].set_xticklabels(x_ticks, fontsize=8)
    axes[2].set_xlabel('Pixels (Largura)', fontsize=10)

    # Configurar eixo Y (vertical - altura)
    y_ticks = np.arange(0, height, 10)
    axes[2].set_yticks(y_ticks)
    axes[2].set_yticklabels(y_ticks, fontsize=8)
    axes[2].set_ylabel('Pixels (Altura)', fontsize=10)

    # Manter grid leve para facilitar leitura
    axes[2].grid(False)

    # Adicionar colorbar customizada
    cbar = plt.colorbar(im, ax=axes[2], fraction=0.046, pad=0.04,
                        ticks=[0.5, 1.5, 2.5, 3.5, 4.5, 5.5])
    cbar.set_ticklabels(['0\n(Idêntico)', '1', '2-3', '4-5', '6-10', '>10'])
    cbar.set_label('Diferença (pixels)', rotation=270,
                   labelpad=20, fontsize=10)

    # Calcular estatísticas por categoria
    num_identical = np.count_nonzero(diff_abs == 0)
    num_diff_1 = np.count_nonzero(diff_abs == 1)
    num_diff_2_3 = np.count_nonzero((diff_abs >= 2) & (diff_abs <= 3))
    num_diff_4_5 = np.count_nonzero((diff_abs >= 4) & (diff_abs <= 5))
    num_diff_6_10 = np.count_nonzero((diff_abs >= 6) & (diff_abs <= 10))
    num_diff_10_plus = np.count_nonzero(diff_abs > 10)

    total = diff_abs.size
    max_diff = np.max(diff_abs)
    mean_diff = np.mean(diff_abs)

    # Título com estatísticas
    fig.suptitle(
        f'Comparação: {os.path.basename(img1_path)}\n'
        f'Total: {total} pixels | Média: {mean_diff:.4f} | Máximo: {max_diff}\n'
        f'Idênticos: {num_identical} | Diff=1: {num_diff_1} | '
        f'Diff 2-3: {num_diff_2_3} | Diff 4-5: {num_diff_4_5} | '
        f'Diff 6-10: {num_diff_6_10} | Diff>10: {num_diff_10_plus}',
        fontsize=10
    )

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"   Heatmap salvo em: {output_path}")


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
    # Definir caminhos (agora test está dentro de python_implementation)
    c_filtered_dir = "../../imgs_filtered"
    python_filtered_dir = "../imgs_filtered"

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

    # Criar diretório para armazenar os heatmaps
    test_imgs_dir = "imgs_tests"
    if not os.path.exists(test_imgs_dir):
        os.makedirs(test_imgs_dir)
        print(f"\nDiretório criado: {test_imgs_dir}/")

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

            # Gerar heatmap sempre (mesmo para imagens idênticas)
            heatmap_filename = f"diff_heatmap_{filename.replace('.pgm', '.png')}"
            heatmap_path = os.path.join(test_imgs_dir, heatmap_filename)
            plot_difference_heatmap(c_path, python_path, heatmap_path)
        except Exception as e:
            print(f"\n[X] Erro ao comparar {filename}: {e}")


if __name__ == "__main__":
    main()
