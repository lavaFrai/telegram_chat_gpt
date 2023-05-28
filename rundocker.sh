docker stop ai_chat_bot
docker rm ai_chat_bot
docker run -it -d --restart=always --name=ai_chat_bot $(docker build -q .)
