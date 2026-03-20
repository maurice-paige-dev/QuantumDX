from agents import QuantumDxPipeline


def main() -> None:
    pipeline = QuantumDxPipeline()
    result = pipeline.current_model()

    if result.ok:
        print(result.message)
        print(result.payload)
    else:
        print("Unable to load production model")
        print(result.message)


if __name__ == "__main__":
    main()