/* USER CODE BEGIN Header */
/**
 ******************************************************************************
 * @file           : main.c
 * @brief          : Main program body
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2025 STMicroelectronics.
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file
 * in the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 *
 ******************************************************************************
 */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include <stdio.h>
#include <math.h>
#include <stdint.h>
#include <string.h>

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */

/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */
#define IMG_SIZE 90			 // Tamanho N x N da imagem (90x90)
#define KUWAHARA_WINDOW 3	 // Janela do filtro Kuwahara
#define BUFFER_SIZE 46		 // Buffer para 46 linhas (0-45 ou 44-89)
#define MAX_PIXEL_VALUE 255 // Valor máximo de pixel (escala de cinza)

// Modo de operação: comente a linha abaixo para usar modo Flash (antigo)
#define STREAMING_MODE // Habilita recepção via UART (modo streaming)

#ifndef STREAMING_MODE
// Modo Flash: escolha a imagem
#define USE_MONA_LISA
// #define USE_PEPPER

#ifdef USE_MONA_LISA
#include "image_mona_lisa.h"
#elif defined(USE_PEPPER)
#include "image_pepper.h"
#else
#error "Nenhuma imagem selecionada! Defina USE_MONA_LISA ou USE_PEPPER"
#endif
#endif

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
UART_HandleTypeDef huart2;

/* USER CODE BEGIN PV */
#ifdef STREAMING_MODE
// Buffer para 46 linhas da imagem (46x90)
static pixel_t image_buffer[BUFFER_SIZE][IMG_SIZE];
#endif
/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_USART2_UART_Init(void);
/* USER CODE BEGIN PFP */

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */
/**
 * @brief Aplica o filtro Kuwahara na imagem de entrada.
 * @param image_in Ponteiro para a imagem de entrada (const, na Flash).
 * @param image_out Ponteiro para a imagem de saída (na SRAM).
 * @param window Tamanho da janela do filtro (deve ser 3, 5, 7, etc.).
 */
/**
 * @brief Aplica o filtro Kuwahara na imagem de entrada e imprime o resultado no terminal.
 * @param image_in Ponteiro para a imagem de entrada (const, na Flash).
 * @param window Tamanho da janela do filtro (deve ser 3, 5, 7, etc.).
 */
void kuwahara_filter(const pixel_t image_in[IMG_SIZE][IMG_SIZE],
							int window)
{
	// Define dimensões da imagem e calcular tamanho dos quadrantes
	const int width = IMG_SIZE;
	const int height = IMG_SIZE;
	const int window_size = window;
	const int quadrant_size = (window_size + 1) / 2;

	// Imprime cabeçalho PGM P2 APENAS UMA VEZ
	printf("P2\n");
	printf("%d %d\n", IMG_SIZE, IMG_SIZE);
	printf("255\n");

	// Percorre cada pixel da imagem e imprime o resultado Imediatamente
	for (int pixel_y = 0; pixel_y < height; ++pixel_y)
	{
		for (int pixel_x = 0; pixel_x < width; ++pixel_x)
		{
			// Calcula canto superior esquerdo da janela centrada no pixel atual
			int window_top_y = pixel_y - (window_size / 2);
			int window_left_x = pixel_x - (window_size / 2);

			// Inicializa busca pelo quadrante com menor desvio padrão
			double best_std_dev = 1e300; // valor inicial muito grande
			double best_mean = image_in[pixel_y][pixel_x];

			// Analisa os 4 quadrantes sobrepostos
			// Pykuwahara usa "anchors" na ordem: (0,0), (0,1), (1,0), (1,1)
			// Que correspondem aos quadrantes: (1,1), (0,1), (1,0), (0,0)
			int quadrant_order[4][2] = {{1, 1}, {0, 1}, {1, 0}, {0, 0}};

			for (int q = 0; q < 4; ++q)
			{
				int quadrant_y = quadrant_order[q][0];
				int quadrant_x = quadrant_order[q][1];

				// Acumula soma e soma dos quadrados para calcular estatísticas
				long long sum = 0, sum_sq = 0;
				int pixel_count = 0;

				// Percorre pixels dentro do quadrante atual
				for (int offset_y = 0; offset_y < quadrant_size; ++offset_y)
				{
					for (int offset_x = 0; offset_x < quadrant_size; ++offset_x)
					{
						// Calcula posição real do pixel (com sobreposição dos quadrantes)
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
						int pixel_value = image_in[read_y][read_x];
						sum += pixel_value;
						sum_sq += (long long)pixel_value * (long long)pixel_value;
						pixel_count++;
					}
				}

				// Calcula estatísticas do quadrante atual
				if (pixel_count > 1)
				{
					double mean = (double)sum / (double)pixel_count;

					// Calcula Variância Populacional
					double variance = ((double)sum_sq - (double)sum * sum / pixel_count) / pixel_count;

					double std_dev = sqrt(variance);

					// Atualiza se encontrou quadrante mais homogêneo (menor desvio padrão)
					if (std_dev < best_std_dev)
					{
						best_std_dev = std_dev;
						best_mean = mean; // Armazena sem arredondar
					}
				}
			}

			// Atribui média do melhor quadrante ao pixel de saída (trunca para int)
			int filtered_value = (int)(best_mean);

			printf("%d", filtered_value);

			// Adiciona um espaço após o pixel, exceto o último da linha
			if (pixel_x < width - 1)
			{
				printf(" ");
			}
		}
		// Nova linha após cada linha da imagem (90 pixels)
		printf("\n");
	}
}

