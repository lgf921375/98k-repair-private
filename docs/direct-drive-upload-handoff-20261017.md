# 98K 加密备份：新加坡服务器直传 Google Drive 交接

2026-10-17 10:43 +08，Remote Desktop Commander 已进行下列只读诊断和非破坏性安装。**目前没有发生直传上传，Google Drive 服务器 OAuth 尚未授权。**

## 已确认

- 新加坡 `VM-0-12-ubuntu`，运行 `wg0` 和 `wg-quick@wg0`。香港 `hk-relay-01` 通过 UDP/443 DNAT/MASQUERADE 中转，但未核实所有下一跳详细规则。
- 新加坡设备 WireGuard 接口 2026-10-17 10:40:57 至 10:41:05 的 8 秒采样中 RX/TX、错误与丢弃计数不变；香港 `eth0` 同期另 8 秒有少量流量。不能由短样本证明线路性能瓶颈。
- 服务器能请求 `https://www.googleapis.com/drive/v3/about`，未携带 OAuth 凭据返回 HTTP 401（预期）。
- 已通过 apt 安装 `rclone 1.60.1`，未改变现有 VPN、防火墙和游戏服务；原备份文件仍存在。
- 在原服务器准备了脚本：
  `/srv/projects/98k-backups/20261017/upload-to-drive-after-auth.sh`。
  它会先用 SHA256 核实加密归档，检查名为 `gdrive98k` 的已授权 rclone 远程，然后把 **仅加密的** `98k-core-recovery-20261017.tar.zst.gpg` 上传到用户现有私有 Google Drive `98K传奇修复` 文件夹，并输出日志 `upload-to-drive.log`。
- 脚本已通过 `bash -n` 检查，**未进行 OAuth、未执行上传及云端校验**。
- 服务器当前 `rclone listremotes` 为空。

## 下一步与保护

需要用户明确批准服务器访问自己的 Google Drive，并在**私密身份验证流程**中完成 OAuth。ChatGPT Google Drive 连接器的令牌不会自动转给服务器。请不要在公开 GitHub、聊天或截图分享 refresh token、OAuth 配置文件、恢复密钥或 Google 密码。

OAuth 配置好且验证文件夹权限后，单独启动上述脚本，可在用户断开 ChatGPT 对话时继续执行。随后通过 Google Drive 连接器检查文件大小和内容传输成功；再进行异地解密还原测试。没有云端文件和校验成功之前，不能宣称异地备份已完成。

Google Drive 2.7GB 手机上传速度缓慢，可考虑在服务器直传成功后取消手机重复任务；在此之前保留当前上传，以免备份减少冗余。

官方指引：https://rclone.org/remote_setup/ 及 https://rclone.org/drive/。
