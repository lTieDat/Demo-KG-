# 1.6. Mô phỏng kết quả
Phần này trình bày chi tiết các kết quả thực nghiệm và quá trình vận hành của hệ thống Demo Web trong môi trường thực tế. Các thử nghiệm tập trung đánh giá hiệu năng của hai thành phần cốt lõi bao gồm hệ thống khuyến nghị dựa trên kiến trúc KGAT (Knowledge Graph Attention Network) và cơ chế giải thích thông minh kết hợp giữa trọng số Attention với khả năng tổng hợp ngôn ngữ của mô hình ngôn ngữ lớn (LLM).

## 1.6.1. Mô phỏng chức năng khuyến nghị Top-K
Trong kịch bản mô phỏng, chức năng khuyến nghị được kích hoạt thông qua giao diện người dùng dựa trên mã định danh sinh viên làm tham số đầu vào duy nhất. Khi mã sinh viên được ghi nhận, hệ thống backend thực hiện truy xuất toàn bộ lịch sử tương tác và các nút kiến thức liên quan trong đồ thị tri thức để làm cơ sở dữ liệu cho mô hình KGAT. Mô hình này thực hiện quá trình nhúng thực thể và quan hệ, đồng thời sử dụng cơ chế Attention để định lượng mức độ quan trọng của các nút lân cận đối với nhu cầu học tập hiện tại của sinh viên. Kết quả cuối cùng là một danh sách các bài tập được xếp hạng theo điểm số phù hợp, sau đó được trực quan hóa trên giao diện dưới dạng các thẻ thông tin đa phương tiện. Mỗi thẻ không chỉ hiển thị tên bài tập mà còn cung cấp các siêu dữ liệu quan trọng như chủ đề kiến thức và phân loại độ khó, giúp người học có cái nhìn tổng quan nhanh chóng về lộ trình được đề xuất.

## 1.6.2. Cơ chế giải thích kết quả dựa trên sự kết hợp giữa KGAT và LLM
Nhằm giải quyết triệt để vấn đề "hộp đen" của các mô hình học sâu và nâng cao niềm tin của người học, nghiên cứu đã xây dựng một cơ chế giải thích tinh vi dựa trên việc khai thác dữ liệu nội tại từ mô hình KGAT. Thay vì sử dụng các cấu trúc luật cứng nhắc hoặc các thông tin mô tả tĩnh, hệ thống trực tiếp can thiệp vào các tầng Aggregator của mô hình để trích xuất trọng số Attention trên từng cạnh cụ thể trong đồ thị tri thức. Quá trình này cho phép xác định chính xác những yếu tố tri thức nào đang đóng vai trò quyết định trong việc định hình kết quả gợi ý, từ đó biến các tham số số học phức tạp thành các tín hiệu có ý nghĩa về mặt học thuật.

Sau khi các trọng số Attention được trích xuất, hệ thống thực hiện thuật toán khai phá đường dẫn tri thức để tìm kiếm các kết nối logic xuyên suốt từ lịch sử hoàn thành bài tập của sinh viên đến bài tập mục tiêu. Mỗi đường dẫn không chỉ đơn thuần là một chuỗi các nút và cạnh mà còn mang theo giá trị định lượng về mức độ ảnh hưởng của chúng đối với dự đoán của mô hình. Chẳng hạn, một đường dẫn có thể chỉ ra rằng việc sinh viên hoàn thành tốt một bài tập về mảng đã tạo ra một lực đẩy Attention cực lớn hướng tới các bài tập về cấu trúc dữ liệu nâng cao hơn. Việc minh bạch hóa các đường dẫn này giúp hệ thống tạo ra một nền tảng biện luận vững chắc, cho thấy mọi gợi ý đều dựa trên một lộ trình phát triển năng lực có tính toán kỹ lưỡng.

Giai đoạn cuối cùng của cơ chế giải thích là quá trình tổng hợp ngôn ngữ tự nhiên thông qua việc tích hợp mô hình ngôn ngữ lớn (LLM). LLM đóng vai trò là một lớp giao tiếp thông minh, tiếp nhận các dữ liệu kỹ thuật bao gồm cấu trúc đồ thị, các đường dẫn tri thức và các trọng số Attention để chuyển hóa chúng thành các đoạn văn bản có tính sư phạm cao. Khác với các hệ thống giải thích tự động thông thường vốn thường khô khan, phương pháp tiếp cận này cho phép tạo ra các đoạn giải thích có văn phong khuyến khích, chuyên nghiệp và giàu ngữ cảnh. LLM biết cách nhấn mạnh vào những điểm mạnh trong lịch sử học tập của sinh viên thông qua các con số Attention ấn tượng, từ đó giúp người học hiểu rõ hơn về mối liên hệ giữa những gì họ đã biết và những gì họ cần đạt được tiếp theo, tạo nên một vòng lặp phản hồi tích cực trong quá trình tự học.

