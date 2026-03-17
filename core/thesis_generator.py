"""论文生成核心引擎：分6阶段调用 Claude API"""
import anthropic
import config
from core.prompts import *

class ThesisGenerator:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        self.sections = {}

    def _call(self, system: str, user: str, max_tokens: int = None) -> str:
        for attempt in range(3):
            try:
                resp = self.client.messages.create(
                    model=config.MODEL,
                    max_tokens=max_tokens or config.MAX_TOKENS,
                    system=system,
                    messages=[{"role": "user", "content": user}],
                )
                return resp.content[0].text
            except Exception as e:
                if attempt == 2:
                    raise
                continue

    def generate_outline(self, proposal: str, data_summary: str) -> str:
        text = self._call(SYSTEM_PROMPT, OUTLINE_PROMPT.format(
            proposal=proposal[:6000], data_summary=data_summary[:2000]
        ))
        self.sections["outline"] = text
        return text

    def generate_literature(self) -> str:
        outline = self.sections.get("outline", "")
        topic = outline[:500]
        text = self._call(SYSTEM_PROMPT, LITERATURE_PROMPT.format(
            outline=outline[:3000], topic=topic
        ))
        self.sections["literature"] = text
        return text

    def generate_methodology(self, data_summary: str) -> str:
        text = self._call(SYSTEM_PROMPT, METHODOLOGY_PROMPT.format(
            outline=self.sections.get("outline", "")[:3000],
            data_summary=data_summary[:3000]
        ))
        self.sections["methodology"] = text
        return text

    def generate_results(self, analysis_results: str) -> str:
        text = self._call(SYSTEM_PROMPT, RESULTS_PROMPT.format(
            outline=self.sections.get("outline", "")[:2000],
            analysis_results=analysis_results[:5000]
        ))
        self.sections["results"] = text
        return text

    def generate_conclusion(self) -> str:
        results_summary = self.sections.get("results", "")[:2000]
        text = self._call(SYSTEM_PROMPT, CONCLUSION_PROMPT.format(
            outline=self.sections.get("outline", "")[:2000],
            results_summary=results_summary
        ))
        self.sections["conclusion"] = text
        return text

    def generate_abstract(self) -> str:
        text = self._call(SYSTEM_PROMPT, ABSTRACT_PROMPT.format(
            outline=self.sections.get("outline", "")[:2000],
            conclusion=self.sections.get("conclusion", "")[:2000]
        ))
        self.sections["abstract"] = text
        return text
