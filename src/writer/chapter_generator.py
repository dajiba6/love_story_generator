from pathlib import Path
from collections import deque
from src.models.novel import Novel
from src.models.ai_client import AIClient
from src.utils.file_handler import FileHandler


class ChapterGenerator:
    def __init__(self, ai_client, config):
        self.ai_client = ai_client
        self.config = config
        self.current_chapter = 1

        # 使用deque来存储固定数量的前文章节
        max_previous = self.config.get("generation", {}).get("max_previous_chapters", 1)
        self.previous_chapters = deque(maxlen=max_previous)

    def generate_chapters(self, outline, novel):
        """Generate all chapters based on outline"""
        # 加载世界观设定
        world_setting = self._load_world_setting(novel.novel_dir)

        chapter_config = self.config.get("generation", {}).get("chapters", {})
        generate_all = chapter_config.get("generate_all", True)
        start_idx = chapter_config.get("start_index", 1)
        end_idx = chapter_config.get("end_index")

        # Split and clean outline lines
        chapter_items = [line.strip() for line in outline.split("\n") if line.strip()]

        if not generate_all:
            # Generate chapters based on configured range
            end_idx = end_idx or len(chapter_items)
            chapter_items = chapter_items[start_idx - 1 : end_idx]

        chapters = []
        for idx, chapter_outline in enumerate(chapter_items, start=start_idx):
            try:
                chapter_num = f"Chapter {idx}"
                print(f"\nGenerating {chapter_num}...")

                # 生成章节内容
                self.current_chapter = idx
                chapter_content = self._generate_single_chapter(
                    chapter_outline=chapter_outline,
                    novel=novel,
                    world_setting=world_setting,
                    full_outline=outline,
                )

                # 从大纲中提取章节标题
                title = (
                    chapter_outline.split("：")[0].split(" ")[1]
                    if "：" in chapter_outline
                    else None
                )

                # 保存章节
                filepath = FileHandler.save_chapter(
                    novel_dir=novel.novel_dir,
                    content=chapter_content,
                    chapter_num=idx,
                    title=title,
                )
                print(f"Saved {chapter_num} to {filepath}")

                # 记录章节信息
                chapter_info = {
                    "index": idx,
                    "outline": chapter_outline,
                    "content": chapter_content,
                }
                chapters.append(chapter_info)
                self.previous_chapters.append(chapter_info)  # 自动保持固定长度

            except Exception as e:
                print(f"Error generating {chapter_num}: {str(e)}")
                continue

        return chapters

    def _load_world_setting(self, novel_dir: Path) -> str:
        """Load world setting from file"""
        setting_file = novel_dir / "world_setting.txt"
        if not setting_file.exists():
            raise FileNotFoundError("World setting file not found")
        return setting_file.read_text(encoding="utf-8")

    def _get_previous_chapter_summary(self) -> str:
        """Get summary of previous chapters"""
        if not self.previous_chapters:
            return "这是第一章，没有前文内容。"

        summaries = []
        for chapter in self.previous_chapters:
            summary = f"第{chapter['index']}章 {chapter['outline']}\n"
            summary += f"内容概要：{chapter['content']}...\n"  # 添加内容概要
            summaries.append(summary)

        return "\n".join(summaries)

    def _generate_single_chapter(
        self, chapter_outline, novel, world_setting, full_outline
    ):
        """Generate single chapter content with full context"""
        previous_content = self._get_previous_chapter_summary()

        prompt = f"""
        基于以下背景信息生成小说章节，要求内容连贯自然，适合读者阅读：

        1. 世界观设定：
        {world_setting}

        2. 完整大纲：
        {full_outline}

        3. 前文概要：
        {previous_content}

        4. 当前章节信息：
        - 小说标题: {novel.config.title}
        - 当前章节: {self.current_chapter}
        - 字数要求: {novel.config.words_per_chapter}字
        - 小说类型: {novel.config.genre}
        - 感情基调: {novel.config.tone}
        - 女主角: {novel.config.female_lead.name}，性格：{novel.config.female_lead.personality}
        - 男主角: {novel.config.male_lead.name}，性格：{novel.config.male_lead.personality}
        - 本章大纲: {chapter_outline}

        创作要求：
        1. 场景描写：
        - 选择1-2个核心场景，不要频繁跳转
        - 场景细节要丰富，渲染氛围
        - 通过环境烘托人物心理

        2. 情节发展：
        - 以一条主要情节线索为主
        - 情节推进要循序渐进，不要跳跃
        - 每个转折都要有合理铺垫
        - 人物对话和行为要符合性格特点

        3. 情感表达：
        - 通过细节体现情感变化
        - 保持情感基调的连贯性
        - 感情发展要自然，不要突兀

        4. 写作要求：
        - 保持与前文的连贯性
        - 为下章内容做好铺垫
        - 直接输出小说内容，不要输出任何解释说明
        """

        response = self.ai_client.generate(prompt)
        return self._filter_think_content(response)

    def _filter_think_content(self, content: str) -> str:
        """Filter out content between <think> tags"""
        import re

        # 移除<think>标签及其内容
        filtered_content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL)
        # 清理可能的多余空行
        filtered_content = "\n".join(
            line for line in filtered_content.splitlines() if line.strip()
        )

        return filtered_content.strip()
