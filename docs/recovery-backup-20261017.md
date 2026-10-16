# 2026-10-17 核心恢复包：服务端已生成并验证

## 已实测状态

- 服务端归档任务：`98k-preservation-snapshot-20261017.service`，最后 `Result=success`、`ActiveState=inactive`。
- 加密文件：`98k-core-recovery-20261017.tar.zst.gpg`，约 **2.8 GiB**。
- 加密方式：先 tar、zstd，再使用 GPG 对称 AES-256；随机生成的恢复密钥另存于 `recovery-key.txt`。
- 已通过：压缩任务结束；GPG 解密流 + zstd 检查；服务端 SHA256 验证。
- SHA256：`2a2b8d3e53bf3baf456f7c11568118d38897c793e6f96796200ebcfe3e39dadc`。
- HTTP 匿名请求加密文件和恢复密钥均返回 `401`；仅通过**原有已认证私人文件库**提供下载。
- **尚未通过**：用户将归档和密钥复制到服务器以外的设备/云存储、异地恢复试验。

## 私人文件库（需要原网站登录）

请登录你已有的 `899yx.online` 私人文件库，进入 `98k-backups/20261017/`。

必须获取：
1. `98k-core-recovery-20261017.tar.zst.gpg`
2. `recovery-key.txt`
3. `98k-core-recovery-20261017.sha256`
4. `README-RECOVERY.txt`

**不要在公共 GitHub 上传恢复密钥或未加密版本。** 把密钥与密文分别保管，下载完成后检查 SHA256。

## 归档范围与边界

包含服务器保存的 98K 七个原始文件、修复工作区的核心脚本、反编译研究资料、候选补丁、隔离测试数据和证据。

由于原服务器磁盘空间有限，创建时排除了可再装的测试 chroot `usr/var/home`、临时测试日志、apk-out 构建中间结果、以及多份签名候选 APK 输出。因此这不是逐字节全盘快照。需要新服务器重新构建测试 Linux 环境，或另行备份全部缓存和历史 APK。

## 从另一台 Linux 机器验证

```bash
sha256sum -c 98k-core-recovery-20261017.sha256
gpg --batch --pinentry-mode loopback \
  --passphrase-file recovery-key.txt \
  --decrypt 98k-core-recovery-20261017.tar.zst.gpg \
  | zstd -dc | tar -tf - | head
```

不要直接在正式服务器解包覆盖，不要在公共 CI 日志打印密码。下一阶段需要有合法的服务器终端或在独立环境中从备份重新构建；GitHub 文档仓库本身不能代替服务器访问权限。

> 注意：文件在原服务器成功生成，不等于已经异地备份成功。取走并校验后再确认。
