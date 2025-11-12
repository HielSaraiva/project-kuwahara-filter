"""
Script para comparar imagens PGM filtradas pixel a pixel.
Gera heatmap mostrando as diferenças entre duas imagens.

Uso:
    python compare_filtered.py <imagem1.pgm> <imagem2.pgm>

Exemplo:
    python compare_filtered.py ../Core/pgms/filtered_20251108_120000.pgm \\
                                ../../v1-kuwahara/imgs_filtered/mona_lisa.ascii.pgm

Autor: Hiel Saraiva
Data: 8 de novembro de 2025
"""

from typing import Tuple, Dict
from matplotlib.colors import ListedColormap, BoundaryNorm
import matplotlib.pyplot as plt
import os
import sys
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
        img1_path: Caminho para primeira imagem
        img2_path: Caminho para segunda imagem

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
            'error': f'Dimensões diferentes: Imagem1({w1}x{h1}) vs Imagem2({w2}x{h2})'
        }

    # Verificar identidade
    identical = np.array_equal(img1, img2)

    # Calcular diferenças COM SINAL (img1 - img2)
    diff_signed = img1.astype(int) - img2.astype(int)

    # Calcular diferenças ABSOLUTAS pixel a pixel
    diff_abs = np.abs(diff_signed)

    # ========== MÉTRICAS DE DIFERENÇA ABSOLUTA ==========

    # Diferença máxima entre pixels de mesma posição
    max_diff_position = np.unravel_index(np.argmax(diff_abs), diff_abs.shape)
    max_diff_value = int(diff_abs[max_diff_position])
    max_diff_img1 = int(img1[max_diff_position])
    max_diff_img2 = int(img2[max_diff_position])

    # Diferença média absoluta (MAE - Mean Absolute Error)
    mae = np.mean(diff_abs)

    # Erro Quadrático Médio (RMSE - Root Mean Square Error)
    rmse = np.sqrt(np.mean(diff_signed ** 2))

    # ========== MÉTRICAS DE DIFERENÇA COM SINAL ==========

    # Diferença média com sinal (indica bias)
    mean_bias = np.mean(diff_signed)

    # Desvio padrão das diferenças
    std_diff = np.std(diff_signed, ddof=1) if len(
        diff_signed.flatten()) > 1 else 0.0

    # ========== PIXELS DIFERENTES ==========

    num_diff_pixels = np.count_nonzero(diff_abs)
    total_pixels = w1 * h1
    percent_diff = (num_diff_pixels / total_pixels) * 100

    # ========== ESTATÍSTICAS DAS IMAGENS ORIGINAIS ==========

    # Estatísticas da imagem 1
    img1_mean = np.mean(img1)
    img1_std = np.std(img1, ddof=1)

    # Estatísticas da imagem 2
    img2_mean = np.mean(img2)
    img2_std = np.std(img2, ddof=1)

    # Diferenças entre estatísticas
    diff_means = img1_mean - img2_mean
    diff_stds = img1_std - img2_std

    # ========== MÉTRICAS DE SIMILARIDADE ==========

    # Correlação normalizada
    img1_norm = (img1 - img1_mean) / (img1_std + 1e-10)
    img2_norm = (img2 - img2_mean) / (img2_std + 1e-10)
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
        'max_diff_img1': max_diff_img1,
        'max_diff_img2': max_diff_img2,
        'mae': mae,
        'rmse': rmse,
        'mean_bias': mean_bias,
        'std_diff': std_diff,
        'img1_mean': img1_mean,
        'img1_std': img1_std,
        'img2_mean': img2_mean,
        'img2_std': img2_std,
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
        img1_path: Caminho para primeira imagem
        img2_path: Caminho para segunda imagem
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

    # Subplot 1: Imagem 1
    axes[0].imshow(img1, cmap='gray', vmin=0, vmax=255)
    axes[0].set_title(f'Imagem 1\n{os.path.basename(img1_path)}',
                      fontsize=10, fontweight='bold')
    axes[0].axis('off')

    # Subplot 2: Imagem 2
    axes[1].imshow(img2, cmap='gray', vmin=0, vmax=255)
    axes[1].set_title(f'Imagem 2\n{os.path.basename(img2_path)}',
                      fontsize=10, fontweight='bold')
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
        f'Comparação de Imagens PGM Filtradas\n'
        f'Total: {total} pixels | Média: {mean_diff:.4f} | Máximo: {max_diff}\n'
        f'Idênticos: {num_identical} | Diff=1: {num_diff_1} | '
        f'Diff 2-3: {num_diff_2_3} | Diff 4-5: {num_diff_4_5} | '
        f'Diff 6-10: {num_diff_6_10} | Diff>10: {num_diff_10_plus}',
        fontsize=10
    )

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"\n✓ Heatmap salvo em: {output_path}")


