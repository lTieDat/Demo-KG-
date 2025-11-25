import openai
import streamlit as st
from typing import List, Dict, Any, Optional


class LLMExplainer:
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model

    def explain_recommendations(
        self,
        student_code: str,
        recommendations: List[Dict],
        user_history: Optional[List[str]] = None,
    ) -> str:
        """
        Giải thích kết quả gợi ý bằng LLM

        Args:
            student_code: Mã sinh viên
            recommendations: Danh sách bài tập được gợi ý
            user_history: Lịch sử làm bài của sinh viên (optional)

        Returns:
            Giải thích từ LLM
        """
        # Tạo prompt context
        context = self._build_context(student_code, recommendations, user_history)

        prompt = f"""
        Bạn là một trợ lý giáo dục thông minh chuyên về lập trình. Hãy giải thích tại sao hệ thống gợi ý những bài tập này cho sinh viên.

        {context}

        Hãy viết một đoạn giải thích ngắn gọn (2-3 câu) về:
        1. Tại sao những bài tập này phù hợp với sinh viên dựa trên chủ đề và độ khó
        2. Sự liên quan và thứ tự logic giữa các chủ đề trong danh sách gợi ý
        3. Lời khuyên về cách tiếp cận hoặc thứ tự làm bài

        Viết bằng tiếng Việt, phong cách thân thiện và dễ hiểu. Tập trung vào giá trị giáo dục.
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=400,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Không thể tạo giải thích: {str(e)}"

    def _build_context(
        self,
        student_code: str,
        recommendations: List[Dict],
        user_history: Optional[List[str]],
    ) -> str:
        """Xây dựng context cho prompt"""
        context = f"Mã sinh viên: {student_code}\n\n"
        context += "Danh sách bài tập được gợi ý (theo thứ tự ưu tiên):\n"

        for i, rec in enumerate(recommendations, 1):
            context += f"{i}. {rec['title']} - Chủ đề: {rec['topic']} - Độ khó: {rec['difficulty']} - Điểm: {rec['score']:.3f}\n"

        if user_history:
            context += f"\nLịch sử làm bài gần nhất: {', '.join(user_history[:5])}"

        return context

    def explain_single_recommendation(
        self, student_code: str, item_info: Dict, rank: int, score: float
    ) -> str:
        """
        Giải thích một bài tập cụ thể tại sao được gợi ý
        """
        prompt = f"""
        Giải thích tại sao bài tập "{item_info['title']}" (chủ đề: {item_info['topic']}, độ khó: {item_info['difficulty']}) 
        được gợi ý ở vị trí số {rank} cho sinh viên {student_code} với điểm số {score:.3f}.

        Viết 1-2 câu ngắn gọn bằng tiếng Việt, tập trung vào lợi ích học tập.
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
                max_tokens=150,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Lỗi giải thích: {str(e)}"


class MistralCloudExplainer:
    """
    Sử dụng Mistral AI từ cloud (mistral.ai)
    """

    def __init__(self, api_key: str, model_name: str = "mistral-small-latest"):
        """
        Initialize Mistral Cloud client
        
        Args:
            api_key: API key từ console.mistral.ai
            model_name: Tên model (mistral-small-latest, mistral-medium-latest, mistral-large-latest)
        """
        try:
            from mistralai import Mistral
            self.client = Mistral(api_key=api_key)
            self.model_name = model_name
        except ImportError:
            raise ImportError("Cần cài đặt mistralai: pip install mistralai")

    def explain_recommendations(
        self, student_code: str, recommendations: List[Dict]
    ) -> str:
        """Giải thích sử dụng Mistral AI từ cloud"""
        context = self._build_context(student_code, recommendations)

        prompt = f"""Bạn là giáo viên lập trình có kinh nghiệm. Hãy phân tích danh sách gợi ý bài tập sau và giải thích tại sao chúng phù hợp:

{context}

Hãy viết một phân tích chi tiết bao gồm:

**1. Phân tích tổng quan:**
- Chủ đề chính của các bài tập được gợi ý
- Mức độ khó và sự phân bố

**2. Lý do gợi ý:**
- Tại sao những bài tập này phù hợp với sinh viên
- Sự liên kết giữa các chủ đề

**3. Lộ trình học tập:**
- Thứ tự nên làm bài
- Kỹ năng sẽ phát triển

Viết bằng tiếng Việt, đầy đủ và dễ hiểu."""

        try:
            response = self.client.chat.complete(
                model=self.model_name,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=800,
            )
            
            return response.choices[0].message.content

        except Exception as e:
            return f"Không thể kết nối Mistral AI: {str(e)}"

    def _build_context(self, student_code: str, recommendations: List[Dict]) -> str:
        context = f"Sinh viên: {student_code}\nBài tập gợi ý:\n"
        for i, rec in enumerate(recommendations, 1):
            context += f"{i}. {rec['title']} ({rec['topic']}, {rec['difficulty']})\n"
        return context


