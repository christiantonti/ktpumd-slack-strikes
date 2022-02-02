#!/bin/bash
LOG_GROUP=/aws/lambda/ktpSlackStrikes
LOG_STREAM=`aws logs describe-log-streams --log-group-name /aws/lambda/ktpSlackStrikes --max-items 1 --order-by LastEventTime --descending --query logStreams[].logStreamName --output text | head -n 1 -`
aws logs get-log-events --log-group-name $LOG_GROUP --log-stream-name $LOG_STREAM --query events[1:-2].message --output text | head -n -1 - | awk '{ sub(/^[ \t]+/, ""); print "\033[32m"NR,"\033[37m"$0,"\n" }' -