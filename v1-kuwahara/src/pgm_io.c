#include "../include/pgm_io.h"
#include <stdio.h>
#include <string.h>

int read_pgm(const char *path, int image[IMG_SIZE][IMG_SIZE], int *width, int *height)
{
    FILE *f = fopen(path, "r");
    if (!f)
        return -1;
    
    char line[256];
    int w, h, maxv;
    
    // Lê header P2
    if (!fgets(line, sizeof(line), f) || strncmp(line, "P2", 2) != 0)
    {
        fclose(f);
        return -1;
    }
    
    // Pula comentários
    do
    {
        if (!fgets(line, sizeof(line), f))
        {
            fclose(f);
            return -1;
        }
    } while (line[0] == '#');
    
    // Lê dimensões
    if (sscanf(line, "%d %d", &w, &h) != 2)
    {
        fclose(f);
        return -1;
    }
    
    // Lê valor máximo
    if (fscanf(f, "%d", &maxv) != 1)
    {
        fclose(f);
        return -1;
    }
    
    *width = w;
    *height = h;

    // Lê dados da imagem
    for (int i = 0; i < h; ++i)
    {
        for (int j = 0; j < w; ++j)
        {
            if (fscanf(f, "%d", &image[i][j]) != 1)
            {
                fclose(f);
                return -1;
            }
        }
    }
    
    fclose(f);
    return 0;
}

int write_pgm(const char *path, int image[IMG_SIZE][IMG_SIZE], int width, int height)
{
    FILE *f = fopen(path, "w");
    if (!f)
        return -1;
        
    fprintf(f, "P2\n%d %d\n255\n", width, height);
    
    for (int i = 0; i < height; ++i)
    {
        for (int j = 0; j < width; ++j)
        {
            fprintf(f, "%d ", image[i][j]);
        }
        fprintf(f, "\n");
    }
    
    fclose(f);
    return 0;
}