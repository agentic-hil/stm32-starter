#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define REG32(address) (*(volatile uint32_t *)(address))

#define RCC_AHB1ENR REG32(0x40023830U)
#define RCC_APB1ENR REG32(0x40023840U)
#define GPIOA_MODER REG32(0x40020000U)
#define GPIOA_AFRL REG32(0x40020020U)
#define USART2_SR REG32(0x40004400U)
#define USART2_DR REG32(0x40004404U)
#define USART2_BRR REG32(0x40004408U)
#define USART2_CR1 REG32(0x4000440CU)

#define GPIOA_ENABLE (1U << 0)
#define USART2_ENABLE (1U << 17)
#define USART2_TX_PIN 2U
#define USART2_RX_PIN 3U
#define USART_SR_RXNE (1U << 5)
#define USART_SR_TXE (1U << 7)
#define USART_CR1_RE (1U << 2)
#define USART_CR1_TE (1U << 3)
#define USART_CR1_UE (1U << 13)
#define USART2_BRR_115200_PCLK16MHZ 139U
#define COMMAND_CAPACITY 32U

#define SCB_CPACR REG32(0xE000ED88U)
#define CPACR_CP10_CP11_FULL (0xFU << 20)

static bool diagnostic_active;

void SystemInit(void)
{
    /* Reset defaults use the 16 MHz HSI clock. */

    /* This target is built for the hard-float ABI, so the FPU has to be on
       before main. Nothing here uses a float today; a fix that introduces one
       would hard fault instead of failing a test. */
    SCB_CPACR |= CPACR_CP10_CP11_FULL;
    __asm volatile("dsb" ::: "memory");
    __asm volatile("isb" ::: "memory");
}

static void uart_init(void)
{
    RCC_AHB1ENR |= GPIOA_ENABLE;
    RCC_APB1ENR |= USART2_ENABLE;

    GPIOA_MODER &= ~((3U << (USART2_TX_PIN * 2U)) | (3U << (USART2_RX_PIN * 2U)));
    GPIOA_MODER |= (2U << (USART2_TX_PIN * 2U)) | (2U << (USART2_RX_PIN * 2U));
    GPIOA_AFRL &= ~((0xFU << (USART2_TX_PIN * 4U)) | (0xFU << (USART2_RX_PIN * 4U)));
    GPIOA_AFRL |= (7U << (USART2_TX_PIN * 4U)) | (7U << (USART2_RX_PIN * 4U));

    USART2_CR1 = 0U;
    USART2_BRR = USART2_BRR_115200_PCLK16MHZ;
    USART2_CR1 = USART_CR1_RE | USART_CR1_TE | USART_CR1_UE;
}

static void uart_write_char(char value)
{
    while ((USART2_SR & USART_SR_TXE) == 0U) {
    }
    USART2_DR = (uint32_t)(uint8_t)value;
}

static void uart_write(const char *text)
{
    while (*text != '\0') {
        uart_write_char(*text);
        ++text;
    }
}

static char uart_read_char(void)
{
    while ((USART2_SR & USART_SR_RXNE) == 0U) {
    }
    return (char)(uint8_t)USART2_DR;
}

static bool text_equals(const char *left, const char *right)
{
    while ((*left != '\0') && (*right != '\0') && (*left == *right)) {
        ++left;
        ++right;
    }
    return (*left == '\0') && (*right == '\0');
}

static void report_status(void)
{
    if (diagnostic_active) {
        uart_write("{\"state\":\"DEGRADED\",\"diagnostic\":\"E_SELF_TEST\"}\r\n");
    } else {
        uart_write("{\"state\":\"READY\",\"diagnostic\":\"NONE\"}\r\n");
    }
}

static void handle_command(const char *command)
{
    if (text_equals(command, "DIAG ENABLE")) {
        diagnostic_active = true;
    } else if (text_equals(command, "DIAG CLEAR")) {
        diagnostic_active = false;
    }
    report_status();
}

int main(void)
{
    char command[COMMAND_CAPACITY];
    size_t length = 0U;

    uart_init();
    uart_write("{\"event\":\"boot\",\"firmware\":\"stm32-starter\"}\r\n");

    for (;;) {
        char received = uart_read_char();
        if ((received == '\n') || (received == '\r')) {
            if (length > 0U) {
                command[length] = '\0';
                handle_command(command);
                length = 0U;
            }
        } else if (length < (COMMAND_CAPACITY - 1U)) {
            command[length] = received;
            ++length;
        } else {
            length = 0U;
        }
    }
}
