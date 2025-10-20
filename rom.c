#define SERIAL ((volatile uint8_t*)0xffff)

void print(const char* str) {
    while (*str)
        *SERIAL = *str++;
}

// Entry point at $d000
void __fastcall__ reset(void) {
    static const char message[] = "Hello, world!";
    print(message);

    for (;;) ; // infinite loop
}

// Put the reset vector at $fffc
#pragma rodata-name ("VECTORS")
const void (*const reset_vector)(void) = reset;