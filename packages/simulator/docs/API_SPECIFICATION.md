# F1 Strategy Simulator API 仕様書

## 概要

F1ピット戦略シミュレーターのバックエンドAPI仕様書です。実際のF1レースデータ（2024年日本GP）を使用して、代替ピット戦略をシミュレーションし、最適化を行うことができます。

## 基本情報

- **Base URL**: `http://localhost:8000`
- **API Documentation**: `http://localhost:8000/docs` (Swagger UI)
- **API Version**: 1.0.0
- **Framework**: FastAPI
- **Data Format**: JSON

## 認証

現在のバージョンでは認証は不要です。

## エンドポイント一覧

### 1. ヘルスチェック

**GET** `/`

APIの動作状況を確認します。

#### レスポンス例
```json
{
  "message": "F1 Strategy Simulator API",
  "status": "running",
  "version": "1.0.0",
  "simulator_loaded": true
}
```

### 2. レース情報取得

**GET** `/race-info`

読み込まれているレースの基本情報を取得します。

#### レスポンス例
```json
{
  "session_key": 9496,
  "race_name": "2024 Japan GP",
  "total_laps": 53,
  "drivers": [
    {
      "driver_number": 1,
      "name": "M VERSTAPPEN",
      "team": "Red Bull Racing",
      "abbreviation": "VER"
    }
  ]
}
```

### 3. 全ドライバー一覧

**GET** `/drivers`

レースに参加した全ドライバーの情報を取得します。

#### レスポンス例
```json
[
  {
    "driver_number": 1,
    "name": "M VERSTAPPEN",
    "team": "Red Bull Racing",
    "abbreviation": "VER"
  },
  {
    "driver_number": 16,
    "name": "C LECLERC",
    "team": "Ferrari",
    "abbreviation": "LEC"
  }
]
```

### 4. 実際の戦略取得

**GET** `/actual-strategy/{driver_number}`

指定したドライバーの実際のピット戦略を取得します。

#### パラメータ
- `driver_number` (int): ドライバー番号 (1-99)

#### レスポンス例
```json
[
  {
    "lap": 1,
    "tire_compound": "MEDIUM",
    "pit_loss": 22.0
  },
  {
    "lap": 16,
    "tire_compound": "MEDIUM",
    "pit_loss": 22.0
  }
]
```

### 5. 戦略シミュレーション

**POST** `/simulate-strategy`

代替ピット戦略をシミュレーションし、実際の戦略と比較します。

#### リクエストボディ
```json
{
  "driver_number": 1,
  "pit_stops": [
    {
      "lap": 15,
      "tire_compound": "SOFT",
      "pit_loss": 22.0
    },
    {
      "lap": 35,
      "tire_compound": "MEDIUM",
      "pit_loss": 22.0
    }
  ]
}
```

#### レスポンス例
```json
{
  "driver_number": 1,
  "driver_name": "M VERSTAPPEN",
  "actual_strategy": [
    {
      "lap": 1,
      "tire_compound": "MEDIUM",
      "pit_loss": 22.0
    }
  ],
  "alternative_strategy": [
    {
      "lap": 15,
      "tire_compound": "SOFT",
      "pit_loss": 22.0
    }
  ],
  "actual_total_time": 5121.7,
  "alternative_total_time": 5158.0,
  "time_difference": 36.3,
  "improvement": false,
  "predicted_position": null
}
```

### 6. 最適戦略検索

**GET** `/optimal-strategy/{driver_number}`

指定したドライバーの最適なピット戦略を検索します。

#### パラメータ
- `driver_number` (int): ドライバー番号 (1-99)
- `max_stops` (int, optional): 最大ピット回数 (1-3, default: 2)
- `top_n` (int, optional): 返す戦略の数 (1-20, default: 5)

#### レスポンス例
```json
{
  "driver_number": 1,
  "driver_name": "M VERSTAPPEN",
  "current_strategy": [
    {
      "lap": 1,
      "tire_compound": "MEDIUM",
      "pit_loss": 22.0
    }
  ],
  "optimal_strategies": [
    {
      "strategy": [
        {
          "lap": 18,
          "tire_compound": "SOFT",
          "pit_loss": 22.0
        }
      ],
      "total_time": 5092.0,
      "improvement": 29.7,
      "rank": 1
    }
  ]
}
```

### 7. タイヤ劣化分析

**GET** `/tire-degradation/{driver_number}`

指定したドライバーのタイヤ劣化パターンを分析します。

#### パラメータ
- `driver_number` (int): ドライバー番号 (1-99)