class OllamaExplainer:
    """
    Phiên bản sử dụng Ollama (local LLM)
    """

    def __init__(
        self, model_name: str = "llama2", base_url: str = None
    ):
        import os
        
        self.model_name = model_name
        # Use provided URL, environment variable, or default to localhost
        self.base_url = base_url or os.getenv("OLLAMA_URL", "http://localhost:11434")

        try:
            import requests

            self.requests = requests
        except ImportError:
            raise ImportError("Cần cài đặt requests: pip install requests")

    def explain_recommendations(
        self, student_code: str, recommendations: List[Dict]
    ) -> str:
        """Giải thích sử dụng Ollama"""
        context = self._build_context(student_code, recommendations)

        prompt = f"""Bạn là giáo viên lập trình có kinh nghiệm. Hãy phân tích danh sách gợi ý bài tập sau và giải thích tại sao chúng phù hợp:

{context}

Hãy viết một phân tích chi tiết bao gồm:

**1. Phân tích tổng quan:**
- Chủ đề chính của các bài tập được gợi ý
- Mức độ khó và sự phân bố

**2. Lý do gợi ý:**
- Tại sao những bài tập này phù hợp với sinh viên
- Sự liên kết giữa các chủ đề

**3. Lộ trình học tập:**
- Thứ tự nên làm bài
- Kỹ năng sẽ phát triển

Viết bằng tiếng Việt, đầy đủ và dễ hiểu. Không cắt ngắn."""

        try:
            response = self.requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 800,  # Tăng lên để có đủ chỗ cho câu trả lời đầy đủ
                        "top_p": 0.9,
                        "repeat_penalty": 1.1,
                    },
                },
            )

            if response.status_code == 200:
                return response.json()["response"]
            else:
                return f"Lỗi kết nối Ollama: {response.status_code}"

        except Exception as e:
            return f"Không thể kết nối Ollama: {str(e)}"

    def _build_context(self, student_code: str, recommendations: List[Dict]) -> str:
        context = f"Sinh viên: {student_code}\nBài tập gợi ý:\n"
        for i, rec in enumerate(
            recommendations[:5], 1
        ):  # Giới hạn 5 bài để tiết kiệm token
            context += f"{i}. {rec['title']} ({rec['topic']}, {rec['difficulty']})\n"
        return context


class LocalLLMExplainer:
    """
    Phiên bản rule-based fallback khi không có LLM
    """

    def __init__(self):
        pass

    def explain_recommendations(
        self, student_code: str, recommendations: List[Dict]
    ) -> str:
        """
        Giải thích sử dụng rule-based approach khi không có LLM
        """
        # Phân tích patterns
        topics = [rec["topic"] for rec in recommendations]
        difficulties = [rec["difficulty"] for rec in recommendations]

        # Đếm chủ đề
        topic_counts = {}
        for topic in topics:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1

        main_topic = max(topic_counts, key=topic_counts.get)

        # Tạo giải thích rule-based
        explanation = (
            f"Dựa trên phân tích, hệ thống gợi ý tập trung vào chủ đề '{main_topic}' "
        )

        if len(set(difficulties)) > 1:
            explanation += "với độ khó tăng dần để phát triển kỹ năng từng bước. "
        else:
            explanation += f"ở mức độ {difficulties[0]} phù hợp với trình độ hiện tại. "

        explanation += f"Các bài tập được sắp xếp theo mức độ phù hợp giảm dần từ {recommendations[0]['score']:.3f} đến {recommendations[-1]['score']:.3f}."

        return explanation
