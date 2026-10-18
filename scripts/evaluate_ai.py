import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from app.services.ai import MockAiProvider, sanitize_text  # noqa: E402


def load_dataset(path: str = "data/eval_dataset.json") -> list[dict]:
    dataset_path = ROOT / path

    with open(dataset_path, "r", encoding="utf-8") as file:
        return json.load(file)


def evaluate(dataset: list[dict]) -> dict:
    provider = MockAiProvider()

    total = 0
    correct_category = 0
    correct_priority = 0
    correct_both = 0

    errors = []

    for item in dataset:
        title = item["title"]
        description = item["description"]

        expected_category = item["expected_category"].lower()
        expected_priority = item["expected_priority"].lower()

        sanitized_description = sanitize_text(description)

        result = provider.analyze(
            title=title,
            description=sanitized_description,
        )

        predicted_category = result.suggested_category.lower()
        predicted_priority = result.suggested_priority.lower()

        category_ok = predicted_category == expected_category
        priority_ok = predicted_priority == expected_priority

        total += 1

        if category_ok:
            correct_category += 1

        if priority_ok:
            correct_priority += 1

        if category_ok and priority_ok:
            correct_both += 1

        if not category_ok or not priority_ok:
            errors.append(
                {
                    "id": item["id"],
                    "title": title,
                    "expected_category": expected_category,
                    "predicted_category": predicted_category,
                    "expected_priority": expected_priority,
                    "predicted_priority": predicted_priority,
                    "confidence": result.confidence,
                }
            )

    return {
        "total": total,
        "correct_category": correct_category,
        "correct_priority": correct_priority,
        "correct_both": correct_both,
        "category_accuracy": correct_category / total if total else 0,
        "priority_accuracy": correct_priority / total if total else 0,
        "both_accuracy": correct_both / total if total else 0,
        "errors": errors,
    }


def main():
    dataset = load_dataset()
    result = evaluate(dataset)

    print("=== Avaliação da IA ===")
    print(f"Total de casos: {result['total']}")
    print(f"Acertos de categoria: {result['correct_category']}")
    print(f"Acertos de prioridade: {result['correct_priority']}")
    print(f"Acertos completos: {result['correct_both']}")
    print(f"Acurácia de categoria: {result['category_accuracy']:.2%}")
    print(f"Acurácia de prioridade: {result['priority_accuracy']:.2%}")
    print(f"Acurácia completa: {result['both_accuracy']:.2%}")

    if result["errors"]:
        print("\n=== Casos com erro ===")
        print(json.dumps(result["errors"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
