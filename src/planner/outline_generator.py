from src.models.novel import Novel
from src.models.ai_client import AIClient
from src.utils.file_handler import FileHandler


class OutlineGenerator:
    def __init__(self, novel: Novel, ai_client: AIClient):
        self.novel = novel
        self.ai_client = ai_client

    def generate_outline(self, novel) -> str:
        """Generate novel outline"""
        print("\nStarting to generate novel outline...")
        prompt = self._generate_outline_prompt()
        outline = self.ai_client.generate(prompt)

        # Process outline format
        processed_outline = self._process_outline(outline)

        # Save outline
        FileHandler.save_outline(novel.outline_file, processed_outline)
        print(f"Novel outline generated and saved to {novel.outline_file}")

        return processed_outline

    def _generate_outline_prompt(self) -> str:
        """生成大纲提示词"""
        config = self.novel.config
        return f"""请为一部言情小说生成详细的章节大纲，要求：
        - 小说标题：{config.title}
        - 小说语言：{config.language}
        - 总章节数：{config.total_chapters}章
        - 女主角名字：{config.female_lead.name}，性格：{config.female_lead.personality}
        - 男主角名字：{config.male_lead.name}，性格：{config.male_lead.personality}
        - 故事类型：{config.genre}
        - 感情基调：{config.tone}
        - 重要剧情元素：{', '.join(config.plot_elements)}
        
        输出格式要求：
        - 每章大纲必须只占一行
        - 每行格式为：第X章 章节名：章节内容概要
        - 不要输出多余的空行
        - 不要输出序号或其他格式
        
        示例格式：
        第1章 初见：男女主角在咖啡厅偶遇，开启故事
        第2章 误会：一场误会导致两人产生矛盾
        ...
        """

    def _process_outline(self, outline: str) -> str:
        """处理大纲格式，确保每章节占一行"""
        # 移除多余的空行
        lines = [line.strip() for line in outline.split("\n") if line.strip()]

        # 验证每行格式
        processed_lines = []
        for line in lines:
            # 确保每行都以"第X章"开头
            if not line.startswith("第") or "章" not in line:
                continue
            processed_lines.append(line)

        # 返回处理后的大纲
        return "\n".join(processed_lines)
