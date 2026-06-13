#include <stdio.h>
#include <stdlib.h>
#include "cJSON.h"

int main(int argc, char *argv[])
{
    FILE *fp;
    long size;
    char *buffer;
    cJSON *json;

    if (argc < 2) {
        return 1;
    }

    fp = fopen(argv[1], "rb");
    if (!fp) {
        return 0;
    }

    fseek(fp, 0, SEEK_END);
    size = ftell(fp);
    rewind(fp);

    buffer = malloc(size + 1);
    if (!buffer) {
        fclose(fp);
        return 0;
    }

    fread(buffer, 1, size, fp);
    fclose(fp);

    buffer[size] = '\0';

    json = cJSON_Parse(buffer);

    if (json) {
        cJSON_Delete(json);
    }

    free(buffer);

    return 0;
}
