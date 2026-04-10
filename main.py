import logging

from detector import predict_message, train_model

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main() -> None:
    try:
        artifacts = train_model()
        dataset = artifacts["dataset"]

        print("Dataset size:", dataset.shape)
        print(dataset["label"].value_counts().rename({0: "ham", 1: "spam"}))
        print(f"\nModel Accuracy: {artifacts['accuracy']:.4f}")
        print("\nEnter a message to check:")

        user_input = input().strip()

        if not user_input:
            print("Error: Please enter a message.")
            return

        result = predict_message(
            user_input,
            artifacts["model"],
            artifacts["vectorizer"],
        )

        if result["is_scam"]:
            print("\n⚠️  Possible Scam Message")
        else:
            print("\n✓ Message looks Safe")

        print(f"Scam Probability: {result['scam_probability']:.2%}")

        if result["keyword_hits"]:
            print("Suspicious keywords:", ", ".join(result["keyword_hits"]))
        else:
            print("No suspicious keywords found.")

        logger.info(
            f"Analysis completed. Result: {'Scam' if result['is_scam'] else 'Safe'}"
        )
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()
