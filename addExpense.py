import json
import boto3
import uuid
from decimal import Decimal

# DynamoDB setup
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('MyExpenses')

# SNS setup
sns = boto3.client('sns')
SNS_TOPIC_ARN = "arn:aws:sns:ap-southeast-1:401853833115:ExpenseNotifAlert"

def lambda_handler(event, context):
    try:
        # Parse request body
        if "body" in event:
            body = json.loads(event["body"])
        else:
            body = event

        # Extract and convert amount to Decimal
        expense_id = str(uuid.uuid4())
        amount = Decimal(str(body["amount"]))  # ✅ Use Decimal
        category = body["category"]
        date = body["date"]

        # Save to DynamoDB
        table.put_item(
            Item={
                "expense_id": expense_id,
                "amount": amount,
                "category": category,
                "date": date
            }
        )

        # Send SNS alert if amount > 5000
        if amount > 5000:
            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject="💸 Expense Alert: Over ₹5000",
                Message=f"⚠️ High Expense Alert!\nAmount: ₹{amount}\nCategory: {category}\nDate: {date}"
            )
        
        
        return {
            "statusCode": 200,
            "body": json.dumps("✅ Expense added successfully!")
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps(f"❌ Error: {str(e)}")
        }