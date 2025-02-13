from pathlib import Path
import yaml
from typing import Dict, Tuple


class FileHandler:
    @staticmethod
    def load_config(config_path: str) -> Dict:
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    @staticmethod
    def save_outline(outline_file: Path, outline: str):
        if outline_file.exists():
            previous_outline = outline_file.read_text(encoding="utf-8")
            if previous_outline and not previous_outline.endswith("\n"):
                outline = "\n" + outline
        outline_file.write_text(outline + "\n", encoding="utf-8")

    @staticmethod
    def save_chapter(
        novel_dir: Path, content: str, chapter_num: int, title: str = None
    ) -> Path:
        """Save chapter content to file

        Args:
            novel_dir: Directory to save the chapter
            content: Chapter content
            chapter_num: Chapter number
            title: Chapter title (optional)

        Returns:
            Path to saved file
        """
        if title:
            filename = f"{chapter_num:03d}_{title}.txt"
        else:
            filename = f"{chapter_num:03d}.txt"

        filepath = novel_dir / filename
        filepath.write_text(content, encoding="utf-8")
        return filepath

    @staticmethod
    def extract_chapter_title(outline: str, chapter_num: int = 1) -> str:
        """
        从大纲中提取章节标题，如果无法提取则返回默认格式的标题

        Args:
            outline: 大纲内容
            chapter_num: 当前章节号，默认为1

        Returns:
            str: 章节标题
        """
        return (
            outline.split("：")[1].split("\n")[0]
            if "：" in outline
            else f"第{chapter_num}章"
        )
