/*
 * AFL++ fuzzing harness — license validation library
 *
 * Build:  make fuzzer
 * Run:    afl-fuzz -i corpus/ -o findings/ -- ./fuzzer @@
 *
 * AFL++ is launching, the binary runs, but the fuzzer makes no progress.
 * Something is wrong. Find the issues and fix them.
 */

#include "license.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

static uint32_t calc_crc32(const uint8_t *data, size_t size) {
    uint32_t crc = 0xFFFFFFFF;
    for (size_t i = 0; i < size; i++) {
        crc ^= data[i];
        for (int j = 0; j < 8; j++) {
            crc = (crc >> 1) ^ (0xEDB88320 & (-(crc & 1)));
        }
    }
    return ~crc;
}

static void set_crc(uint8_t *buffer, size_t total_size) {
    uint32_t crc = calc_crc32(buffer + 4, total_size - 4);
    buffer[0] = (crc >> 24) & 0xFF;
    buffer[1] = (crc >> 16) & 0xFF;
    buffer[2] = (crc >> 8) & 0xFF;
    buffer[3] = crc & 0xFF;
}

int main(int argc, char *argv[])
{
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <input_file>\n", argv[0]);
        return 1;
    }

    FILE *f = fopen(argv[1], "rb");
    if (!f)
        return 0;

    uint8_t buf[65536];
    size_t len = fread(buf, 1, sizeof(buf), f);
    fclose(f);

    if (len >= 4) {
	set_crc(buf, len);
    }

    if (init_license_system()){
        validate_license(buf, len);
        cleanup_license_system();
    }
    
    return 0;
}
