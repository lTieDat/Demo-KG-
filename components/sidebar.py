"""
Sidebar Component - Giao diện sidebar cấu hình model
"""

import streamlit as st
import os


class SidebarComponent:
    """Component quản lý sidebar"""

    def __init__(self, model_service):
        self.model_service = model_service

    def render_model_selection(self):
        """Render phần chọn model trong sidebar"""
        st.sidebar.header("Cấu hình Model")
        load_method = st.sidebar.radio(
            "Chọn phương thức load model:",
            ["Từ checkpoint (mới)", "Từ RecBole (cũ)"],
        )

        model_path = None
        config = None
        model = None
        dataset = None

        if load_method == "Từ checkpoint (mới)":
            model_path, config, model, dataset = self._render_checkpoint_selection()
        else:
            model_path, config, model, dataset = self._render_old_model_selection()

        return load_method, model_path, config, model, dataset

    def _render_checkpoint_selection(self):
        """Render phần chọn checkpoint"""
        compatible_models, incompatible_models = (
            self.model_service.get_compatible_checkpoints()
        )

        if compatible_models:
            st.sidebar.success(f"{len(compatible_models)} model tương thích")

            model_options = []
            model_info_dict = {}

            for model_file, info in compatible_models:
                display_name = f"{model_file}"
                model_options.append(display_name)
                model_info_dict[display_name] = (model_file, info)

            selected_model = st.sidebar.selectbox(
                "Chọn model tương thích:", model_options
            )

            if selected_model:
                model_file, info = model_info_dict[selected_model]
                model_path = os.path.join(self.model_service.recbole_dir, model_file)

                # Hiển thị thông tin checkpoint
                with st.sidebar.expander("Thông tin Checkpoint"):
                    st.write(f"**Dataset:** {info['dataset']}")
                    st.write(f"**Epoch:** {info['epoch']}")
                    st.write(f"**Score:** {info['score']}")
                    st.write(f"**Embedding size:** {info['embedding_size']}")
                    st.write(
                        f"**Users:** {info['user_count']:,}"
                        if info["user_count"] != "Unknown"
                        else "**Users:** Unknown"
                    )
                    st.write(
                        f"**Entities:** {info['entity_count']:,}"
                        if info["entity_count"] != "Unknown"
                        else "**Entities:** Unknown"
                    )
                    st.write(
                        f"**Relations:** {info['relation_count']:,}"
                        if info["relation_count"] != "Unknown"
                        else "**Relations:** Unknown"
                    )

            # Hiển thị model không tương thích
            if incompatible_models:
                with st.sidebar.expander(
                    f"{len(incompatible_models)} model không tương thích"
                ):
                    for model_file, info in incompatible_models:
                        st.write(f"**{model_file}**")
                        if "compatibility_issues" in info:
                            for issue in info["compatibility_issues"]:
                                st.write(f"  - {issue}")
                        st.write("---")

            # Load model
            config, model, dataset = self.model_service.load_trained_model(model_path)
            return model_path, config, model, dataset

        else:
            st.sidebar.error("Không có model nào tương thích với dataset hiện tại!")
            st.sidebar.write("Dataset yêu cầu: code-ptit-100k, embedding_size=64")

            all_models = [
                f
                for f in os.listdir(self.model_service.recbole_dir)
                if f.endswith(".pth")
            ]
            if all_models:
                with st.sidebar.expander("Tất cả model có sẵn"):
                    for model_file in all_models:
                        model_path = os.path.join(
                            self.model_service.recbole_dir, model_file
                        )
                        info = self.model_service.check_checkpoint_compatibility(
                            model_path, "code-ptit-100k"
                        )
                        st.write(f"**{model_file}**")
                        if "compatibility_issues" in info:
                            for issue in info["compatibility_issues"]:
                                st.write(f"  - {issue}")
                        st.write("---")

            st.stop()

    def _render_old_model_selection(self):
        """Render phần chọn model cũ"""
        from recbole.quick_start import load_data_and_model

        models = [
            f for f in os.listdir(self.model_service.model_dir) if f.endswith(".pth")
        ]
        if not models:
            st.sidebar.warning("Không tìm thấy model nào trong thư mục saved/")
            st.stop()

        selected_model = st.sidebar.selectbox("Chọn model:", models)
        model_path = os.path.join(self.model_service.model_dir, selected_model)

        if selected_model:
            config, model, dataset, train_data, valid_data, test_data = (
                load_data_and_model(model_path)
            )
            return model_path, config, model, dataset

        return None, None, None, None

    def render_dataset_info(self, dataset, student_options):
        """Render thông tin dataset"""
        st.sidebar.header("Thông tin Dataset")
        st.sidebar.metric("Tổng số user", f"{dataset.user_num:,}")
        st.sidebar.metric("Số sinh viên hợp lệ", f"{len(student_options):,}")
        st.sidebar.metric("Số bài tập", f"{dataset.item_num:,}")

    def render_statistics(self, student_codes):
        """Render thống kê chi tiết"""
        year_stats = {}
        major_stats = {}

        for code in student_codes:
            if len(code) >= 3:
                year = code[:3]
                year_stats[year] = year_stats.get(year, 0) + 1

            if len(code) >= 7:
                major = code[3:7]
                major_stats[major] = major_stats.get(major, 0) + 1

        with st.sidebar.expander("Thống kê chi tiết"):
            st.write("**Theo năm:**")
            for year, count in sorted(year_stats.items()):
                st.write(f"- {year}: {count} sinh viên")

            st.write("**Theo ngành (top 5):**")
            top_majors = sorted(major_stats.items(), key=lambda x: x[1], reverse=True)[
                :5
            ]
            for major, count in top_majors:
                st.write(f"- {major}: {count} sinh viên")
