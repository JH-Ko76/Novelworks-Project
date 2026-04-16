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

# CloudWatch Logsの権限（デバッグ用）
resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# DynamoDB & Secrets Managerアクセス権限
resource "aws_iam_role_policy" "lambda_policy" {
  name = "inquiry_classifier_lambda_policy"
  role = aws_iam_role.lambda_role.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
         #DynamoDB関連の権限：書き込み（Put）、更新（Update）、読み取り（Get）
        Action   = [
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:GetItem"
        ]
        Effect   = "Allow"
        Resource = [aws_dynamodb_table.inquiry_table.arn]
      },
      # Secrets Manager 権限（Gemini APIキー）
      {
        Action   = ["secretsmanager:GetSecretValue"]
        Effect   = "Allow"
        Resource = [aws_secretsmanager_secret.gemini_api_key.arn]
      },
       # CloudWatch Logs 権限
      {
        Action   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"]
        Effect   = "Allow"
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}