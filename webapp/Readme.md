# Draft League App

## Set up environment for windows and mac

For windows users:

In your terminal, you need to run these 3 lines seperately
 - set AWS_ACCESS_KEY_ID="your access key" # edit for your own
 - set AWS_SECRET_ACCESS_KEY_ID="your secret access key" # edit for your own
 - set AWS_DEFAULT_REGION=us-east-1


For mac users:

 ```
export AWS_ACCESS_KEY_ID=`aws configure get aws_access_key_id`
export AWS_SECRET_ACCESS_KEY=`aws configure get aws_secret_access_key`
export AWS_DEFAULT_REGION=`aws configure get region`
 ```

# Build and Run Locally

## Build

```bash
cd webapp/
docker build -t draft-league-app .
```

## Run

```bash
cd webapp/
docker run -e AWS_DEFAULT_REGION="%AWS_DEFAULT_REGION%" -e AWS_ACCESS_KEY_ID="%AWS_ACCESS_KEY_ID%" -e AWS_SECRET_ACCESS_KEY="%AWS_SECRET_ACCESS_KEY%" -p 3838:3838 draft-league-app 

```

