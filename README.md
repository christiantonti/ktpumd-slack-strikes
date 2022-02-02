# ktpumd-slack-strikes
#### Codebase for serverless strike tracking for Kappa Theta Pi Epsilon Chapter

## General Usage
All lambda function code is located in [lambda_function.py](lambda_function.py) (for now). Once changes are made, they can be deployed to AWS by using [deploy.sh](deploy.sh). After running a command on the slackbot, you can fetch a pretty-print of the latest log stream using [getlogs.sh](getlogs.sh). For deployment and logging to work, your AWS CLI must be configured properly, with the correct permissions to access/modify Lambda and CloudWatch (TODO: Add instructions for configuring AWS CLI). Otherwise, updates can be made by manually pasting changes in through the Lambda console and pressing deploy; log streams can be found in CloudWatch console.

## Additional Details
This slackbot is designed to run completely serverless within AWS using Lambda and DynamoDB. Up to a certain Lambda request capacity or DynamoDB size/read/writes, this falls completely under AWS Free Tier. Later I will add instructions on setting up the slash command bot Slack-side, bringing it into a workspace, and actually using the bot.
