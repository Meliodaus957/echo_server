import socket
from http.server import BaseHTTPRequestHandler
from typing import Dict, Tuple


class HTTPStatusHelper:
    """
    Класс для получения фразы статуса из модуля http
    """
    @staticmethod
    def get_status_phrase(status_code: int) -> str:
        try:
            return f"{status_code} {BaseHTTPRequestHandler.responses[status_code]}"
        except KeyError:
            return "200 OK"  # Если код статуса невалиден


def parse_request(data: str) -> Tuple[str, str, Dict[str, str]]:
    """
    Парсит HTTP-запрос и возвращает метод, путь и заголовки.

    Args:
        data: Строка HTTP-запроса.

    Returns:
        Кортеж из метода, пути и заголовков.
    """
    lines = data.split("\r\n")
    method, path, _ = lines[0].split(" ", 2)
    headers = {}

    for line in lines[1:]:
        if line == "":
            break
        key, value = line.split(": ", 1)
        headers[key] = value

    return method, path, headers


def build_response(status: str, method: str, client_address: Tuple[str, int], headers: Dict[str, str]) -> bytes:
    """
    Создает HTTP-ответ с заголовками и телом ответа.

    Args:
        status: Строка статуса HTTP.
        method: Метод HTTP-запроса.
        client_address: Адрес клиента.
        headers: Заголовки HTTP-запроса.

    Returns:
        Полный HTTP-ответ в виде байтов.
    """
    status_line = f"HTTP/1.1 {status}\r\n"
    response_body = [
        f"Request Method: {method}",
        f"Request Source: {client_address}",
        f"Response Status: {status}",
    ]

    response_body.extend(f"{key}: {value}" for key, value in headers.items())
    body = "\n".join(response_body)

    response_headers = (
        f"Content-Length: {len(body.encode('utf-8'))}\r\n"
        "Content-Type: text/plain\r\n"
        "\r\n"
    )
    return (status_line + response_headers + body).encode("utf-8")


def run_server(host: str = "127.0.0.1", port: int = 8080) -> None:
    """
    Запускает echo-сервер.

    Args:
        host: Хост для прослушивания соединений.
        port: Порт для прослушивания соединений.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
        server_socket.listen()

        print(f"Server is running on {host}:{port}")

        while True:
            client_socket, client_address = server_socket.accept()
            with client_socket:
                print(f"Connection from {client_address}")

                request_data = client_socket.recv(1024).decode("utf-8")
                if not request_data:
                    continue

                method, path, headers = parse_request(request_data)

                # Определяем статус ответа
                status_code = 200
                if "?status=" in path:
                    try:
                        status_code = int(path.split("?status=")[1].split("&")[0])
                    except ValueError:
                        pass

                status_phrase = HTTPStatusHelper.get_status_phrase(status_code)
                response = build_response(status_phrase, method, client_address, headers)

                client_socket.sendall(response)

if __name__ == "__main__":
    run_server()
