from agents import QuantumDxPipeline


def main() -> None:
    pipeline = QuantumDxPipeline()
    result = pipeline.retrain(min_accuracy=0.75)

    if result.ok:
        print("Retraining succeeded")
        print(result.payload)
    else:
        print("Retraining failed")
        print(result.message)
        if result.payload:
            print(result.payload)


if __name__ == "__main__":
    main()