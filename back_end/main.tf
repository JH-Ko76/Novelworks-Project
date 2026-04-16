# 1. DynamoDB Table 生成
resource "aws_dynamodb_table" "inquiry_table" {
  name           = "novel_works_db"
  billing_mode   = "PROVISIONED"
  read_capacity  = 1
  write_capacity = 1
  hash_key       = "inquiry_id"

  attribute {
    name = "inquiry_id"
    type = "S"
  }
}

# 2. Secrets Manager 生成
resource "aws_secretsmanager_secret" "gemini_api_key" {
  name        = "gemini_api_key_${formatdate("YYYYMMDDhhmmss", timestamp())}"
  description = "API Key for Google Gemini"
}

# 3. Lambda Function 生成
resource "aws_lambda_function" "classifier_lambda" {
  filename      = "lambda_function.zip"
  function_name = "inquiry_classifier_handler"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.11"
  timeout       = 15
  memory_size   = 256

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.inquiry_table.name
      SECRET_NAME    = aws_secretsmanager_secret.gemini_api_key.name
    }
  }
}

# 4. API Gateway (REST API) 生成
resource "aws_api_gateway_rest_api" "classifier_api" {
  name = "ClassifierAPI"
}

# ASKリソース：分類用
resource "aws_api_gateway_resource" "proxy" {
  rest_api_id = aws_api_gateway_rest_api.classifier_api.id
  parent_id   = aws_api_gateway_rest_api.classifier_api.root_resource_id
  path_part   = "ask"
}

resource "aws_api_gateway_method" "proxy_method" {
  rest_api_id   = aws_api_gateway_rest_api.classifier_api.id
  resource_id   = aws_api_gateway_resource.proxy.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda_integration" {
  rest_api_id             = aws_api_gateway_rest_api.classifier_api.id
  resource_id             = aws_api_gateway_resource.proxy.id
  http_method             = aws_api_gateway_method.proxy_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.classifier_lambda.invoke_arn
}

# UPDATEリソース：修正用
resource "aws_api_gateway_resource" "update" {
  rest_api_id = aws_api_gateway_rest_api.classifier_api.id
  parent_id   = aws_api_gateway_rest_api.classifier_api.root_resource_id
  path_part   = "update"
}

resource "aws_api_gateway_method" "update_patch" {
  rest_api_id   = aws_api_gateway_rest_api.classifier_api.id
  resource_id   = aws_api_gateway_resource.update.id
  http_method   = "PATCH"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "update_lambda_integration" {
  rest_api_id             = aws_api_gateway_rest_api.classifier_api.id
  resource_id             = aws_api_gateway_resource.update.id
  http_method             = aws_api_gateway_method.update_patch.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.classifier_lambda.invoke_arn
}

# CORS設定：/askリソース用
resource "aws_api_gateway_method" "options_ask" {
  rest_api_id   = aws_api_gateway_rest_api.classifier_api.id
  resource_id   = aws_api_gateway_resource.proxy.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "options_ask_integration" {
  rest_api_id = aws_api_gateway_rest_api.classifier_api.id
  resource_id = aws_api_gateway_resource.proxy.id
  http_method = aws_api_gateway_method.options_ask.http_method
  type        = "MOCK"
  request_templates = { "application/json" = "{\"statusCode\": 200}" }
}

resource "aws_api_gateway_method_response" "options_ask_200" {
  rest_api_id = aws_api_gateway_rest_api.classifier_api.id
  resource_id = aws_api_gateway_resource.proxy.id
  http_method = aws_api_gateway_method.options_ask.http_method
  status_code = "200"
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true,
    "method.response.header.Access-Control-Allow-Methods" = true,
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

resource "aws_api_gateway_integration_response" "options_ask_response" {
  rest_api_id = aws_api_gateway_rest_api.classifier_api.id
  resource_id = aws_api_gateway_resource.proxy.id
  http_method = aws_api_gateway_method.options_ask.http_method
  status_code = aws_api_gateway_method_response.options_ask_200.status_code
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
    "method.response.header.Access-Control-Allow-Methods" = "'POST,OPTIONS,GET'",
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
  depends_on = [aws_api_gateway_integration.options_ask_integration]
}

# CORS設定：/updateリソース用
resource "aws_api_gateway_method" "options_update" {
  rest_api_id   = aws_api_gateway_rest_api.classifier_api.id
  resource_id   = aws_api_gateway_resource.update.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "options_update_integration" {
  rest_api_id = aws_api_gateway_rest_api.classifier_api.id
  resource_id = aws_api_gateway_resource.update.id
  http_method = aws_api_gateway_method.options_update.http_method
  type        = "MOCK"
  request_templates = { "application/json" = "{\"statusCode\": 200}" }
}

resource "aws_api_gateway_method_response" "options_update_200" {
  rest_api_id = aws_api_gateway_rest_api.classifier_api.id
  resource_id = aws_api_gateway_resource.update.id
  http_method = aws_api_gateway_method.options_update.http_method
  status_code = "200"
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true,
    "method.response.header.Access-Control-Allow-Methods" = true,
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

resource "aws_api_gateway_integration_response" "options_update_response" {
  rest_api_id = aws_api_gateway_rest_api.classifier_api.id
  resource_id = aws_api_gateway_resource.update.id
  http_method = aws_api_gateway_method.options_update.http_method
  status_code = aws_api_gateway_method_response.options_update_200.status_code
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
    "method.response.header.Access-Control-Allow-Methods" = "'PATCH,OPTIONS,GET'",
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
  depends_on = [aws_api_gateway_integration.options_update_integration]
}

# デプロイおよびアクセス権限
resource "aws_api_gateway_deployment" "deployment" {
  rest_api_id = aws_api_gateway_rest_api.classifier_api.id

  # コアポイント：すべての関連リソースが作成された後にデプロイが実行されるように強制する
  depends_on = [
    aws_api_gateway_integration.lambda_integration,
    aws_api_gateway_integration.update_lambda_integration,
    aws_api_gateway_integration_response.options_ask_response,
    aws_api_gateway_integration_response.options_update_response
  ]

  triggers = {
    redeployment = sha1(jsonencode({
      resources = [
        aws_api_gateway_resource.proxy.id,
        aws_api_gateway_resource.update.id
      ]
      methods = [
        aws_api_gateway_method.proxy_method.id,
        aws_api_gateway_method.update_patch.id,
        aws_api_gateway_method.options_ask.id,
        aws_api_gateway_method.options_update.id
      ]
      integrations = [
        aws_api_gateway_integration.lambda_integration.id,
        aws_api_gateway_integration.update_lambda_integration.id,
        aws_api_gateway_integration.options_ask_integration.id,
        aws_api_gateway_integration.options_update_integration.id
      ]
      responses = [
        aws_api_gateway_integration_response.options_ask_response.id,
        aws_api_gateway_integration_response.options_update_response.id
      ]
    }))
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "prod" {
  deployment_id = aws_api_gateway_deployment.deployment.id
  rest_api_id   = aws_api_gateway_rest_api.classifier_api.id
  stage_name    = "prod"
}

resource "aws_lambda_permission" "apigw_lambda" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.classifier_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.classifier_api.execution_arn}/prod/*/*"
}
