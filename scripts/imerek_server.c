#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <pthread.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <fcntl.h>
#include <errno.h>
#include <android/log.h>

#define TAG "ZenithImerek"
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, TAG, __VA_ARGS__)
#define LOGE(...) __android_log_print(ANDROID_LOG_ERROR, TAG, __VA_ARGS__)

#define SERVER_PORT 9936
#define BUFFER_SIZE 65536

static void send_cors_response(int client_fd, int status, const char* status_text, const char* content_type, const char* body) {
    char header[2048];
    int body_len = body ? strlen(body) : 0;
    snprintf(header, sizeof(header),
        "HTTP/1.1 %d %s\r\n"
        "Access-Control-Allow-Origin: *\r\n"
        "Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS\r\n"
        "Access-Control-Allow-Headers: Content-Type, Authorization, x-avukat-config, x-calisan-config, x-oturum-token, x-eklenti-yetenek, x-relayed\r\n"
        "Content-Type: %s\r\n"
        "Content-Length: %d\r\n"
        "Connection: close\r\n"
        "\r\n",
        status, status_text, content_type, body_len);
    write(client_fd, header, strlen(header));
    if (body_len > 0) {
        write(client_fd, body, body_len);
    }
}

static void handle_client(int client_fd) {
    char buffer[BUFFER_SIZE];
    ssize_t bytes_read = read(client_fd, buffer, sizeof(buffer) - 1);
    if (bytes_read <= 0) {
        close(client_fd);
        return;
    }
    buffer[bytes_read] = '\0';

    char method[16], path[256];
    if (sscanf(buffer, "%15s %255s", method, path) < 2) {
        close(client_fd);
        return;
    }

    LOGI("Request: %s %s", method, path);

    // Handle OPTIONS (CORS preflight)
    if (strcmp(method, "OPTIONS") == 0) {
        send_cors_response(client_fd, 204, "No Content", "text/plain", "");
        close(client_fd);
        return;
    }

    // Handle GET endpoints
    if (strcmp(method, "GET") == 0) {
        if (strstr(path, "/serverInfo") != NULL) {
            const char* resp = "{\"serverVersion\":\"3.11.7\",\"role\":\"yerel\",\"mainAd\":\"Zenith Built-in UYAP Server\",\"mainAtanmamis\":0}";
            send_cors_response(client_fd, 200, "OK", "application/json", resp);
        } else if (strstr(path, "/connect") != NULL) {
            const char* resp = "{\"ok\":true,\"success\":true,\"message\":\"Zenith dahili sunucusuna baglanildi.\"}";
            send_cors_response(client_fd, 200, "OK", "application/json", resp);
        } else if (strstr(path, "/bagimsizDurum") != NULL) {
            const char* resp = "{\"durum\":\"bagimsiz\",\"izinVerildi\":true}";
            send_cors_response(client_fd, 200, "OK", "application/json", resp);
        } else {
            const char* resp = "{\"serverVersion\":\"3.11.7\",\"status\":\"ok\"}";
            send_cors_response(client_fd, 200, "OK", "application/json", resp);
        }
        close(client_fd);
        return;
    }

    // Handle POST endpoints
    if (strcmp(method, "POST") == 0) {
        if (strstr(path, "/auth/login") != NULL) {
            const char* resp = "{\"success\":true,\"token\":\"zenith-builtin-token\",\"rol\":\"ADMIN\"}";
            send_cors_response(client_fd, 200, "OK", "application/json", resp);
        } else if (strstr(path, "/auth/me") != NULL) {
            const char* resp = "{\"success\":true,\"calisan\":{\"kullaniciAdi\":\"admin\",\"ad\":\"Avukat\",\"rol\":\"ADMIN\"}}";
            send_cors_response(client_fd, 200, "OK", "application/json", resp);
        } else if (strstr(path, "/SQL/") != NULL || strstr(path, "/query") != NULL || strstr(path, "/exec") != NULL || strstr(path, "/run") != NULL) {
            const char* resp = "{\"success\":true,\"ok\":true,\"rows\":[],\"rowCount\":0,\"changes\":0}";
            send_cors_response(client_fd, 200, "OK", "application/json", resp);
        } else {
            const char* resp = "{\"success\":true}";
            send_cors_response(client_fd, 200, "OK", "application/json", resp);
        }
        close(client_fd);
        return;
    }

    send_cors_response(client_fd, 404, "Not Found", "application/json", "{\"error\":\"not_found\"}");
    close(client_fd);
}

static void* imerek_server_loop(void* arg) {
    (void)arg;
    int server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) {
        LOGE("Failed to create socket: %s", strerror(errno));
        return NULL;
    }

    int opt = 1;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = inet_addr("127.0.0.1");
    addr.sin_port = htons(SERVER_PORT);

    if (bind(server_fd, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        LOGE("Bind failed on port %d: %s", SERVER_PORT, strerror(errno));
        close(server_fd);
        return NULL;
    }

    if (listen(server_fd, 32) < 0) {
        LOGE("Listen failed: %s", strerror(errno));
        close(server_fd);
        return NULL;
    }

    LOGI("Zenith Imerek Built-in UYAP Server is active and listening on 127.0.0.1:%d", SERVER_PORT);

    while (1) {
        struct sockaddr_in client_addr;
        socklen_t client_len = sizeof(client_addr);
        int client_fd = accept(server_fd, (struct sockaddr*)&client_addr, &client_len);
        if (client_fd >= 0) {
            handle_client(client_fd);
        }
    }
    return NULL;
}

// Automatically runs when libimerek.so is loaded by Android runtime!
__attribute__((constructor))
static void start_imerek_builtin_daemon(void) {
    LOGI("Initializing Zenith Imerek UYAP Native Bridge Daemon...");
    pthread_t thread;
    pthread_create(&thread, NULL, imerek_server_loop, NULL);
    pthread_detach(thread);
}