#### レスポンス例
```json
{
  "driver_number": 1,
  "driver_name": "M VERSTAPPEN",
  "stints": [
    {
      "compound": "MEDIUM",
      "stint_length": 15,
      "degradation_rate": 0.149,
      "average_lap_time": 96.5,
      "stint_start": 1
    }
  ],
  "avg_degradation_by_compound": {
    "MEDIUM": {
      "avg_degradation": 0.149,
      "avg_lap_time": 96.5,
      "avg_stint_length": 15.0
    },
    "HARD": {
      "avg_degradation": 0.017,
      "avg_lap_time": 94.7,
      "avg_stint_length": 18.0
    }
  }
}
```

### 8. 複数ドライバー戦略分析

**POST** `/field-analysis`

複数ドライバーの戦略変更がフィールド全体に与える影響を分析します。

#### リクエストボディ
```json
{
  "strategies": {
    "1": [
      {
        "lap": 18,
        "tire_compound": "SOFT",
        "pit_loss": 22.0
      }
    ],
    "16": [
      {
        "lap": 20,
        "tire_compound": "SOFT",
        "pit_loss": 22.0
      }
    ]
  }
}
```

#### レスポンス例
```json
{
  "scenario_name": "Custom Field Analysis",
  "driver_results": {
    "1": {
      "driver_number": 1,
      "driver_name": "M VERSTAPPEN",
      "time_difference": 35.9,
      "improvement": false,
      "predicted_position": 1
    }
  },
  "total_time_saved": -66.0,
  "drivers_improved": 0,
  "average_improvement": 33.0
}
```

## データモデル

### タイヤコンパウンド
```
SOFT: 最も速いが劣化が早い
MEDIUM: バランスタイプ（基準）
HARD: 最も遅いが持続性がある
```

### タイヤ性能モデル
- **SOFT**: -0.6秒/ラップ (vs MEDIUM), 劣化率: 0.08秒/ラップ
- **MEDIUM**: 基準 (0.0秒/ラップ), 劣化率: 0.05秒/ラップ  
- **HARD**: +0.5秒/ラップ (vs MEDIUM), 劣化率: 0.03秒/ラップ

### ピットストップ
- **標準ピットロス**: 22.0秒
- **最小間隔**: 3ラップ
- **最大回数**: 4回

## エラーハンドリング

### 標準エラーレスポンス
```json
{
  "error": "Invalid input",
  "detail": "Driver number must be between 1 and 99",
  "code": "VALIDATION_ERROR"
}
```

### エラーコード一覧
- **400**: バリデーションエラー、無効なリクエスト
- **404**: 指定されたリソースが見つからない
- **500**: サーバー内部エラー

## バリデーションルール

### ピットストップ
- ラップ番号: 1-100
- ピット回数: 最大4回
- ピット間隔: 最小3ラップ
- ピットロス: 15.0-40.0秒

### ドライバー番号
- 範囲: 1-99
- 実在ドライバーのみ有効

## 使用例

### cURLでの基本的な使用方法

```bash
# ヘルスチェック
curl http://localhost:8000/

# ドライバー一覧取得
curl http://localhost:8000/drivers

# 戦略シミュレーション
curl -X POST http://localhost:8000/simulate-strategy \
  -H "Content-Type: application/json" \
  -d '{
    "driver_number": 1,
    "pit_stops": [
      {"lap": 15, "tire_compound": "SOFT"},
      {"lap": 35, "tire_compound": "MEDIUM"}
    ]
  }'

# 最適戦略検索
curl "http://localhost:8000/optimal-strategy/1?max_stops=2&top_n=3"
```

### Pythonでの使用例

```python
import requests

# 戦略シミュレーション
response = requests.post('http://localhost:8000/simulate-strategy', json={
    "driver_number": 1,
    "pit_stops": [
        {"lap": 15, "tire_compound": "SOFT"},
        {"lap": 35, "tire_compound": "MEDIUM"}
    ]
})

result = response.json()
print(f"Time difference: {result['time_difference']:.1f}s")
```

## 開発・運用情報

### 環境要件
- Python 3.9+
- FastAPI 0.116.1+
- pandas 2.3.1+
- numpy 2.0.2+

### 起動方法
```bash
# 開発環境
python3 api.py

# 本番環境
uvicorn api:app --host 0.0.0.0 --port 8000
```

### テスト実行
```bash
python3 test_api.py
```

### パフォーマンス考慮事項
- 最適戦略検索は計算量が多いため、`max_stops`と`top_n`を適切に設定
- 大量の同時リクエストを処理する場合は、ワーカープロセス数を調整
- データはメモリ上にロードされるため、大規模データセットの場合は要注意

## 今後の拡張予定

- [ ] 複数レース対応
- [ ] SC/VSC（セーフティカー）対応  
- [ ] 天候・路面状況の考慮
- [ ] リアルタイム戦略最適化
- [ ] WebSocket対応
- [ ] 認証・認可機能
- [ ] レート制限機能
- [ ] キャッシュ機能