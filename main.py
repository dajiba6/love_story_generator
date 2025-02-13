import argparse
import time
from src.models.novel import Novel
from src.models.ai_client import AIClient
from src.planner.outline_generator import OutlineGenerator
from src.writer.chapter_generator import ChapterGenerator
from src.utils.file_handler import FileHandler


def main():
    start_time = time.time()
    print("Love Novel Generator start...")

    parser = argparse.ArgumentParser(description="Novel Generator")
    parser.add_argument("--config", default="config.yaml", help="Path to config file")
    args = parser.parse_args()

    try:
        # Load configuration
        print(f"Loading config: {args.config}")
        config = FileHandler.load_config(args.config)

        # Initialize novel object
        novel = Novel(config)
        ai_client = AIClient(config["ai_service"])

        # Generate outline
        outline_generator = OutlineGenerator(novel, ai_client)
        outline = outline_generator.generate_outline(novel)

        # Generate all chapters
        chapter_generator = ChapterGenerator(ai_client, config)
        chapters = chapter_generator.generate_chapters(outline, novel)

        # Output results
        end_time = time.time()
        duration = round(end_time - start_time, 2)

        print(f"\nGenerated {len(chapters)} chapters")
        print(f"Total time: {duration} seconds")
        print("\nPreview last chapter content:")
        print("-" * 50)
        print(chapters[-1]["content"][:200] + "...")
        print("-" * 50)

    except Exception as e:
        print(f"\nError: An error occurred while generating the novel")
        print(f"Error message: {str(e)}")
        print(
            "\nPlease check the configuration file and network connection and try again"
        )


if __name__ == "__main__":
    main()
