# file（UP）模块

目标：上传/下载文件（对接 UP 服务）。

## 关键点

- 该模块会强制检查火山鉴权（`VOLC_ACCESSKEY`/`VOLC_SECRETKEY` 或 `~/.volc/.env`）
- `upload` 返回 `path`，用于后续 `download --path`
- `download --key` 可省略，CLI 会先自动获取 DownloadKey

## 常用命令

上传：

```bash
<CMD> --json  file upload \
  --file ./document.pdf \
  --expire 15h \
  --content-type application/pdf
```

下载：

```bash
<CMD> --json  file download \
  --path "<REMOTE_PATH>" \
  --output ./document.pdf
```

## 排障

- 鉴权缺失：设置环境变量或配置 `~/.volc/.env`，然后重试
- 下载失败：确认 path 来自 upload 的返回；必要时显式传 `--key`
