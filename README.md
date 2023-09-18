# PCB-Drill-Path-Optimizer 

本專案針對大型的 PCB 版面設計，使用 `greedy + 2-opt` 策略，優化上萬座標點的鐳射鑽孔路徑。

## 1. 項目背景

對於大型的 PCB 版面，座標點數量龐大，達到上萬點或更多。傳統的啟發式演算法難以在短時間內給出合理的解。本專案所開發的 `greedy + 2-opt` 算法，不僅能在更短的時間內給出解，而且提供了更加合理的鑽孔路徑。

## 2. 技術亮點

- **高效的算法**：結合 `greedy` 和 `2-opt` 策略，有效地找到近似最佳解。
- **numpy 優化**：大量使用 numpy 進行資料結構的改寫，實現高速的數學運算。
- **智能2-opt選擇**：優先選擇能大幅改善路徑長度的線段進行 2-opt 操作，加速算法的收斂

## 3. 使用方法

1. 安裝依賴：`pip install numpy [其他必要的依賴]`
2. 運行主程式：`python main.py [參數]`

## 4. 使用範例

```bash
python main.py example_file.txt

## 5. 作者與聯絡方式

- 作者：[陳宏誠]
- 電子郵件：[hungcheng.chen@outlook.com]