def print_comparison_result(img1_name: str, img2_name: str, result: Dict):
    """Imprime os resultados da comparação de forma formatada."""
    print(f"\n{'='*70}")
    print(f"COMPARAÇÃO DE IMAGENS")
    print(f"{'='*70}")
    print(f"Imagem 1: {img1_name}")
    print(f"Imagem 2: {img2_name}")
    print(f"{'='*70}")

    if 'error' in result:
        print(f"✗ ERRO: {result['error']}")
        return

    if result['identical']:
        print("✓ Imagens IDÊNTICAS")
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
        f"      └─ Valor Img1: {result['max_diff_img1']}, Valor Img2: {result['max_diff_img2']}")

    print(f"   EMA (Erro Médio Absoluto): {result['mae']:.4f} pixels")
    print(f"   RMSE (Erro Quadrático Médio): {result['rmse']:.4f} pixels")

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

    print(f"\nEstatísticas da Imagem 1:")
    print(f"   Média dos pixels: {result['img1_mean']:.2f}")
    print(f"   Desvio padrão (amostral): {result['img1_std']:.2f}")

    print(f"\nEstatísticas da Imagem 2:")
    print(f"   Média dos pixels: {result['img2_mean']:.2f}")
    print(f"   Desvio padrão (amostral): {result['img2_std']:.2f}")

    print(f"\nDiferença entre Estatísticas:")
    print(
        f"   Diferença nas médias (Img1 - Img2): {result['diff_means']:+.2f}")
    print(
        f"   Diferença nos desvios padrão (Img1 - Img2): {result['diff_stds']:+.2f}")


def main():
    """Função principal."""
    if len(sys.argv) != 3:
        print("\n✗ Uso incorreto!")
        print("\nUso:")
        print("   python3 compare_filtered.py <imagem1.pgm> <imagem2.pgm>")
        print("\nExemplo:")
        print("   python3 compare_filtered.py ../Core/pgms/filtered_20251108_120000.pgm \\")
        print("                               ../../v1-kuwahara/imgs_filtered/mona_lisa.ascii.pgm")
        sys.exit(1)

    img1_path = sys.argv[1]
    img2_path = sys.argv[2]

    # Verificar se os arquivos existem
    if not os.path.exists(img1_path):
        print(f"\n✗ Arquivo não encontrado: {img1_path}")
        sys.exit(1)

    if not os.path.exists(img2_path):
        print(f"\n✗ Arquivo não encontrado: {img2_path}")
        sys.exit(1)

    # Criar diretório para heatmaps
    script_dir = os.path.dirname(os.path.abspath(__file__))
    heatmaps_dir = os.path.join(script_dir, 'heatmaps')
    os.makedirs(heatmaps_dir, exist_ok=True)

    try:
        # Comparar as imagens
        result = compare_images(img1_path, img2_path)
        print_comparison_result(
            os.path.basename(img1_path),
            os.path.basename(img2_path),
            result
        )

        # Gerar nome do heatmap
        img1_basename = os.path.splitext(os.path.basename(img1_path))[0]
        img2_basename = os.path.splitext(os.path.basename(img2_path))[0]
        heatmap_filename = f"heatmap_{img1_basename}_vs_{img2_basename}.png"
        heatmap_path = os.path.join(heatmaps_dir, heatmap_filename)

        # Gerar heatmap
        plot_difference_heatmap(img1_path, img2_path, heatmap_path)

        print(f"\n{'='*70}")
        print("✓ COMPARAÇÃO CONCLUÍDA COM SUCESSO!")
        print(f"{'='*70}")

    except Exception as e:
        print(f"\n✗ Erro ao comparar imagens: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
