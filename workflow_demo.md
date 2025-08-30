# Workflow: Recommendation Demo with Streamlit + RecBole

## Steps

1.  **User Input**
    -   Người dùng nhập `user_id` vào giao diện Streamlit.\
    -   Người dùng chọn model muốn chạy từ danh sách model đã train (ví
        dụ: BPR, NeuMF, NCF...).
2.  **Model Loading**
    -   Ứng dụng đọc `user_id` và tên model mà user chọn.\
    -   Từ tên model, ứng dụng tìm tới checkpoint `.pth` trong thư mục
        `saved/`.\
    -   RecBole API được sử dụng để load lại model và dataset đã train
        trước đó.
3.  **Generate Recommendation**
    -   Sau khi model được load, hệ thống chạy hàm dự đoán cho
        `user_id`.\
    -   Model trả về danh sách các item với score (mức độ phù hợp).
4.  **Post-processing**
    -   Các item được sắp xếp theo score giảm dần.\
    -   Lấy ra Top-10 item gợi ý cho người dùng.
5.  **Display Result**
    -   Streamlit hiển thị bảng kết quả gồm **item_id** và **tên bài**
        (hoặc metadata khác nếu có).\
    -   UI chỉ đóng vai trò trình bày, còn việc suy luận được thực hiện
        bởi RecBole + model đã train.

------------------------------------------------------------------------

## Notes

-   `saved/` chứa checkpoint các model đã train (`.pth`).\
-   Code demo chỉ cần load lại model và dataset từ RecBole.\
-   Người dùng không cần train lại model khi chạy demo.
