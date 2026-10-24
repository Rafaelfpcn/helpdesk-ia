"""Mede o tempo de resposta da API local.

Uso:
  Em um terminal com o servidor rodando:
    python -m scripts.benchmark --n 50
"""

import argparse
import math
import statistics
import time

import httpx

BASE_URL = "http://127.0.0.1:8000"
PAYLOAD = {
    "requester_name": "Ana Souza Teste",
    "requester_email": "ana.teste@exemplo.com",
    "initial_category": "rede",
    "title": "VPN não conecta no notebook",
    "description": "Desde cedo a VPN não conecta e a internet está lenta.",
}


def measure(client: httpx.Client, method: str, path: str, n: int, **kwargs) -> dict:
    times_ms = []
    for _ in range(n):
        start = time.perf_counter()
        client.request(method, path, **kwargs).raise_for_status()
        times_ms.append((time.perf_counter() - start) * 1000)
    times_ms.sort()
    p95_index = max(0, math.ceil(0.95 * len(times_ms)) - 1)
    return {
        "p50": statistics.median(times_ms),
        "p95": times_ms[p95_index],
        "max": times_ms[-1],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark simples da API local.")
    parser.add_argument("--n", type=int, default=50, help="número de requisições por endpoint")
    args = parser.parse_args()

    print(f"Executando benchmark contra {BASE_URL} (n={args.n})...\n")

    with httpx.Client(base_url=BASE_URL, timeout=10) as client:
        scenarios = [
            ("POST /api/tickets (sanitizer + IA mock + DB)", "POST", "/api/tickets", {"json": PAYLOAD}),
            ("GET /api/tickets (listagem de chamados)", "GET", "/api/tickets", {}),
            ("GET /api/metrics (agregações e governança)", "GET", "/api/metrics", {}),
            ("GET /dashboard (renderização Jinja2)", "GET", "/dashboard", {}),
        ]
        print(f"{'Endpoint':50} {'p50 ms':>8} {'p95 ms':>8} {'max ms':>8} (n={args.n})")
        print("-" * 80)
        for label, method, path, kwargs in scenarios:
            try:
                r = measure(client, method, path, args.n, **kwargs)
                print(f"{label:50} {r['p50']:8.1f} {r['p95']:8.1f} {r['max']:8.1f}")
            except Exception as e:
                print(f"{label:50} ERRO: {e}")


if __name__ == "__main__":
    main()