#ifdef STREAMING_MODE
// Envia string inteira
static void uart_send_str(const char *s)
{
	size_t len = strlen(s);
	if (len > 0)
	{
		HAL_UART_Transmit(&huart2, (uint8_t *)s, (uint16_t)len, 1000);
	}
}

// Aguarda por um token específico (ex: "#GO2#") dentro de um tempo total
static int uart_wait_token(const char *token, uint32_t timeout_ms)
{
	const size_t tlen = strlen(token);
	size_t matched = 0;
	uint8_t b;
	uint32_t start = HAL_GetTick();

	while ((HAL_GetTick() - start) < timeout_ms)
	{
		if (HAL_UART_Receive(&huart2, &b, 1, 100) == HAL_OK)
		{
			if (b == (uint8_t)token[matched])
			{
				matched++;
				if (matched == tlen)
					return 1; // encontrado
			}
			else
			{
				matched = (b == (uint8_t)token[0]) ? 1 : 0;
			}
		}
	}
	return 0; // não encontrado
}

/**
 * @brief Recebe uma linha de pixels via UART.
 * @param line_buffer Ponteiro para array onde armazenar a linha.
 * @return 1 se sucesso, 0 se erro.
 */
int receive_line_uart(pixel_t *line_buffer)
{
	uint8_t rx_byte;
	int pixel_count = 0;
	int current_value = 0;
	int has_digit = 0;

	while (pixel_count < IMG_SIZE)
	{
		if (HAL_UART_Receive(&huart2, &rx_byte, 1, 3600000) == HAL_OK)
		{
			if (rx_byte >= '0' && rx_byte <= '9')
			{
				current_value = current_value * 10 + (rx_byte - '0');
				has_digit = 1;
			}
			else if (rx_byte == ' ' || rx_byte == '\n' || rx_byte == '\r')
			{
				if (has_digit)
				{
					line_buffer[pixel_count++] = (pixel_t)current_value;
					current_value = 0;
					has_digit = 0;
				}
				if (rx_byte == '\n')
					break;
			}
		}
		else
		{
			return 0; // Timeout
		}
	}
	return (pixel_count == IMG_SIZE) ? 1 : 0;
}

/**
 * @brief Processa e envia linhas filtradas, usando o buffer como fonte.
 * @param start_line Linha inicial na imagem COMPLETA (0-89).
 * @param end_line Linha final na imagem COMPLETA (0-89).
 * @param buffer_start_line Linha inicial no BUFFER (0-45).
 */
