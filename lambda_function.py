import os
import json
import boto3
import urllib.request
from datetime import datetime

def get_secret():
    secret_name = os.environ.get('SECRET_NAME', 'gemini_api_key_v1')
    region_name = "ap-northeast-2"
    client = boto3.client("secretsmanager", region_name=region_name)
    response = client.get_secret_value(SecretId=secret_name)
    secret_value = response['SecretString']
    
    try:
        secret_dict = json.loads(secret_value)
        return secret_dict.get('api_key') # 保存したときに使った「キー」の名前を入力
    except json.JSONDecodeError:
        # 一般テキスト（プレーンテキスト）で保存した場合は、そのまま返し
        return secret_value


def classify_with_gemini(api_key, text):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    examples = [
        {"query": "ログインが何度も失敗してしまいます。", "category": "技術"},
        {"query": "決済のレシートはどこで受け取れますか？", "category": "料金"},
        {"query": "オペレーターの対応がとても不親切です。", "category": "クレーム"}
        ]
    example_str = "\n".join([f"問い合わせ: {ex['query']} -> 分類: {ex['category']}" for ex in examples])

    # プロンプトに「confidence」の測定指針を定義
    prompt = f"""
あなたはカスタマーセンターのお問い合わせ分類器です。以下のルールを厳守してください。

### 例文 (Few-shot)
{example_str}

### 指示
1. お問い合わせ内容を分析し、どのカテゴリーに該当するかを論理的に推論してください。
2. 分類結果は必ず [技術, 料金, クレーム, その他] のいずれかでなければなりません。
3. 分類結果に対する確信度を0.0から1.0の数値で示してください。（例：確実なら0.9、曖昧なら0.4）
4. 必ず以下のJSON形式のみで回答してください。


### 出力形式（JSON）
{{
  "reason": "分類 理由",
  "category": "最終分類",
  "confidence": 0.00
}}

### 分析するお問い合わせ内容
"{text}"
"""

    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    data = json.dumps(payload).encode('utf-8')
    
    req = urllib.request.Request(url, data=data)
    req.add_header('Content-Type', 'application/json')
    req.add_header('x-goog-api-key', api_key.strip()) 
    
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            res_json = json.loads(response.read().decode('utf-8'))
            raw_response = res_json['candidates'][0]['content']['parts'][0]['text'].strip()
            
            if "```json" in raw_response:
                raw_response = raw_response.split("```json")[1].split("```")[0].strip()
            
            ai_data = json.loads(raw_response)
            
            # 確信度スコアとカテゴリを抽出
            category = ai_data.get("category", "その他")
            confidence = ai_data.get("confidence", 0.0)
            
            # 確信度が低い場合は「確認が必要です」フラグを立てます   
            if confidence < 0.5:
                print(f"DEBUG: Low confidence ({confidence}) for text: {text}")
                return "確認が必要です"
            
            if category in ["技術", "料金", "クレーム"]:
                return category
            return "その他"
            
    except Exception as e:
        print(f"AI Classification Error: {e}")
        return "その他"

def lambda_handler(event, context):
    headers = {
        'Access-Control-Allow-Origin': 'Novelworks.github.io', # CORS 특정 도메인으로 설정 
        'Access-Control-Allow-Methods': 'POST,GET,OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }

    # API GatewayのOPTIONSリクエスト処理
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers}

    try:
        body = json.loads(event.get('body', '{}'))
        user_query = body.get('query', '')

        # 入力値の長さ制限
        if len(user_query) > 1000:
            return {'statusCode': 400, 'body': json.dumps({'error': 'Input too long'})}

        # 1. AIによる分類を実行
        api_key = get_secret()
        category = classify_with_gemini(api_key, user_query)

        # 2. Amazon DynamoDB に保存
        table_name = os.environ.get('DYNAMODB_TABLE', 'novel_works_db')
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)
        
        item = {
            'inquiry_id': context.aws_request_id,
            'content': user_query,
            'category': category,
            'timestamp': datetime.utcnow().isoformat()
        }
        table.put_item(Item=item)

return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'message': f"分類結果: {category}",
                'category': category
            }, ensure_ascii=False)
        }
        
    except Exception as e: # try와 줄을 맞춰야 합니다.
        print(f"Error detail: {e}") 
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': 'An internal error occurred.'}) 
        }