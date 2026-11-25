from typing import Dict, List, Tuple

from ai_agent import ComplaintAIAgent
from priority_reasoning import prioritize


DEPARTMENT_TO_CATEGORY: Dict[str, str] = {
    "شؤون الطلاب": "Academic & Student Affairs",
    "الخدمات المالية والمصروفات": "Financial Affairs",
    "الشؤون الأكاديمية والامتحانات": "Exams & Results",
    "الخدمات التقنية والمرافق": "Technical Issues",
    "الشكاوى العامة والإدارية": "Administrative Communication",
    "Student Affairs": "Academic & Student Affairs",
    "Financial Affairs": "Financial Affairs",
    "Academic Affairs": "Exams & Results",
    "Technical & Facilities": "Technical Issues",
    "General & Administrative": "Administrative Communication",
}


class ComplaintService:
    def __init__(self, model_path: str = "complaint_agent.joblib"):
        self.agent = ComplaintAIAgent(model_path=model_path)
        self._ensure_ready()

    def _ensure_ready(self):
        if not self.agent.load():
            texts, labels = self.agent.load_from_excel()
            self.agent.train(texts, labels)

    def get_categories(self) -> List[str]:
        return sorted(set(self.agent.labels))

    def classify(self, text: str) -> Tuple[str, float]:
        return self.agent.predict(text)

    def learn_feedback(self, text: str, correct_category: str):
        self.agent.learn(text, correct_category)

    @staticmethod
    def _normalize_confidence_for_reasoning(confidence: float) -> float:
        conf = float(confidence or 0.0)
        if conf > 1.0:
            conf = conf / 100.0
        return max(0.0, min(1.0, conf))

    def estimate_priority(self, text: str, category: str, confidence: float) -> Dict[str, object]:
        mapped_category = DEPARTMENT_TO_CATEGORY.get(category, category)
        normalized_conf = self._normalize_confidence_for_reasoning(confidence)
        result = prioritize(
            text=text or "",
            category=mapped_category or "",
            confidence=normalized_conf,
        )
        return {
            "priority": result["priority"],
            "score": result["score"],
            "reasons": result["reasons"],
            "reason": " | ".join(result["reasons"]),
        }

    def analyze_complaint(self, text: str) -> Dict[str, object]:
        category, confidence = self.classify(text)
        priority_info = self.estimate_priority(text, category, confidence)
        return {
            "category": category,
            "confidence": confidence,
            "priority": priority_info["priority"],
            "score": priority_info["score"],
            "reasons": priority_info["reasons"],
            "reason": priority_info["reason"],
        }

    # إبقاء الاسم القديم كـ alias عشان لو أي صفحة قديمة بتنادي عليه
    def estimate_priority_fallback(self, text: str, category: str, confidence: float) -> Dict[str, object]:
        return self.estimate_priority(text, category, confidence)