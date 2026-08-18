# 📚 知识库端到端闭环（KB End-to-End）

> **中文**：帮你把知识库从「建起来」管到「用起来」再「迭代优化」的完整闭环技能。
>
> **English**: A complete knowledge base lifecycle skill for AI agents — build, classify, tag, retrieve & archive with quality gates.

## ✨ 功能概览 / Features

覆盖知识库全生命周期六大阶段，每阶段带质量门禁。
Covers the full knowledge base lifecycle in six stages, each with quality gates:

| 阶段 Stage | 产出 Output | 质量门禁 Quality Gate |
|------|------|----------|
| ① 构建 Build | 文件夹架构 + 笔记清单 + MOC + 模板 + 示例 / Folder architecture + note inventory + MOC + templates + examples | MOC 双链 100% 在清单有落点（零死链）/ 100% of MOC links resolve (zero broken links) |
| ② 识别 Classify | 每篇笔记的 type + 出处 + 置信度 + 处置 / Type + source + confidence + disposition per note | type 全部取自 7 类枚举，无自造 / All types from 7-class enum, none invented |
| ③ 入库校验 Validate | 结构 / 去重 / 质量 / 密级 四项检查 / Structure, dedup, quality, security checks | 密级超标或来源未授权 → 一票否决 / Over-classified or unauthorized → veto |
| ④ 打标入库 Tag | 每篇完整 frontmatter / Complete frontmatter per note | 基础层 + 治理层字段完整，无空值 / Full base + governance fields, no empty values |
| ⑤ 调用路径 Retrieve | 检索式方案 + 工作流触发表 / Retrieval plan + workflow trigger table | 每个业务场景有对应知识挂载 / Every business scenario has knowledge attached |
| ⑥ 复盘归档 Archive | 复审计划 + 过期策略 + 归档流程 / Review plan + expiry policy + archive flow | 每篇笔记有 valid_until 或标记「长期」/ Every note has valid_until or "long-term" |

**通用适配 / Universally adaptable**: 个人学习库 / 业务知识库 / 项目库 / 研究库，任意领域皆可。
Personal / business / project / research knowledge bases, any domain.

## 🚀 快速开始 / Quick Start

如果你只需要一个简单知识库，不追求企业级治理：
For a simple knowledge base without enterprise-grade governance:

1. 文件夹架构 + 笔记清单（零死链）/ Folder architecture + note inventory (zero broken links)
2. 基础 frontmatter（type + category + tags + status）/ Basic frontmatter
3. MOC 总索引 / MOC master index

完整企业级治理流程见 `SKILL.md`。See `SKILL.md` for the full enterprise workflow.

## 📁 仓库结构 / Repository Structure

```
kb-end-to-end/
├── SKILL.md                      # 技能主文件（含完整执行逻辑与输出模板）/ Main skill file
├── README.md                     # 说明文档 / Documentation
├── LICENSE                       # MIT 开源协议 / MIT License
└── references/
    ├── type-taxonomy.md          # 知识类型词表(7类) + 企业受控标签词表 + 有效期策略 / Type taxonomy (7 classes) + controlled vocabulary + expiry policy
    └── example-pipeline.md       # 端到端全链路 Few-shot 样例 / End-to-end few-shot example
```

## 🔑 触发场景 / Trigger Scenarios

下列关键词任意命中即启用。Triggers on any of the following keywords:

- **建库类 Build**: obsidian知识库 / 创建obsidian库 / obsidian模板 / obsidian双链 / obsidian frontmatter / 生成obsidian笔记 / obsidian目录规划
- **治理类 Governance**: 知识库闭环 / 知识识别 / 入库标准 / 打标入库 / 知识治理 / 知识调用复用 / 企业知识库管理
- **生命周期类 Lifecycle**: 知识库复盘 / 知识归档 / 知识复审 / 知识过期

## 🛡️ 安全说明 / Security

- 纯文本方案输出，**不写库、不调 API、不读写本地文件**，无数据风险
  Pure text output — no database writes, no API calls, no local file access. Zero data risk.
- 密级 / 合规等判定需人工最终复核，AI 结果仅供辅助决策
  Security classification & compliance decisions require human review; AI output is advisory only.

## 📄 许可证 / License

本项目采用 [MIT License](LICENSE) 开源。Released under the [MIT License](LICENSE).
