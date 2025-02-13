from pathlib import Path
from src.models.novel import Novel
from src.models.ai_client import AIClient
from src.utils.file_handler import FileHandler


class ChapterGenerator:
    def __init__(self, ai_client, config):
        self.ai_client = ai_client
        self.config = config
        self.current_chapter = 1  # 初始化当前章节号

    def generate_chapters(self, outline, novel):
        """Generate all chapters based on outline"""
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
                chapter_content = self._generate_single_chapter(chapter_outline, novel)

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
                chapters.append(
                    {
                        "index": idx,
                        "outline": chapter_outline,
                        "content": chapter_content,
                    }
                )

            except Exception as e:
                print(f"Error generating {chapter_num}: {str(e)}")
                continue

        return chapters

    def _generate_single_chapter(self, chapter_outline, novel):
        """Generate single chapter content in Chinese"""
        prompt = f"""
        基于以下信息生成一个章节的内容：
        小说标题: {novel.config.title}
        小说语言: {novel.config.language}
        总章节数: {novel.config.total_chapters}
        当前章节: {self.current_chapter}
        字数要求: {novel.config.words_per_chapter}字
        小说类型: {novel.config.genre}
        感情基调: {novel.config.tone}
        女主角: {novel.config.female_lead.name}，性格：{novel.config.female_lead.personality}
        男主角: {novel.config.male_lead.name}，性格：{novel.config.male_lead.personality}
        章节大纲: {chapter_outline}
        
        要求：
        1. 生成详细的章节内容，包含对话和描写
        2. 字数控制在{novel.config.words_per_chapter}字左右
        3. 符合{novel.config.tone}的感情基调
        4. 情节自然流畅
        5. 注意人物性格特点的体现
        6. 直接输出小说内容，不要输出任何解释或说明
        """

        response = self.ai_client.generate(prompt)
        # 过滤掉<think>标签中的内容
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
