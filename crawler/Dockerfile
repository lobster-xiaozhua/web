FROM golang:1.22-alpine AS builder

WORKDIR /build

COPY go.mod go.sum ./
RUN go mod download

COPY . .

RUN CGO_ENABLED=0 GOOS=linux go build -o novel-crawler .

FROM alpine:3.19

RUN apk --no-cache add ca-certificates tzdata

WORKDIR /app

COPY --from=builder /build/novel-crawler .

EXPOSE 50051

VOLUME ["/app/sources", "/app/books"]

CMD ["./novel-crawler"]
