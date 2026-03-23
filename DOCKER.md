# Docker 部署说明

## 快速启动

1. 复制环境变量配置：
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，填入你的配置：
```
OPENAI_API_KEY=你的API密钥
MCBBS_USERNAME=你的用户名
MCBBS_PASSWORD=你的密码
```

3. 确保 `config.json` 中的 API 配置正确

4. 启动容器：
```bash
docker-compose up -d
```

## 管理命令

查看日志：
```bash
docker-compose logs -f
```

停止服务：
```bash
docker-compose down
```

重启服务：
```bash
docker-compose restart
```

## 工作机制

- 容器启动后每 10 分钟自动运行一次 `main.py`
- 输出文件保存在 `./output` 目录（与宿主机同步）
- 内存限制 512MB，预留 256MB
- 每次运行后自动垃圾回收，避免内存泄漏

## 注意事项

- 首次运行会自动创建 `output` 目录
- 状态文件 `.state.json` 和 `.posted.json` 会持久化保存
- 容器会在系统重启后自动启动（`restart: unless-stopped`）
