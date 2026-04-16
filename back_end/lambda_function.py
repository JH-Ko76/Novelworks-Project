import os
import json
import boto3
import urllib.request
from datetime import datetime, timezone

# リージョン名、シークレットネームをグローバル変数で管理
SECRET_NAME = os.environ.get('SECRET_NAME')
AWS_REGION = os.environ.get('AWS_REGION', 'ap-northeast-2')
#dynamodb table name グローバル変数として宣言（ラムダの特徴を利用して Warm Start で実装）
table_name = os.environ.get('DYNAMODB_TABLE', 'novel_works_db')
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
table = dynamodb.Table(table_name)
_cached_api_key = None

def get_secret_cached():
    global _cached_api_key
    if _cached_api_key is not None:
        return _cached_api_key

    _cached_api_key = get_secret()
    return _cached_api_key

def get_secret():
    secret_name = SECRET_NAME
    region_name = AWS_REGION
    #secretsmanager Access
    client = boto3.client("secretsmanager", region_name=region_name)
    response = client.get_secret_value(SecretId=secret_name)
    secret_value = response['SecretString']
    try:
        secret_dict = json.loads(secret_value)
        return secret_dict.get('api_key') 
    except json.JSONDecodeError:
        # Plainext で保存した場合はそのまま返す
        return secret_value

def classify_with_gemini(api_key, text):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    examples = [
        {"query": "ログインが何度も失敗してしまいます。", "category": "技術"},
        {"query": "決済のレシートはどこで受け取れますか？", "category": "料金"},
        {"query": "オペレーターの対応がとても不親切です。", "category": "クレーム"}
        ]
    example_str = "\n".join([f"問い合わせ: {ex['query']} -> 分類: {ex['category']}" for ex in examples])

    # プロンプトに「confidence」測定指針を追加
    prompt = f"""
    [Role]
    Expert Customer Service Classifier.
    
    [Instructions]
    1. Analyze the input text and classify into: [技術, 料金, クレーム, その他].
    2. Assign a Confidence Score (0.0-1.0):
    - 1.0: Clear keywords (e.g., 決済, ログイン, 返金, 被害).
    - 0.7: Context-based inference, but keywords are vague.
    - Below 0.5: Insufficient evidence (e.g., あの, できない).
    - Below 0.4: Meaningless input (e.g., あ, s).
    3. Output MUST be in JSON format only.
    
    [Output Format]
    {{
        "reason": "Classification logic in Japanese",
        "category": "One of the 4 categories",
        "confidence": 0.00
    }}
    ### Input Text to Analyze
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
            
            # 確信度スコアとカテゴリ抽出
            category = ai_data.get("category", "その他")
            confidence = ai_data.get("confidence", 0.0)
            
            # Human-in-the-Loop
            if confidence < 0.5:
                print(f"DEBUG: Low confidence ({confidence}) for text: {text}")
                return "確認必要です"
            
            if category in ["技術", "料金", "クレーム"]:
                return category
            return "その他"
            
    except Exception as e:
        return "AI Classification Error"

def lambda_handler(event, context):
    headers = {
        'Access-Control-Allow-Origin': '*', # 今回はテスト段階なので、すべて許可しました。
        'Access-Control-Allow-Methods': 'POST,GET,OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }

    # API Gateway OPTIONS
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers}

    try:
        body = json.loads(event.get('body', '{}'))
        user_query = body.get('query', '')
        # 修正用の既存IDを取得する
        inquiry_id = body.get('inquiry_id')
        
        # 入力値の長さ制限
        if len(user_query) > 500:
            return {'statusCode': 400, 'body': json.dumps({'error': 'Input too long'})}

        # 1. AI分類の実行
        api_key = get_secret_cached()
        category = classify_with_gemini(api_key, user_query)

        # 2. 確認が必要な場合は修正
        # (1) 修正依頼の場合（フロントエンドから inquiry_id を送信）
        if inquiry_id:
            print(f"DEBUG: Update request received for inquiry_id: {inquiry_id}")
            # 이 ID를 그대로 사용해 DynamoDB에 저장합니다. (PutItem 시 자동 덮어씌우기됨)
            pass

        # (2) 初回作成の場合（フロントエンドから inquiry_id を送信しない）
        else:
            print(f"DEBUG: Create request received. Generating new inquiry_id.")
            # 従来と同様に、aws_request_id を使用して新しいIDを生成します。
            inquiry_id = context.aws_request_id

        # 2. DynamoDB の保存       
        item = {
            'inquiry_id': context.aws_request_id,
            'content': user_query,
            'category': category,
            'timestamp': datetime.now(timezone.utc).isoformat(timespec='seconds')
        }
        table.put_item(Item=item)
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({'category': category}, ensure_ascii=False)
        }
    except Exception as e: 
        
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': 'An internal error occurred.'}) 
        }
