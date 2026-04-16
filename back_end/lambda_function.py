import os
import json
import boto3
import urllib.request
from datetime import datetime, timezone

# 리전명, 시크릿 네임 전역변수로 관리 
SECRET_NAME = os.environ.get('SECRET_NAME')
AWS_REGION = os.environ.get('AWS_REGION', 'ap-northeast-2')
#dynamodb table name 전역변수로 선언  (람다 특징을 사용해 Warm Start로 구현)
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
    #secretsmanager 접근
    client = boto3.client("secretsmanager", region_name=region_name)
    response = client.get_secret_value(SecretId=secret_name)
    secret_value = response['SecretString']
    # 만약 JSON 형식으로 저장했다면 파싱이 필요합니다.
    try:
        secret_dict = json.loads(secret_value)
        return secret_dict.get('api_key') # 저장할 때 쓴 '키' 이름을 넣으세요.
    except json.JSONDecodeError:
        # 일반 텍스트(Plaintext)로 저장했다면 그대로 반환
        return secret_value

def classify_with_gemini(api_key, text):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    examples = [
        {"query": "ログインが何度も失敗してしまいます。", "category": "技術"},
        {"query": "決済のレシートはどこで受け取れますか？", "category": "料金"},
        {"query": "オペレーターの対応がとても不親切です。", "category": "クレーム"}
        ]
    example_str = "\n".join([f"問い合わせ: {ex['query']} -> 分類: {ex['category']}" for ex in examples])

    # 프롬프트에 'confidence' 측정 지침 추가
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
            
            # 확신도 점수와 카테고리 추출
            category = ai_data.get("category", "その他")
            confidence = ai_data.get("confidence", 0.0)
            
            # [핵심 로직] 확신도가 낮으면 '確認が必要です' 플래그 세움
            # 보안 관제 임계값 설정과 같은 원리입니다.
            if confidence < 0.5:
                print(f"DEBUG: Low confidence ({confidence}) for text: {text}")
                return "確認必要です"
            
            if category in ["技術", "料金", "クレーム"]:
                return category
            return "その他"
            
    except Exception as e:
        print(f"AI Classification Error: {e}")
        return "確認必要です"

def lambda_handler(event, context):
    headers = {
        'Access-Control-Allow-Origin': '*', # 이번에는 테스트 단계이므로 모두 허용을 했지만, 실제 서비스 시 특정 도메인 설정이 필요합니다.
        'Access-Control-Allow-Methods': 'POST,GET,OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }

    # API Gateway의 OPTIONS(Preflight) 요청 처리
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers}

    try:
        body = json.loads(event.get('body', '{}'))
        user_query = body.get('query', '')

        # 입력값 길이 제한 (기본적인 방어)
        if len(user_query) > 500:
            return {'statusCode': 400, 'body': json.dumps({'error': 'Input too long'})}

        # 1. AI 분류 실행
        api_key = get_secret_cached()
        category = classify_with_gemini(api_key, user_query)

        # 2. DynamoDB 저장        
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