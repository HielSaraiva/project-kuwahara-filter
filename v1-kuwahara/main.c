#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "include/kuwahara.h"
#include "include/pgm_io.h"

int main(void)
{
    // Define endereco de imagem de entrada
    // const char *inpath = "imgs_original/balloons.ascii.pgm";
    // const char *inpath = "imgs_original/body3.ascii.pgm";
    // const char *inpath = "imgs_original/Brain1.pgm";
    // const char *inpath = "imgs_original/coins.ascii.pgm";
    const char *inpath = "imgs_original/mona_lisa.ascii.pgm";
    // const char *inpath = "imgs_original/PengBrew.pgm";
    // const char *inpath = "imgs_original/pepper.ascii.pgm";
    // const char *inpath = "imgs_original/saturn.ascii.pgm";

    // Define o tamanho da janela (ímpar)
    int window = 3;

    // Define variável auxiliar
    int image[IMG_SIZE][IMG_SIZE];
    int width = IMG_SIZE, height = IMG_SIZE;

    // Lê imagem
    read_pgm(inpath, image, &width, &height);

    // Aplica filtro kuwahara
    kuwahara_filter(image, window);

    // Constroi caminho de saída
    char outpath[1024];
    if (strncmp(inpath, "imgs_original/", 14) == 0)
    {
        snprintf(outpath, sizeof(outpath), "imgs_filtered/%s", inpath + 14);
    }
    else
    {
        const char *name = strrchr(inpath, '/');
        if (!name)
            name = strrchr(inpath, '\\');
        if (name)
            name++;
        else
            name = inpath;
        snprintf(outpath, sizeof(outpath), "imgs_filtered/%s", name);
    }

    // Escreve imagem após aplicação do filtro
    write_pgm(outpath, image, width, height);

    // Printa no terminal o path de origem, o de destino e o tamanho da janela
    printf("Processado %s -> %s (window=%d)\n", inpath, outpath, window);
    return 0;
}
