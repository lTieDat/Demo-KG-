"""
Recommendation generation utilities
"""
import torch
from recbole.data.interaction import Interaction


def get_top_k_recommendations(model, dataset, user_id, topk=10):
    """
    Lấy top-k recommendation cho user
    """
    try:
        model.eval()
        uid_field = dataset.uid_field
        iid_field = dataset.iid_field

        # Kiểm tra user_id hợp lệ
        if user_id >= dataset.user_num or user_id < 0:
            raise ValueError(
                f"User ID {user_id} không hợp lệ. Phải trong khoảng 0-{dataset.user_num-1}"
            )

        # Tạo input cho user
        user_inter = Interaction({uid_field: torch.tensor([user_id])})

        with torch.no_grad():
            scores = model.full_sort_predict(
                user_inter.to(model.device)
            )  # [1, num_items]
            scores = scores.view(-1)

            # Lấy top-k items
            topk_scores, topk_iids = torch.topk(scores, min(topk, len(scores)))

            # Convert về tên item nếu có mapping
            item_id2token = dataset.field2id_token[iid_field]

            results = []
            for i, iid in enumerate(topk_iids):
                item_internal_id = int(iid.item())

                # Xử lý item_id2token có thể là dict hoặc array
                if hasattr(item_id2token, "get"):
                    # Nếu là dictionary
                    item_external_id = item_id2token.get(
                        item_internal_id, f"Item_{item_internal_id}"
                    )
                elif hasattr(item_id2token, "__getitem__"):
                    # Nếu là array/list
                    try:
                        item_external_id = item_id2token[item_internal_id]
                    except (IndexError, KeyError):
                        item_external_id = f"Item_{item_internal_id}"
                else:
                    # Fallback
                    item_external_id = f"Item_{item_internal_id}"

                score = float(topk_scores[i].item())
                results.append((item_internal_id, item_external_id, score))

            return results

    except Exception as e:
        raise Exception(f"Lỗi trong get_top_k_recommendations: {str(e)}")
