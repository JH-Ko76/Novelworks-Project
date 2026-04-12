# Lambda Execution Role
resource "aws_iam_role" "lambda_role" {
  name = "inquiry_classifier_lambda_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

# CloudWatch Logs 기본 권한 연결
resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# 통합 상세 권한 (Secrets Manager + DynamoDB + Logs)
resource "aws_iam_role_policy" "lambda_extra_policy" {
  name = "lambda_extra_policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        # 1. Secrets Manager: 특정 Gemini API Key만 읽기 허용
        Action   = ["secretsmanager:GetSecretValue"]
        Effect   = "Allow"
        Resource = [aws_secretsmanager_secret.gemini_api_key.arn]
      },
      {
        # 2. DynamoDB: 특정 테이블에만 데이터 기록 허용
        Action   = ["dynamodb:PutItem"]
        Effect   = "Allow"
        Resource = [aws_dynamodb_table.inquiry_table.arn]
      },
      {
        # 3. 로깅 권한 상세 설정
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Effect   = "Allow"
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}
