# AI Studio Proxy API

## 项目描述
将 Google AI Studio 网页界面转换为 OpenAI 兼容 API 的代理服务

## 启动命令
```powershell
cd D:\AIstudioProxyAPI\AIstudioProxyAPI
poetry run python launch_camoufox.py --headless
```

## 测试命令
```powershell
# 健康检查
curl http://127.0.0.1:2048/health

# 模型列表
curl http://127.0.0.1:2048/v1/models

# 聊天
curl -X POST http://127.0.0.1:2048/v1/chat/completions -H "Content-Type: application/json" -d "{\"model\":\"gemini-2.0-flash\",\"messages\":[{\"role\":\"user\",\"content\":\"你好\"}]}"
```

## 配置
- API 端口: 2048
- 流式代理端口: 3120
- 认证文件: auth_profiles/active/auth_auto_1772950763.json
- 日志目录: logs/

## 常用操作
1. 启动服务: `poetry run python launch_camoufox.py --headless`
2. 调试模式: `poetry run python launch_camoufox.py`
3. 查看日志: logs/app.log
