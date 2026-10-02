import statistics
import time
import requests

API_URL = "https://kentris-github-io-backend-1.onrender.com/api/search"

TEST_QUERIES = [
    "transformer architectures for natural language processing",
    "large language models and scaling laws",
    "retrieval augmented generation for question answering",
    "efficient fine tuning of large language models",
    "reinforcement learning from human feedback",
    "multimodal vision language models",
    "diffusion models for image generation",
    "generative adversarial networks image synthesis",
    "self supervised learning for computer vision",
    "object detection using deep neural networks",
    "graph neural networks for molecular prediction",
    "federated learning and privacy preserving machine learning",
    "adversarial attacks against neural networks",
    "explainable artificial intelligence model interpretability",
    "knowledge distillation for neural networks",
    "neural machine translation with attention mechanisms",
    "speech recognition using deep learning",
    "AI agents and tool use with language models",
    "long context language models",
    "parameter efficient training of neural networks",
]

TOP_K = 5


def run_query(query):
    start = time.perf_counter()

    response = requests.post(
        API_URL,
        json={"query": query},
        timeout=60,
    )

    latency_ms = (time.perf_counter() - start) * 1000

    response.raise_for_status()

    data = response.json()

    return latency_ms, data.get("results", [])


def main():
    latencies = []
    total_results = 0
    relevant_results = 0
    queries_with_relevant_result = 0

    print("=" * 80)
    print("RAG RETRIEVAL BENCHMARK")
    print("=" * 80)

    for number, query in enumerate(TEST_QUERIES, start=1):
        print(f"\n[{number}/{len(TEST_QUERIES)}] {query}")

        try:
            latency_ms, results = run_query(query)

            latencies.append(latency_ms)

            print(f"Latency: {latency_ms:.2f} ms")
            print(f"Results: {len(results)}")

            # Display returned papers
            for i, result in enumerate(results, start=1):
                score = result.get("score", 0)
                title = result.get("title", "Unknown title")

                print(f"  {i}. [{score:.4f}] {title}")

            # Manually evaluate relevance
            relevant_count = 0

            for i, result in enumerate(results, start=1):
                answer = input(
                    f"    Is result #{i} relevant? [y/n]: "
                ).strip().lower()

                if answer == "y":
                    relevant_count += 1

            total_results += len(results)
            relevant_results += relevant_count

            if relevant_count > 0:
                queries_with_relevant_result += 1

        except requests.RequestException as exc:
            print(f"ERROR: {exc}")

    if not latencies:
        print("\nNo successful requests.")
        return

    # Latency statistics
    average_latency = statistics.mean(latencies)
    median_latency = statistics.median(latencies)

    sorted_latencies = sorted(latencies)

    # Nearest-rank 95th percentile
    index = min(
        len(sorted_latencies) - 1,
        int(0.95 * len(sorted_latencies))
    )

    p95_latency = sorted_latencies[index]

    # Relevance statistics
    precision_at_5 = (
        relevant_results / total_results
        if total_results
        else 0
    )

    top_5_relevance = (
        queries_with_relevant_result / len(TEST_QUERIES)
    )

    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)

    print(f"Queries tested:              {len(TEST_QUERIES)}")
    print(f"Successful requests:         {len(latencies)}")
    print(f"Average latency:             {average_latency:.2f} ms")
    print(f"Median latency:              {median_latency:.2f} ms")
    print(f"95th percentile latency:     {p95_latency:.2f} ms")
    print(f"Total results evaluated:     {total_results}")
    print(f"Relevant results:            {relevant_results}")
    print(f"Precision@5:                 {precision_at_5:.2%}")
    print(f"Queries with relevant result:{top_5_relevance:.2%}")


if __name__ == "__main__":
    main()
