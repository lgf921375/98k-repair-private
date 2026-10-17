# 98K V5A 手机上传卡顿排查与可靠性优化（2026-10-17）

## 现象
用户手机使用 sing-box 1.14.3 / V5A，通过中国移动或电信 → 香港 hk-relay-01 (UDP/443 NAT) → 新加坡 VM-0-12-ubuntu (WireGuard wg0) → Google Drive 上传手机里的加密 98K 备份，重新开始有短暂速度峰值，随后常下降至几十 KB/s 或接近零。

## 静态核查与证据
- V5A 里 Google Drive App (`com.google.android.apps.docs`) 走 WireGuard `wg-hk-sg`；TUN=gvisor，端点 MTU=1280；Peer keepalive=25s。
- 日志 `测试logs_20261017_113616.txt` 约 1634 行；ERROR 24 条，其中可准确归属 Drive 的 IPv4/TCP/443 错误 3 条，可归属 ChatGPT 的 15 条，另有归属不明的 Google IPv4 错误 5 条及国内应用错误 1 条。`endpoint not connected` 是连接关闭报错，不能单独判断丢包或 Google 上传失败。
- 香港和新加坡部署非驻留的只读 90 秒采样（每5秒读取 sysfs 网卡计数）。香港 eth0 大部分样本 0.001~0.048Mbps，短时最高 0.226Mbps；新加坡 wg0 大多数 0~0.001Mbps，最高一个短时样本约0.118Mbps；两端网卡 error/drop 增量均为零。
- 这说明采样期没有持续大文件上传流量进入隧道，但没有同一时刻手机 Drive 百分比及专属包级数据，不能锁定具体断点；这也不是服务器持续最大可用带宽的测速。
- **未修改** WireGuard、NAT、系统 MTU、BBR 或现有 sing-box 在线配置；没有中断上传。

## 本轮可靠性优化（手机可选）
准备了一个 Termux shell 脚本 `98K_phone_drive_chunks_128MiB.sh` （文件已在聊天下载区提供，不含认证令牌）。它首先核对加密备份原文件 SHA256 `2a2b8d3e53bf3af456f7c11568118d38897c793e6f96796200ebcfe3e39dadc`，匹配后切成不超过128MiB的独立分卷，生成每卷 SHA256 清单和恢复说明。手机再通过**现有香港→新加坡 WireGuard**将所有分卷上传 Drive，成功的分卷不必因其他分卷失败而重传。**不会提速线路 Mbps，本质是减少失败重传损失。**

已在独立本地随机小文件模拟校验：分卷、每卷SHA256、重组合并逐字节一致、重运行不重复覆盖，均通过。未在用户 Termux 和 Google Drive 实测。用户需明确中止/完成原来的大文件任务后再生成分卷，防止同时 I/O 竞争。

## 下一步
请用户在上传低速/停住的同一分钟记录：Drive进度、sing-box实时上传速率、精确时间；导出该分钟日志。如要辨别 Drive App 本身的上传问题，可选取同一个小文件使用 Drive App 与其他客户端在相同VPN下对照；若客户端都慢，再进行香港 NAT 和新加坡 WireGuard 双端同步流量与重传监测。V5B 加 QUIC 阻断是未验证对照，不应当作已证实提速方案。

安全边界：不泄露源VPN私钥、Google OAuth凭据或GPG解密密钥。现有GitHub仓库虽名带private，实际上是公开仓库。