### Hình 1: Kiến trúc pipeline giải thích KGAT-LLM

Sơ đồ dưới đây minh họa luồng xử lý chính của hệ thống giải thích, từ đầu vào yêu cầu khuyến nghị cho đến kết quả đầu ra là văn bản giải thích tự nhiên được hiển thị trên giao diện người dùng.

```mermaid
flowchart TB
    subgraph Input["Đầu vào"]
        A["Mã sinh viên<br/>(Student ID)"]
        B["Lịch sử hoàn thành<br/>(User History)"]
    end
    
    subgraph KGAT["Mô hình KGAT"]
        C["Tầng Embedding<br/>Entity & Relation"]
        D["Aggregator Layers<br/>với cơ chế Attention"]
        E["Trích xuất<br/>Attention Weights"]
    end
    
    subgraph PathFinding["Khai phá đường dẫn"]
        F["Tìm đường nối<br/>History → Target"]
        G["Tính tổng Attention<br/>cho mỗi path"]
        H["Xếp hạng Top-K<br/>paths quan trọng"]
    end
    
    subgraph LLM["Tổng hợp ngôn ngữ"]
        I["Prompt Engineering<br/>với context KG"]
        J["LLM Processing<br/>(Mistral/GPT)"]
        K["Văn bản giải thích<br/>tự nhiên"]
    end
    
    A --> C
    B --> F
    C --> D
    D --> E
    E --> G
    F --> G
    G --> H
    H --> I
    I --> J
    J --> K
    
    style Input fill:#e1f5fe,stroke:#01579b
    style KGAT fill:#fff3e0,stroke:#e65100
    style PathFinding fill:#f3e5f5,stroke:#7b1fa2
    style LLM fill:#e8f5e9,stroke:#2e7d32
```

### Hình 2: Cấu trúc đường dẫn tri thức trong Knowledge Graph

Sơ đồ này mô tả cách hệ thống tìm kiếm các đường dẫn kết nối giữa những bài tập mà sinh viên đã hoàn thành (lịch sử học tập) và bài tập được đề xuất thông qua các nút trung gian như chủ đề (Topic) và độ khó (Level) trong đồ thị tri thức.

```mermaid
flowchart LR
    subgraph History["Lịch sử sinh viên"]
        H1["Bài tập đã làm 1<br/>(Entity E1)"]
        H2["Bài tập đã làm 2<br/>(Entity E2)"]
    end
    
    subgraph Topics["Chủ đề kiến thức"]
        T1["T_Mảng_một_chiều"]
        T2["T_Số_học"]
    end
    
    subgraph Levels["Độ khó"]
        L1["L_2<br/>(Trung bình)"]
    end
    
    subgraph Target["Bài tập gợi ý"]
        R["Bài tập mục tiêu<br/>(Entity E10)"]
    end
    
    H1 -->|"has_topic<br/>attention: 0.85"| T1
    H2 -->|"has_topic<br/>attention: 0.72"| T2
    H1 -->|"has_level<br/>attention: 0.65"| L1
    
    T1 -->|"topic_of<br/>attention: 0.88"| R
    T2 -->|"topic_of<br/>attention: 0.70"| R
    L1 -->|"level_of<br/>attention: 0.60"| R
    
    style History fill:#bbdefb,stroke:#1976d2
    style Topics fill:#ffe0b2,stroke:#f57c00
    style Levels fill:#c8e6c9,stroke:#388e3c
    style Target fill:#ffcdd2,stroke:#d32f2f
```

Trong cả hai sơ đồ trên, các giá trị attention được trích xuất trực tiếp từ các tầng Aggregator của mô hình KGAT thể hiện mức độ quan trọng của từng mối quan hệ. Đường dẫn có tổng attention cao nhất sẽ được ưu tiên sử dụng làm cơ sở lập luận cho việc giải thích, đảm bảo rằng mỗi khuyến nghị đều có thể được biện minh bằng các bằng chứng định lượng từ quá trình học của mô hình.
