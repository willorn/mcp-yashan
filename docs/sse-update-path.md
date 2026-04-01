# SSE -> Streamable HTTP 简化重构计划（自用版）

## 目标
- 现在的 SSE 版先不要删
- 在现有项目上补一个 Streamable HTTP 入口
- 让 Codex 能正常连上并调用数据库工具
- 确认可用后，再决定是否移除旧 SSE

---

## 1. 先确认现状
- 找到现在 SSE 的入口代码
- 确认现有 MCP 能力有哪些：
  - initialize
  - tools/list
  - 主要 tool（尤其是查数据库的）
- 记下当前 tool 名称和参数结构
- 先不要改 tool 逻辑

---

## 2. 把业务逻辑和 SSE 入口稍微拆开
目标：
- 把“查数据库”“参数校验”“tool 注册”保留下来
- 不要让这些逻辑直接绑死在 SSE handler 上

做法：
- 提取一个公共的 server/core 层
- 旧 SSE 和新 HTTP 都调用这套公共逻辑

注意：
- 不需要做很复杂的抽象
- 只要做到“换个 transport，不重写 tool”就够了

---

## 3. 新增一个 Streamable HTTP endpoint
例如新增：
- /mcp

要求：
- 先支持最基本的：
  - initialize
  - tools/list
  - 一个数据库查询 tool
- 能正常返回 JSON
- 如果框架/SDK要求支持流式，再补 SSE 响应流

重点：
- 不要去改旧 SSE endpoint
- 新旧先同时保留，方便出问题时回退

---

## 4. 用官方 SDK / transport，尽量别自己手搓协议
原则：
- 如果你用的语言对应 SDK 已支持 Streamable HTTP，直接用 SDK
- 不要自己拼 content-type、握手流程、消息格式，容易踩坑

目标：
- 少写 transport 细节
- 重点放在让现有数据库 tool 复用起来

---

## 5. 本地手工验证
至少测这几项：
- Codex 能连上新 /mcp
- initialize 成功
- tools/list 成功
- 能调用一个实际数据库查询 tool
- 返回结果正常
- 报错时不会返回 text/plain 或 html 错误页

如果这里已经能通，基本就够用了

---

## 6. 如果连接失败，优先排查这几项
- URL 是否填对
- 是否真的连的是 /mcp，而不是别的页面
- content-type 是否正确
- 服务端报错是不是被框架/网关改成了 text/plain
- 是否误用了旧 SSE 的接法

---

## 7. 能用以后再做清理
当新入口已经稳定可用后，再考虑：

可选清理项：
- 删除旧 SSE 代码
- 删除老配置
- 保留一个最小可用的 Streamable HTTP 版本
- 顺手补一点日志，方便以后排错

注意：
- 如果旧 SSE 代码留着也不碍事，其实可以先不删
- 单人自用时，“能稳定用”比“代码绝对干净”更重要

---

## 8. 推荐的最小执行顺序
第 1 步：
- 不动旧 SSE，先备份当前可用版本

第 2 步：
- 提取公共 tool / 数据库逻辑

第 3 步：
- 新增 /mcp 的 Streamable HTTP 入口

第 4 步：
- 本地用 Codex 直接连 /mcp 测试

第 5 步：
- 测通后再考虑删旧 SSE

---

## 9. 一句话版本
- 先保留 SSE
- 再补一个原生 Streamable HTTP 入口
- 复用原来的数据库 tool
- 只要 Codex 能连上并成功调用，就算迁移完成