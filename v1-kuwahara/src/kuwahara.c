#include "../include/kuwahara.h"
#include <math.h>

void kuwahara_filter(int image[IMG_SIZE][IMG_SIZE], int window)
{
    // Define dimensões da imagem e calcular tamanho dos quadrantes
    int width = IMG_SIZE, height = IMG_SIZE;
    int window_size = window;
    int quadrant_size = (window_size + 1) / 2;
    int result[IMG_SIZE][IMG_SIZE]; // ESTRUTURA DE DADOS auxiliar para armazenar o resultado (8100 valores inteiros)

    // Percorre cada pixel da imagem
    for (int pixel_y = 0; pixel_y < height; ++pixel_y)
    {
        for (int pixel_x = 0; pixel_x < width; ++pixel_x)
        {
            // Calcula canto superior esquerdo da janela centrada no pixel atual
            int window_top_y = pixel_y - (window_size / 2);
            int window_left_x = pixel_x - (window_size / 2);

            // Inicializa busca pelo quadrante com menor desvio padrão
            double best_std_dev = 1e300; // valor inicial muito grande
            double best_mean = image[pixel_y][pixel_x];

            // Analisa os 4 quadrantes sobrepostos
            for (int quadrant_y = 0; quadrant_y <= 1; ++quadrant_y)
            {
                for (int quadrant_x = 0; quadrant_x <= 1; ++quadrant_x)
                {
                    // Acumula soma e soma dos quadrados para calcular estatísticas
                    long long sum = 0, sum_sq = 0;
                    int pixel_count = 0;

                    // Percorre pixels dentro do quadrante atual
                    for (int offset_y = 0; offset_y < quadrant_size; ++offset_y)
                    {
                        for (int offset_x = 0; offset_x < quadrant_size; ++offset_x)
                        {
                            // Aalcula posição real do pixel (com sobreposição dos quadrantes)
                            int read_y = window_top_y + (quadrant_y ? (quadrant_size - 1) : 0) + offset_y;
                            int read_x = window_left_x + (quadrant_x ? (quadrant_size - 1) : 0) + offset_x;

                            // Aplica BORDER_REFLECT_101 (reflexão espelhada, como no OpenCV)
                            // Reflete para dentro da imagem sem incluir o pixel da borda
                            if (read_y < 0)
                                read_y = -read_y;
                            if (read_y >= height)
                                read_y = 2 * height - read_y - 2;
                            if (read_x < 0)
                                read_x = -read_x;
                            if (read_x >= width)
                                read_x = 2 * width - read_x - 2;
                            
                            // Clamping como fallback para casos extremos
                            if (read_y < 0)
                                read_y = 0;
                            if (read_y >= height)
                                read_y = height - 1;
                            if (read_x < 0)
                                read_x = 0;
                            if (read_x >= width)
                                read_x = width - 1;

                            // Acumula valores para cálculo de média e desvio padrão
                            int pixel_value = image[read_y][read_x];
                            sum += pixel_value;
                            sum_sq += (long long)pixel_value * (long long)pixel_value;
                            pixel_count++;
                        }
                    }

                    // Calcula estatísticas do quadrante atual
                    if (pixel_count > 1)
                    {
                        double mean = (double)sum / (double)pixel_count;
                        
                        // Desvio padrão
                        double variance = ((double)sum_sq - (double)sum * sum / pixel_count) / (pixel_count - 1);
                        
                        double std_dev = sqrt(variance);

                        // Atualiza se encontrou quadrante mais homogêneo (menor desvio padrão)
                        if (std_dev < best_std_dev)
                        {
                            best_std_dev = std_dev;
                            best_mean = mean; // Armazena sem arredondar
                        }
                    }
                }
            }
            // Atribui média do melhor quadrante ao pixel de saída
            result[pixel_y][pixel_x] = (int)(best_mean);
        }
    }

    // Copia resultado do buffer temporário para a imagem original
    for (int i = 0; i < height; ++i)
    {
        for (int j = 0; j < width; ++j)
        {
            image[i][j] = result[i][j];
        }
    }
}