# 🏁 F1 Lap Time Visualization Guide

全ドライバーのラップタイムをグラフ化して分析するための包括的な視覚化ツールです。

## 🧹 NEW: 外れ値フィルタリング機能

### 主要な改善点:
- **統計的外れ値検出**: IQR、Z-Score、Modified Z-Score手法による外れ値の自動検出
- **ピット後異常値除去**: ピットアウト直後の異常なラップタイムを自動除外
- **クリーンデータ分析**: より正確な平均タイム、パフォーマンス比較、統計分析
- **外れ値可視化**: 除外されたデータポイントを赤いXマークで表示

### 外れ値除去の効果:
- より正確な平均ラップタイム計算
- パフォーマンス比較の精度向上
- タイヤ劣化分析の信頼性向上
- レース戦略評価の改善

## 📊 利用可能な可視化

### 1. 全ドライバー概要 (All Drivers Overview)
- 全ドライバーのラップタイム推移
- 平均ラップタイム比較（ピットラップ除く）
- チーム色による識別

### 2. レース進行ヒートマップ (Race Evolution Heatmap)
- 全ドライバーの全ラップのヒートマップ表示
- ピットストップのマーカー付き
- レース全体の流れを一目で把握

### 3. 詳細ドライバー分析 (Detailed Driver Analysis)
- 個別ドライバーの詳細分析（4パネル表示）:
  - ラップタイム推移（ピットストップ標記付き）
  - タイヤコンパウンド別パフォーマンス
  - ラップタイム分布
  - タイヤ劣化分析

### 4. 比較分析 (Comparative Analysis)
- 複数ドライバーの直接比較（4パネル表示）:
  - ラップタイム直接比較
  - パフォーマンス統計
  - タイヤコンパウンド別分析
  - 最速タイムとのギャップ分析

## 🚀 使用方法

### インタラクティブメニュー
```bash
python3 lap_time_visualizer.py
```

メニューからオプションを選択:
1. 全ドライバー概要
2. レース進行ヒートマップ
3. 詳細ドライバー分析
4. 比較分析
5. 全視覚化生成
6. 利用可能ドライバー一覧

### 全視覚化の一括生成
```bash
python3 lap_time_visualizer.py --generate-all
```

`visualizations/` フォルダに以下が生成されます:
- `01_all_drivers_overview.png` - 全ドライバー概要
- `02_race_evolution_heatmap.png` - レース進行ヒートマップ
- `03_detailed_[DRIVER].png` - 主要ドライバーの詳細分析
- `04_comparative_top3.png` - トップ3ドライバー比較

### クイック視覚化コマンド
```bash
# 全ドライバー概要
python3 quick_viz.py overview

# レース進行ヒートマップ
python3 quick_viz.py heatmap

# 特定ドライバーの詳細分析（例：フェルスタッペン）
python3 quick_viz.py driver 1

# トップ3ドライバー比較
python3 quick_viz.py top3

# カスタムドライバー比較（例：VER, HAM, LEC）
python3 quick_viz.py compare 1,44,16
```

## 📋 利用可能ドライバー

| 番号 | ドライバー | チーム | 略称 |
|------|------------|---------|------|
| 1 | Max VERSTAPPEN | Red Bull Racing | VER |
| 2 | Logan SARGEANT | Williams | SAR |
| 4 | Lando NORRIS | McLaren | NOR |
| 10 | Pierre GASLY | Alpine | GAS |
| 11 | Sergio PEREZ | Red Bull Racing | PER |
| 14 | Fernando ALONSO | Aston Martin | ALO |
| 16 | Charles LECLERC | Ferrari | LEC |
| 18 | Lance STROLL | Aston Martin | STR |
| 20 | Kevin MAGNUSSEN | Haas F1 Team | MAG |
| 22 | Yuki TSUNODA | RB | TSU |
| 24 | ZHOU Guanyu | Kick Sauber | ZHO |
| 27 | Nico HULKENBERG | Haas F1 Team | HUL |
| 31 | Esteban OCON | Alpine | OCO |
| 44 | Lewis HAMILTON | Mercedes | HAM |
| 55 | Carlos SAINZ | Ferrari | SAI |
| 63 | George RUSSELL | Mercedes | RUS |
| 77 | Valtteri BOTTAS | Kick Sauber | BOT |
| 81 | Oscar PIASTRI | McLaren | PIA |

## 🎨 視覚化の特徴

### チーム色
各ドライバーは2024年F1シーズンの公式チーム色で表示されます:
- 🔵 Red Bull Racing: #3671C6
- 🔴 Ferrari: #E80020
- 🟠 McLaren: #FF8000
- 🟢 Mercedes: #27F4D2
- 🟢 Aston Martin: #229971
- 🔵 Alpine: #0093CC
- 🔵 Williams: #64C4FF
- 🔵 RB: #6692FF
- 🟢 Kick Sauber: #52E252
- ⚪ Haas F1 Team: #B6BABD

### タイヤコンパウンド色
- 🔴 SOFT (ソフト): 赤
- 🟡 MEDIUM (ミディアム): 黄
- ⚪ HARD (ハード): 白
- 🟢 INTERMEDIATE (インターミディエイト): 緑
- 🔵 WET (ウェット): 青

## 📈 分析機能

### 1. パフォーマンス分析
- 平均ラップタイム
- 最速ラップタイム
- ラップタイムの一貫性（標準偏差）
- タイヤコンパウンド別パフォーマンス

### 2. 戦略分析
- ピットストップタイミング
- スティント長分析
- タイヤ劣化パターン
- 戦略の効果

### 3. 比較分析
- ドライバー間の直接比較
- 最速タイムとのギャップ
- チーム内比較
- レース進行での順位変動

## 🔧 技術仕様

### 必要なライブラリ
```bash
pip install pandas numpy matplotlib seaborn
```

### データソース
- `data/drivers.csv` - ドライバー情報
- `data/lap_times.csv` - ラップタイム記録
- `data/pit_stops.csv` - ピットストップ記録
- `data/stints.csv` - スティント情報

### 出力形式
- PNG形式（300 DPI、高解像度）
- インタラクティブ表示（matplotlib）

## 💡 使用例

### レース戦略分析
```bash
# トップ3チームの比較
python3 quick_viz.py compare 1,11,16,55,44,63

# 特定ドライバーの詳細分析
python3 quick_viz.py driver 1  # フェルスタッペン
python3 quick_viz.py driver 44 # ハミルトン
```

### チーム分析
```bash
# Red Bull Racing
python3 quick_viz.py compare 1,11

# Ferrari
python3 quick_viz.py compare 16,55

# Mercedes
python3 quick_viz.py compare 44,63
```

## 📊 データ分析のヒント

1. **ピットストップ戦略**: 詳細ドライバー分析でピットタイミングを確認
2. **タイヤ劣化**: スティント分析でタイヤパフォーマンスの変化を観察
3. **一貫性**: ラップタイム分布で各ドライバーの安定性を評価
4. **相対パフォーマンス**: 比較分析で競争力を客観的に評価

この視覚化ツールを使用して、2024年日本GPの詳細な分析を行い、F1戦略の理解を深めてください！