// Aplica o filtro Kuwahara usando o buffer parcial (streaming) e envia linhas filtradas
void kuwahara_filter_buffered(int start_line, int end_line, int buffer_start_line)
{
	const int width = IMG_SIZE;
	const int height = IMG_SIZE;
	const int window_size = KUWAHARA_WINDOW;
	const int quadrant_size = (window_size + 1) / 2;
	char line_buf[512];

	for (int pixel_y = start_line; pixel_y <= end_line; ++pixel_y)
	{
		// Mapeia coordenada global para buffer
		int buffer_y = pixel_y - start_line + buffer_start_line;
		int offset = 0;

		for (int pixel_x = 0; pixel_x < width; ++pixel_x)
		{
			int window_top_y = pixel_y - (window_size / 2);
			int window_left_x = pixel_x - (window_size / 2);

			double best_std_dev = 1e300;
			double best_mean = image_buffer[buffer_y][pixel_x];

			int quadrant_order[4][2] = {{1, 1}, {0, 1}, {1, 0}, {0, 0}};

			for (int q = 0; q < 4; ++q)
			{
				int quadrant_y = quadrant_order[q][0];
				int quadrant_x = quadrant_order[q][1];

				long long sum = 0, sum_sq = 0;
				int pixel_count = 0;
				int valid_quadrant = 1; // Flag para verificar se todos pixels estão no buffer

				for (int offset_y = 0; offset_y < quadrant_size; ++offset_y)
				{
					for (int offset_x = 0; offset_x < quadrant_size; ++offset_x)
					{
						int read_y = window_top_y + (quadrant_y ? (quadrant_size - 1) : 0) + offset_y;
						int read_x = window_left_x + (quadrant_x ? (quadrant_size - 1) : 0) + offset_x;

						// BORDER_REFLECT_101
						if (read_y < 0)
							read_y = -read_y;
						if (read_y >= height)
							read_y = 2 * height - read_y - 2;
						if (read_x < 0)
							read_x = -read_x;
						if (read_x >= width)
							read_x = 2 * width - read_x - 2;

						// Clamping
						if (read_y < 0)
							read_y = 0;
						if (read_y >= height)
							read_y = height - 1;
						if (read_x < 0)
							read_x = 0;
						if (read_x >= width)
							read_x = width - 1;

						// Converter coordenada global → buffer
						int buf_y = read_y - start_line + buffer_start_line;

						// Verifica se está no buffer
						if (buf_y >= 0 && buf_y < BUFFER_SIZE)
						{
							int pixel_value = image_buffer[buf_y][read_x];
							sum += pixel_value;
							sum_sq += (long long)pixel_value * (long long)pixel_value;
							pixel_count++;
						}
						else
						{
							// Pixel necessário não está no buffer - quadrante inválido
							valid_quadrant = 0;
							break;
						}
					}
					if (!valid_quadrant)
						break;
				}

				// Só considera quadrante se todos os pixels estavam disponíveis
				if (valid_quadrant && pixel_count > 1)
				{
					double mean = (double)sum / (double)pixel_count;
					double variance = ((double)sum_sq - (double)sum * sum / pixel_count) / pixel_count;
					double std_dev = sqrt(variance);

					if (std_dev < best_std_dev)
					{
						best_std_dev = std_dev;
						best_mean = mean;
					}
				}
			}

			int filtered_value = (int)(best_mean);
			if (pixel_x < width - 1)
				offset += sprintf(&line_buf[offset], "%d ", filtered_value);
			else
				offset += sprintf(&line_buf[offset], "%d", filtered_value);
		}
		line_buf[offset++] = '\n';
		HAL_UART_Transmit(&huart2, (uint8_t *)line_buf, (uint16_t)offset, 1000);
	}
}
#endif

/* USER CODE END 0 */

/**
 * @brief  The application entry point.
 * @retval int
 */
