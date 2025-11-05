"""
Student Selection Component - Giao diện chọn sinh viên
"""

import streamlit as st


class StudentSelectionComponent:
    """Component quản lý việc chọn sinh viên"""

    def __init__(self):
        pass

    def get_student_options(self, dataset):
        """Lấy danh sách mã sinh viên hợp lệ"""
        uid_field = dataset.uid_field
        user_id2token = dataset.field2id_token[uid_field]

        student_options = {}
        for user_id in range(1, len(user_id2token)):
            student_code = user_id2token[user_id]
            if (
                isinstance(student_code, str)
                and student_code.startswith("B")
                and len(student_code) >= 8
            ):
                student_options[student_code] = user_id

        return student_options

    def render(self, dataset):
        """Render giao diện chọn sinh viên với search suggestion"""
        st.markdown(
            '<div class="section-header">Chọn sinh viên</div>',
            unsafe_allow_html=True,
        )

        student_options = self.get_student_options(dataset)
        sorted_student_codes = sorted(student_options.keys())

        # Bảo đảm session state mặc định
        st.session_state.setdefault("student_selected_code", None)
        st.session_state.setdefault("student_search_query", "")

        user_id, selected_student = self._render_search_selection(
            student_options, sorted_student_codes
        )

        # Chọn số lượng recommendation
        topk = st.selectbox(
            "Số lượng gợi ý bài tập:",
            options=[1, 2, 5, 10, 20],
            index=3,
            help="Chọn số lượng bài tập bạn muốn nhận gợi ý",
        )

        return user_id, selected_student, topk, "search"

    def _render_search_selection(self, student_options, sorted_student_codes):
        """Render search suggestion - live search giống Google Chrome"""
        search_query_key = "student_search_query"
        selection_key = "student_selected_code"
        show_all_key = "student_show_all_results"

        # Live search - gõ 1 ký tự là hiển thị
        search_term = st.text_input(
            "Tìm kiếm mã sinh viên:",
            placeholder="Nhập mã sinh viên (ví dụ: B21DCVT013)...",
            help="Gõ để tìm kiếm ngay",
            key=search_query_key,
        )

        search_term = search_term.strip()
        user_id = None
        selected_student = None

        if not search_term:
            st.session_state[selection_key] = None
            st.session_state.setdefault(show_all_key, False)
            st.info(
                f"Nhập ít nhất 1 ký tự để hiển thị danh sách sinh viên (tổng cộng {len(sorted_student_codes)} sinh viên)."
            )
            return None, None

        # Filter kết quả theo keyword
        filtered_codes = [
            code for code in sorted_student_codes if search_term.upper() in code.upper()
        ]

        if not filtered_codes:
            st.session_state[selection_key] = None
            st.warning(
                f"Không tìm thấy sinh viên nào với từ khóa '{search_term}'. Vui lòng thử lại."
            )
            return None, None

        # Xác định số lượng kết quả hiển thị
        show_all = st.session_state.get(show_all_key, False)
        max_display = len(filtered_codes) if show_all else min(5, len(filtered_codes))
        display_codes = filtered_codes[:max_display]

        # Khởi tạo selection
        if (
            selection_key not in st.session_state
            or st.session_state[selection_key] not in filtered_codes
        ):
            st.session_state[selection_key] = filtered_codes[0]

        # Hiển thị suggestion container
        st.markdown(
            f'<div class="search-info-bar">Tìm thấy {len(filtered_codes)} kết quả</div>',
            unsafe_allow_html=True,
        )

        suggestion_container = st.container()
        with suggestion_container:
            st.markdown(
                '<div class="search-suggestion-container">',
                unsafe_allow_html=True,
            )
            selected_student = st.radio(
                label="",
                options=display_codes,
                key=selection_key,
                label_visibility="collapsed",
            )
            st.markdown("</div>", unsafe_allow_html=True)

        # Hiển thị button "Show more" nếu có kết quả nhiều hơn 5
        if len(filtered_codes) > 5:
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if show_all:
                    if st.button("Ẩn bớt", key="hide_results"):
                        st.session_state[show_all_key] = False
                        st.rerun()
                else:
                    if st.button("Xem thêm", key="show_more"):
                        st.session_state[show_all_key] = True
                        st.rerun()

        # Hiển thị thông tin sinh viên được chọn
        user_id = student_options.get(selected_student)
        if user_id:
            st.markdown(
                f'<div class="selected-student-info"><strong>{selected_student}</strong> · User ID: {user_id}</div>',
                unsafe_allow_html=True,
            )

        return user_id, selected_student
