"""
Demo script để test Ollama trước khi tích hợp vào hệ thống chính
"""

import requests
import json
import time


class OllamaDemo:
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url

    def check_connection(self):
        """Kiểm tra kết nối Ollama server"""
        print("🔍 Kiểm tra kết nối Ollama...")
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                print(f"✅ Kết nối thành công!")
                print(f"📦 Models available: {len(models)}")
                for model in models:
                    print(f"   • {model['name']} ({model.get('size', 'Unknown size')})")
                return True, models
            else:
                print(f"❌ Server error: {response.status_code}")
                return False, []
        except requests.exceptions.ConnectionError:
            print("❌ Không thể kết nối. Hãy đảm bảo Ollama server đang chạy:")
            print("   ollama serve")
            return False, []
        except Exception as e:
            print(f"❌ Lỗi: {str(e)}")
            return False, []

    def test_generation(self, model_name="llama2", prompt=None):
        """Test tạo text với model"""
        if not prompt:
            prompt = """
            Giải thích ngắn gọn tại sao bài tập "Stack và Queue" quan trọng cho sinh viên lập trình.
            Trả lời bằng tiếng Việt trong 2-3 câu.
            """

        print(f"\n🤖 Test generation với model: {model_name}")
        print(f"📝 Prompt: {prompt.strip()}")
        print("⏳ Đang xử lý...")

        start_time = time.time()

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.7, "num_predict": 200},
                },
                timeout=60,
            )

            end_time = time.time()

            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "")

                print(f"✅ Thành công!")
                print(f"⏱️  Thời gian: {end_time - start_time:.2f}s")
                print(f"📊 Tokens: ~{len(response_text.split())} từ")
                print(f"💬 Kết quả:\n{response_text}")
                return True, response_text
            else:
                print(f"❌ Lỗi API: {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Chi tiết: {error_detail}")
                except:
                    print(f"   Response: {response.text}")
                return False, ""

        except requests.exceptions.Timeout:
            print("❌ Timeout! Model có thể quá chậm hoặc prompt quá phức tạp")
            return False, ""
        except Exception as e:
            print(f"❌ Lỗi: {str(e)}")
            return False, ""

    def interactive_demo(self):
        """Demo tương tác"""
        print("🎯 Demo Ollama cho Giải Thích Bài Tập")
        print("=" * 50)

        # Kiểm tra kết nối
        connected, models = self.check_connection()
        if not connected:
            return

        if not models:
            print("⚠️  Không có model nào. Hãy tải model:")
            print("   ollama pull llama2")
            return

        # Chọn model
        print(f"\n📦 Chọn model để test:")
        for i, model in enumerate(models):
            print(f"   {i+1}. {model['name']}")

        try:
            choice = int(input("Nhập số: ")) - 1
            selected_model = models[choice]["name"]
        except (ValueError, IndexError):
            selected_model = models[0]["name"]
            print(f"Sử dụng model mặc định: {selected_model}")

        # Test với prompts mẫu
        sample_prompts = [
            "Giải thích tại sao bài tập 'Stack và Queue' phù hợp cho sinh viên B21DCCN001",
            "Tại sao hệ thống gợi ý bài 'Binary Search Tree' cho sinh viên này?",
            "Giải thích lợi ích của việc học Linked List trước Tree",
        ]

        print(f"\n🧪 Test với các prompt mẫu:")
        for i, prompt in enumerate(sample_prompts, 1):
            print(f"\n--- Test {i}/{len(sample_prompts)} ---")
            success, response = self.test_generation(selected_model, prompt)
            if not success:
                break

            input("\nNhấn Enter để tiếp tục...")

        # Custom prompt
        print(f"\n✏️  Muốn test prompt tùy chỉnh? (y/n): ", end="")
        if input().lower() == "y":
            custom_prompt = input("Nhập prompt: ")
            self.test_generation(selected_model, custom_prompt)

        print("\n🎉 Demo hoàn tất!")


def main():
    print("🚀 Ollama Demo cho Hệ Thống Giải Thích Bài Tập")
    print("=" * 60)

    demo = OllamaDemo()

    # Menu
    while True:
        print("\n📋 Menu:")
        print("1. Kiểm tra kết nối")
        print("2. Test generation nhanh")
        print("3. Demo tương tác đầy đủ")
        print("4. Thoát")

        choice = input("\nChọn (1-4): ").strip()

        if choice == "1":
            demo.check_connection()
        elif choice == "2":
            demo.test_generation()
        elif choice == "3":
            demo.interactive_demo()
        elif choice == "4":
            print("👋 Tạm biệt!")
            break
        else:
            print("❌ Lựa chọn không hợp lệ")


if __name__ == "__main__":
    main()