int main(void)
{

	/* USER CODE BEGIN 1 */

	/* USER CODE END 1 */

	/* MCU Configuration--------------------------------------------------------*/

	/* Reset of all peripherals, Initializes the Flash interface and the Systick. */
	HAL_Init();

	/* USER CODE BEGIN Init */

	/* USER CODE END Init */

	/* Configure the system clock */
	SystemClock_Config();

	/* USER CODE BEGIN SysInit */

	/* USER CODE END SysInit */

	/* Initialize all configured peripherals */
	MX_GPIO_Init();
	MX_USART2_UART_Init();

	/* USER CODE BEGIN 2 */
	/* USER CODE END 2 */

	/* Infinite loop */
	/* USER CODE BEGIN WHILE */
	while (1)
	{
#ifdef STREAMING_MODE
		// ===== MODO STREAMING: Duas fases com buffer 46x90 =====

		// FASE 1: Recebe linhas 0-45 (primeiras 46 linhas)
		for (int i = 0; i < BUFFER_SIZE; i++)
		{
			if (!receive_line_uart(image_buffer[i]))
			{
				printf("ERROR: Failed to receive line %d\n", i);
				break;
			}
		}

		// Delay antes do cabeçalho
		HAL_Delay(750);

		// Envia cabeçalho PGM
		printf("P2\n");
		printf("%d %d\n", IMG_SIZE, IMG_SIZE);
		printf("%d\n", MAX_PIXEL_VALUE);

		// FASE 1: Processa e envia linhas 0-44 (45 linhas)
		// Buffer tem linhas 0-45, então linha 44 tem contexto completo (linha 45 disponível)
		HAL_Delay(150);
		kuwahara_filter_buffered(0, 44, 0);

		// Sinaliza ao host que MCU terminou FASE 1 e está pronto para iniciar FASE 2
		uart_send_str("#READY2#\n");

		// Aguarda comando explícito do host para iniciar FASE 2
		if (!uart_wait_token("#GO2#", 30000))
		{
			printf("ERROR: GO2 timeout\n");
			continue; // recomeça o loop aguardando uma nova rodada
		}

		// FASE 2: Recebe linhas 44-89 (últimas 46 linhas, sobrescreve buffer)
		int ok_phase2 = 1;
		for (int i = 0; i < BUFFER_SIZE; i++)
		{
			int global_line = 44 + i; // Linhas 44 até 89
			if (!receive_line_uart(image_buffer[i]))
			{
				printf("ERROR: Failed to receive line %d\n", global_line);
				ok_phase2 = 0;
				break;
			}
		}

		HAL_Delay(100);

		// FASE 2: Processa e envia linhas 45-89 (45 linhas)
		if (ok_phase2)
		{
			kuwahara_filter_buffered(45, 89, 1);
		}
		else
		{
			printf("SKIP: Phase 2 processing skipped due to incomplete reception.\n");
		}

#else
		// ===== MODO FLASH: Processamento tradicional =====
		kuwahara_filter(IMAGE_DATA_FLASH, KUWAHARA_WINDOW);

		HAL_Delay(5000); // Delay apenas no modo FLASH
#endif
	};
	/* USER CODE END 3 */
}

/**
 * @brief System Clock Configuration
 * @retval None
 */
void SystemClock_Config(void)
{
	RCC_OscInitTypeDef RCC_OscInitStruct = {0};
	RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

	/** Initializes the RCC Oscillators according to the specified parameters
	 * in the RCC_OscInitTypeDef structure.
	 */
	RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
	RCC_OscInitStruct.HSIState = RCC_HSI_ON;
	RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
	RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
	RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSI;
	RCC_OscInitStruct.PLL.PLLMUL = RCC_PLL_MUL12;
	RCC_OscInitStruct.PLL.PREDIV = RCC_PREDIV_DIV1;
	if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
	{
		Error_Handler();
	}

	/** Initializes the CPU, AHB and APB buses clocks
	 */
	RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_SYSCLK | RCC_CLOCKTYPE_PCLK1;
	RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
	RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
	RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV1;

	if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_1) != HAL_OK)
	{
		Error_Handler();
	}
}

/**
 * @brief USART2 Initialization Function
 * @param None
 * @retval None
 */
