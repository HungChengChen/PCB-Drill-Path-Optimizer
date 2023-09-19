"""
使用numpy重寫資料結構以加速運算。
還加入了首先選擇能夠"大幅改善路徑長度的線段"的策略來執行2opt，從而加速收斂。
"""

import numpy as np
from tqdm import tqdm


class GreedySolver:
    def __init__(self, dist_matrix, end_point=None):
        self.dist_matrix = dist_matrix
        self.N = len(dist_matrix)
        self.end_point = end_point
        self.start, self.end = end_point or (None, None)
        # 判斷是否為環路
        self.is_loop = (self.start is not None) and (self.start == self.end)
        self.check_validity()

    def check_validity(self):
        # 檢查起點是否在範圍內
        if self.start is not None and not (0 <= self.start < self.N):
            raise ValueError("起點不在正確的範圍內")
        # 檢查終點是否在範圍內
        if self.end is not None and not (0 <= self.end < self.N):
            raise ValueError("終點不在正確的範圍內")

        if self.N == 0:  # 若距離矩陣為空
            return []
        if self.N == 1:  # 若距離矩陣只有一個元素
            return [0, 0] if self.is_loop else [0]
        if self.N == 2 and self.is_loop:  # 若距離矩陣有兩個元素且為環路
            return [self.start, 1 - self.start, self.start]

        self._assert_triangular()

    def _assert_triangular(self):
        """確保矩陣至少是左下三角形的"""
        for i, row in enumerate(self.dist_matrix):
            if len(row) < i:
                raise ValueError(f"距離矩陣必須至少是左三角形的。第{i}行必須至少有{i}個項目")

    def pairs_by_dist(self):
        """生成節點對，並按距離排序"""
        pairs = np.triu_indices(self.N, k=1)  # 取得上三角矩陣的索引
        pairs = np.transpose(pairs)  # 轉置以獲得所需的格式
        pairs = np.sort(pairs, axis=1)[:, ::-1]  # 對每對進行排序
        # 按照距離對節點對進行排序
        pairs = pairs[
            np.argsort(self.dist_matrix[pairs[:, 0], pairs[:, 1]], kind="mergesort")
        ]
        return pairs

    def edge_connects_endpoint_segments(self, i, j, segments):
        """檢查邊是否連接到端點段"""
        si, sj = segments[i], segments[j]
        ss, se = segments[self.start], segments[self.end]
        # 判斷邊是否連接到起點和終點
        return (si is ss) and (sj is se) or (sj is ss) and (si is se)

    def restore_path(self):
        """從連接中恢復路徑"""
        need_revert = False
        if self.start is None:
            if self.end is None:
                # 找到只有一個連接的第一個節點
                self.start = next(
                    idx for idx, conn in enumerate(self.connections) if len(conn) == 1
                )
            else:
                # 在這種情況下 - 從終點開始搜索，然後反轉順序
                self.start = self.end
                need_revert = True

        # 現在可以生成路徑了
        path = [self.start]
        prev_point = None
        cur_point = self.start
        # 迭代所有連接，生成完整路徑
        for _ in range(len(self.connections) - (0 if self.is_loop else 1)):
            next_point = next(
                pnt for pnt in self.connections[cur_point] if pnt != prev_point
            )
            path.append(next_point)
            prev_point, cur_point = cur_point, next_point
        if need_revert:
            return path[::-1]  # 如果需要，反轉路徑
        else:
            return path

    def run(self):
        """執行解算器"""
        # 初始情況下，每個節點都有2個"黏性端"（可以連接的端點）
        node_valency = np.array([2] * self.N)
        has_both_endpoints = (self.start is not None) and (self.end is not None)

        if not self.is_loop:
            # 若不是環路，起點和終點只有1個黏性端
            if self.start is not None:
                node_valency[self.start] = 1
            if self.end is not None:
                node_valency[self.end] = 1

        # 對於每個節點，儲存1或2個連接的節點
        connections = [set() for _ in range(self.N)]
        segments = [[i] for i in range(self.N)]

        sorted_pairs = self.pairs_by_dist()

        edges_left = self.N - 1
        # 遍歷按距離排序的節點對
        for i, j in tqdm(sorted_pairs, desc="Greedy ", total=len(sorted_pairs)):
            i, j = int(i), int(j)
            if node_valency[i] and node_valency[j] and (segments[i] is not segments[j]):
                # 若此邊連接了起點和終點但不是最後一條邊，則跳過
                if (
                    has_both_endpoints
                    and edges_left != 1
                    and self.edge_connects_endpoint_segments(i, j, segments)
                ):
                    continue

                node_valency[i] -= 1
                node_valency[j] -= 1
                connections[i].add(j)
                connections[j].add(i)

                # 合併兩個段落
                new_segment = segments[i] + segments[j]
                for node_idx in new_segment:
                    segments[node_idx] = new_segment

                edges_left -= 1
                if edges_left == 0:
                    break
        # 如果是尋找一個環路，則關閉它
        if self.is_loop:
            """修改連接以關閉環路"""
            # _close_loop(connections)
            i, j = (i for i, conn in enumerate(connections) if len(conn) == 1)
            connections[i].add(j)
            connections[j].add(i)

        self.connections = connections
        self.path = self.restore_path()

        return self.path

    def opt2_optimize(self, optim_steps):
        """
        進行2-opt優化，並優先選擇能夠"大幅改善路徑長度的線段"以加速收斂。

        Args:
            optim_steps (int): 優化步數

        Returns:
            list: 優化後的路徑
        """
        for passn in range(optim_steps):
            progress_bar = tqdm(
                range(self.N - 4), desc="2-opt steps = {}".format(passn)
            )
            d_total = 0.0
            optimizations = 0
            for a in progress_bar:
                b, c, d = a + 1, a + 3, a + 4

                path_a = self.path[a]
                path_b = self.path[b]
                path_c = self.path[c : self.N - 1]
                path_d = self.path[d : self.N]

                ds_ab = self.dist_matrix[path_a][path_b]
                ds_cd = self.dist_matrix[path_c, path_d]
                ds_ac = self.dist_matrix[path_a][path_c]
                ds_bd = self.dist_matrix[path_b][path_d]

                # 計算路徑交換的距離差
                delta_d = ds_ab + ds_cd - (ds_ac + ds_bd)

                if np.any(delta_d > 0):
                    index = np.argmax(delta_d)  # 找到能大幅改善路徑長的線段
                    d_total += delta_d[index]
                    optimizations += 1
                    progress_bar.set_postfix(
                        {"Opt Dist": d_total, "Opt Count": optimizations},
                        refresh=True,
                    )
                    c_opt = path_c[index]
                    d_opt = path_d[index]

                    # 更新連接關係，實現2-opt交換
                    self.connections[path_a].remove(path_b)
                    self.connections[path_a].add(c_opt)
                    self.connections[path_b].remove(path_a)
                    self.connections[path_b].add(d_opt)

                    self.connections[c_opt].remove(d_opt)
                    self.connections[c_opt].add(path_a)
                    self.connections[d_opt].remove(c_opt)
                    self.connections[d_opt].add(path_b)

                    self.path[:] = self.restore_path()  # 恢復路徑

        progress_bar.close()
        return self.path
