#ifndef PGM_IO_H
#define PGM_IO_H

#define IMG_SIZE 90

/*
   Lê de PGM ASCII (P2).
   Retorna 0 em sucesso, -1 em erro.
*/
int read_pgm(const char *path, int image[IMG_SIZE][IMG_SIZE], int *width, int *height);

/*
   Escreve em PGM ASCII (P2). 
   Retorna 0 em sucesso, -1 em erro.
*/
int write_pgm(const char *path, int image[IMG_SIZE][IMG_SIZE], int width, int height);

#endif