static void MX_USART2_UART_Init(void)
{

	/* USER CODE BEGIN USART2_Init 0 */

	/* USER CODE END USART2_Init 0 */

	/* USER CODE BEGIN USART2_Init 1 */

	/* USER CODE END USART2_Init 1 */
	huart2.Instance = USART2;
	huart2.Init.BaudRate = 115200;
	huart2.Init.WordLength = UART_WORDLENGTH_8B;
	huart2.Init.StopBits = UART_STOPBITS_1;
	huart2.Init.Parity = UART_PARITY_NONE;
	huart2.Init.Mode = UART_MODE_TX_RX;
	huart2.Init.HwFlowCtl = UART_HWCONTROL_NONE;
	huart2.Init.OverSampling = UART_OVERSAMPLING_16;
	huart2.Init.OneBitSampling = UART_ONE_BIT_SAMPLE_DISABLE;
	huart2.AdvancedInit.AdvFeatureInit = UART_ADVFEATURE_NO_INIT;
	if (HAL_UART_Init(&huart2) != HAL_OK)
	{
		Error_Handler();
	}
	/* USER CODE BEGIN USART2_Init 2 */

	/* USER CODE END USART2_Init 2 */
}

/**
 * @brief GPIO Initialization Function
 * @param None
 * @retval None
 */
static void MX_GPIO_Init(void)
{
	GPIO_InitTypeDef GPIO_InitStruct = {0};
	/* USER CODE BEGIN MX_GPIO_Init_1 */

	/* USER CODE END MX_GPIO_Init_1 */

	/* GPIO Ports Clock Enable */
	__HAL_RCC_GPIOC_CLK_ENABLE();
	__HAL_RCC_GPIOF_CLK_ENABLE();
	__HAL_RCC_GPIOA_CLK_ENABLE();

	/*Configure GPIO pin Output Level */
	HAL_GPIO_WritePin(LD2_GPIO_Port, LD2_Pin, GPIO_PIN_RESET);

	/*Configure GPIO pin : B1_Pin */
	GPIO_InitStruct.Pin = B1_Pin;
	GPIO_InitStruct.Mode = GPIO_MODE_IT_FALLING;
	GPIO_InitStruct.Pull = GPIO_NOPULL;
	HAL_GPIO_Init(B1_GPIO_Port, &GPIO_InitStruct);

	/*Configure GPIO pin : LD2_Pin */
	GPIO_InitStruct.Pin = LD2_Pin;
	GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
	GPIO_InitStruct.Pull = GPIO_NOPULL;
	GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
	HAL_GPIO_Init(LD2_GPIO_Port, &GPIO_InitStruct);

	/* USER CODE BEGIN MX_GPIO_Init_2 */

	/* USER CODE END MX_GPIO_Init_2 */
}

/* USER CODE BEGIN 4 */
/**
 * @brief Redireciona a função printf da biblioteca C para a UART.
 * @param ch Caractere a ser enviado.
 * @return Caractere enviado.
 */
int __io_putchar(int ch)
{
	// Usa um buffer de 8 bits para o caractere
	uint8_t data = (uint8_t)ch;

	// Transmite o caractere via UART2 (huart2)
	// O último parâmetro (100) é o timeout em ms.
	HAL_UART_Transmit(&huart2, &data, 1, 100);

	return ch;
}
/* USER CODE END 4 */

/**
 * @brief  This function is executed in case of error occurrence.
 * @retval None
 */
void Error_Handler(void)
{
	/* USER CODE BEGIN Error_Handler_Debug */
	/* User can add his own implementation to report the HAL error return state */
	__disable_irq();
	while (1)
	{
	}
	/* USER CODE END Error_Handler_Debug */
}
#ifdef USE_FULL_ASSERT
/**
 * @brief  Reports the name of the source file and the source line number
 *         where the assert_param error has occurred.
 * @param  file: pointer to the source file name
 * @param  line: assert_param error line source number
 * @retval None
 */
void assert_failed(uint8_t *file, uint32_t line)
{
	/* USER CODE BEGIN 6 */
	/* User can add his own implementation to report the file name and line number,
		ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
	/* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
