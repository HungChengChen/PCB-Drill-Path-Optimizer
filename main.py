import json
import os

import pandas as pd
from icecream import ic

from solver.greedy_2opt import GreedySolver
from utils import calculate_distance_matrix, cost_distance, plot_route


def main(coords_df):
    # 計算距離矩陣
    dist_matrix = calculate_distance_matrix(coords_df)
    original_path = coords_df.index.tolist()  # 原始路徑（按照輸入順序）
    original_distance = cost_distance(dist_matrix, original_path)  # 計算原始路徑的總距離
    ic(original_distance)

    ic("Start greedy solving...")
    solver = GreedySolver(dist_matrix)
    greedy_path = solver.run()  # path 是index的順序
    greedy_distance = cost_distance(dist_matrix, greedy_path)  # 計算貪心算法的路徑總距離
    ic(greedy_distance)

    ic("Start 2-opt solving...")
    opt2_path = solver.opt2_optimize(optim_steps=7)  # path 是index的順序
    opt2_distance = cost_distance(dist_matrix, opt2_path)  # 計算2-opt優化後的路徑總距離
    ic(opt2_distance)

    # 提取出 Node ID 的順序
    opt2_permutation = coords_df.reindex(opt2_path)["Node_ID"].tolist()
    plot_route(coords_df, opt2_permutation)  # 繪製優化後的路徑

    # 保存路徑和距離到JSON文件中
    log_json = {"distance": opt2_distance, "route": opt2_permutation}
    json.dump(log_json, open(os.path.join("result", "opt2_permutation.json"), "w"))


if __name__ == "__main__":
    file_path = r"coords_df.csv"
    coords_df = pd.read_csv(file_path)
    main(coords_df)
