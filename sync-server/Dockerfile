FROM golang:1.22-alpine AS builder

WORKDIR /app
RUN apk add --no-cache gcc musl-dev sqlite-dev
COPY . .
RUN go mod init zenith-sync-server || true
RUN go get github.com/mattn/go-sqlite3
RUN CGO_ENABLED=1 GOOS=linux go build -ldflags="-s -w" -o zenith-sync .

FROM alpine:latest
RUN apk add --no-cache sqlite-libs ca-certificates
WORKDIR /root/
COPY --from=builder /app/zenith-sync .

EXPOSE 8080
VOLUME ["/root/data"]
ENV DB_PATH=/root/data/zenith_sync.db
ENV PORT=8080

CMD ["./zenith-sync"]
