from src.models.novel import Novel
from src.models.ai_client import AIClient
from src.utils.file_handler import FileHandler
from pathlib import Path
import re


class OutlineGenerator:
    def __init__(self, novel: Novel, ai_client: AIClient):
        self.novel = novel
        self.ai_client = ai_client

    def generate_outline(self, novel) -> str:
        """Generate novel outline based on world setting"""
        print("\nStarting to generate world setting...")
        # 1. 生成世界观架构
        world_setting = self._generate_world_setting()
        world_setting = self._filter_think_content(world_setting)
        self._save_world_setting(world_setting)

        print("\nStarting to generate novel outline...")
        # 2. 基于世界观生成大纲
        outline = self._generate_outline_based_on_setting(world_setting)
        outline = self._filter_think_content(outline)

        # 处理大纲格式
        processed_outline = self._process_outline(outline)

        # 保存大纲
        FileHandler.save_outline(novel.outline_file, processed_outline)
        print(f"Novel outline generated and saved to {novel.outline_file}")

        return processed_outline

    def _filter_think_content(self, content: str) -> str:
        """Filter out content between <think> tags"""
        # 移除<think>标签及其内容
        filtered_content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL)
        # 清理可能的多余空行
        filtered_content = "\n".join(
            line for line in filtered_content.splitlines() if line.strip()
        )

        return filtered_content.strip()

    def _generate_world_setting(self) -> str:
        """Generate world setting and background"""
        config = self.novel.config
        prompt = f"""请为这部小说创建详细的世界观架构，包括：

1. 故事背景：
- 时代背景
- 社会环境
- 重要场景描写

2. 人物设定：
- 女主角 {config.female_lead.name}：{config.female_lead.personality}
  - 详细的性格特点
  - 家庭背景
  - 社会地位
  - 重要经历
- 男主角 {config.male_lead.name}：{config.male_lead.personality}
  - 详细的性格特点
  - 家庭背景
  - 社会地位
  - 重要经历
- 其他重要配角

3. 核心矛盾：
- 主要情感冲突
- 次要情节冲突
- 内心/外部矛盾

4. 感情线索：
- 男女主角相识发展线
- 情感转折点
- {config.tone}基调的体现

要求：
- 符合{config.genre}的风格特点
- 为后续{config.total_chapters}章的内容做好铺垫
- 包含这些情节元素：{', '.join(config.plot_elements)}
- 世界观要完整且自洽
- 输出要分段落，层次分明
- 直接输出内容，不要包含任何解释说明
"""
        return self.ai_client.generate(prompt)

    def _save_world_setting(self, world_setting: str):
        """Save world setting to file"""
        setting_file = self.novel.novel_dir / "world_setting.txt"
        setting_file.write_text(world_setting, encoding="utf-8")
        print(f"World setting saved to {setting_file}")

    def _generate_outline_based_on_setting(self, world_setting: str) -> str:
        """Generate outline based on world setting"""
        config = self.novel.config
        prompt = f"""基于以下世界观架构，生成一个{config.total_chapters}章的详细故事大纲：

世界观设定：
{world_setting}

要求：
1. 总体要求：
- 总共{config.total_chapters}章
- 符合{config.genre}的风格特点
- 体现{config.tone}的感情基调
- 合理安排情节元素：{', '.join(config.plot_elements)}

2. 结构要求：
- 起承转合分明
- 感情发展循序渐进
- 情节推进自然流畅
- 各章节内容详略得当

3. 输出格式：
- 每章大纲必须只占一行
- 每行格式为：第X章 章节名：章节内容概要
- 不要输出多余的空行
- 不要输出序号或其他格式
- 直接输出内容，不要包含任何解释说明

示例格式：
第1章 初见：男女主角在咖啡厅偶遇，开启故事
第2章 误会：一场误会导致两人产生矛盾
...
"""
        return self.ai_client.generate(prompt)

    def _process_outline(self, outline: str) -> str:
        """Process outline format to ensure one chapter per line"""
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
