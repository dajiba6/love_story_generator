from dataclasses import dataclass
from typing import List, Dict
from pathlib import Path


@dataclass
class Character:
    name: str
    personality: str


@dataclass
class NovelConfig:
    language: str
    title: str
    total_chapters: int
    words_per_chapter: int
    genre: str
    tone: str
    plot_elements: List[str]
    female_lead: Character
    male_lead: Character


class Novel:
    def __init__(self, config: Dict):
        self.female_lead = Character(**config["characters"]["female_lead"])
        self.male_lead = Character(**config["characters"]["male_lead"])

        self.config = NovelConfig(
            language=config.get("basic", {}).get("language", "zh"),
            title=config["novel"]["title"],
            total_chapters=config["novel"]["total_chapters"],
            words_per_chapter=config["novel"]["words_per_chapter"],
            genre=config["story_style"]["genre"],
            tone=config["story_style"]["tone"],
            plot_elements=config["story_style"]["plot_elements"],
            female_lead=self.female_lead,
            male_lead=self.male_lead,
        )

        # 创建输出目录结构
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)

        self.novel_dir = self.output_dir / self.config.title
        self.novel_dir.mkdir(exist_ok=True)

        self.outline_file = self.novel_dir / "outline.txt"
