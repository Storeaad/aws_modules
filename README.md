# AWS bills report to slack notifications


<img width="511" alt="image" src="https://github.com/user-attachments/assets/d9152ab6-74b0-45c2-bc5c-12413efe6ef1" />

## Before get started

### Environment values

- os environments

  ```shell
  
  export AWS_ACCESS_KEY_ID={your secret key}
  export AWS_SECRET_ACCESS_KEY={your secret key}
  
  ```

- project `.env` sample  

> [!WARNING]
> **must be change**
>
> 

  ```
  SLACK_HOOK_URL="https://hooks.slack.com/services/xxxxxx"
  CHANNEL="#your-channel-name"
  BOT_NAME="test-app"
  ``` 




### Install package manager

> [!NOTE]
> Use package manager "UV"
> 
> - [install guide](https://docs.astral.sh/uv/getting-started/installation/)


### Install dependency

```shell
uv sync
```

### Run command

```shell
cd src
uv run python3 billing.py 
```

