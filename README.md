# 🏁 F1 Strategy Simulator

F1レースのピット戦略をシミュレーションし、代替戦略の効果を分析するWebアプリケーションです。

## 🎯 概要

実際の2024年日本GPデータを使用して、異なるピット戦略がレース結果に与える影響をシミュレーションできます。

### 主要機能
- **ドライバー選択**: 20名のF1ドライバーから選択
- **戦略設定**: ピットタイミングとタイヤコンパウンドを自由に設定
- **リアルタイムシミュレーション**: 代替戦略と実際の戦略を比較
- **視覚的な結果表示**: 時間差、戦略比較、改善効果を表示

## 🏗 技術構成

### フロントエンド (`packages/front`)
- **Framework**: Remix
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **Language**: TypeScript

### バックエンド (`packages/simulator`)
- **Framework**: FastAPI
- **Data Processing**: pandas, numpy
- **Language**: Python
- **API Documentation**: 自動生成 (Swagger UI)

## 🚀 セットアップ

### 1. プロジェクトクローン
```bash
git clone <repository-url>
cd f1_strategy_simulator
```

### 2. バックエンドセットアップ
```bash
cd packages/simulator

# 仮想環境作成（推奨）
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\\Scripts\\activate  # Windows

# 依存関係インストール
pip install -r requirements.txt

# データ取得（初回のみ）
python3 fetch_race_data.py

# APIサーバー起動
python3 api.py
```

### 3. フロントエンドセットアップ
```bash
cd packages/front

# 依存関係インストール
npm install

# 開発サーバー起動
npm run dev
```

## 📱 使用方法

1. **バックエンド起動**: `http://localhost:8000` でAPIサーバーが起動
2. **フロントエンド起動**: `http://localhost:5173` でWebアプリが起動
3. **ドライバー選択**: 左側のリストからドライバーを選択
4. **戦略設定**: 中央でピットストップのタイミングとタイヤを設定
5. **シミュレーション**: "Simulate Strategy"ボタンでシミュレーション実行
6. **結果確認**: 右側で結果と比較を確認

## 🔧 API仕様

詳細なAPI仕様は `packages/simulator/API_SPECIFICATION.md` を参照してください。

### 主要エンドポイント
- `GET /race-info` - レース情報取得
- `GET /drivers` - ドライバー一覧
- `POST /simulate-strategy` - 戦略シミュレーション
- `GET /optimal-strategy/{driver_number}` - 最適戦略検索

## 📊 シミュレーションモデル

### タイヤ性能
- **SOFT (赤)**: -0.6秒/ラップ, 劣化率: 0.08秒/ラップ
- **MEDIUM (黄)**: 基準 (0.0秒/ラップ), 劣化率: 0.05秒/ラップ
- **HARD (白)**: +0.5秒/ラップ, 劣化率: 0.03秒/ラップ

### ピットストップ
- **標準ピットロス**: 22.0秒
- **最大ピット回数**: 4回
- **最小間隔**: 3ラップ

## 🧪 テスト

### バックエンドテスト
```bash
cd packages/simulator
python3 test_api.py
```

### フロントエンドテスト
```bash
cd packages/front
npm run typecheck
npm run lint
```

## 📈 開発

### 開発環境
- **Node.js**: 18.19.0以上推奨
- **Python**: 3.9以上
- **OS**: macOS, Linux, Windows

### プロジェクト構造
```
f1_strategy_simulator/
├── packages/
│   ├── front/           # Remixフロントエンド
│   │   ├── app/         # Remixアプリケーション
│   │   ├── public/      # 静的ファイル
│   │   └── package.json
│   └── simulator/       # Pythonバックエンド
│       ├── data/        # レースデータ（CSV）
│       ├── api.py       # FastAPI サーバー
│       ├── models.py    # Pydantic モデル
│       └── *.py         # シミュレーションロジック
└── README.md
```

### 新機能追加

1. **新しいAPIエンドポイント**: `packages/simulator/api.py` を編集
2. **新しいUIコンポーネント**: `packages/front/app/components/` に追加
3. **新しいページ**: `packages/front/app/routes/` に追加

## 🐛 トラブルシューティング

### API接続エラー
- バックエンドサーバーが起動しているか確認
- ポート8000が利用可能か確認
- CORS設定を確認

### フロントエンド表示エラー
- Node.jsバージョンを確認（18以上推奨）
- 依存関係を再インストール: `npm install`
- キャッシュクリア: `npm run build`

### データ取得エラー
- インターネット接続を確認
- OpenF1 APIの利用可能性を確認
- `fetch_race_data.py` を再実行

## 🤝 コントリビューション

1. フォークを作成
2. フィーチャーブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## 📝 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 🙏 謝辞

- [OpenF1 API](https://openf1.org/) - F1データの提供
- [Remix](https://remix.run/) - フロントエンドフレームワーク
- [FastAPI](https://fastapi.tiangolo.com/) - バックエンドフレームワーク
- [Tailwind CSS](https://tailwindcss.com/) - スタイリングフレームワーク