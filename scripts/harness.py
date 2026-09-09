#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kb-end-to-end harness 验证器（输出质量闸门）

用途：对技能产出的知识库方案 Markdown 做自动校验，全绿才允许交付。
版本：v1.5（2026-09-06）新增 H7 知识网络方案完整性、H8 保护与清理授权声明。
本项目范式来源：飞书个人知识库治理项目「脚本验收」机制（2026-09 实战验证）。

用法：
  python3 harness.py 方案.md
  python3 harness.py 方案.md --script setup_kb.sh   # 额外校验落地脚本一致性
  cat 方案.md | python3 harness.py -                # 从 stdin 读

退出码：0 = 全部通过；1 = 存在 FAIL；2 = 输入错误
"""
import argparse
import os
import re
import sys

TYPE_ENUM = {"concept", "method", "template", "solution", "data", "case", "note"}
SEC_ENUM = {"公开", "内部", "秘密", "机密", "public", "internal", "confidential"}
REQUIRED_FM_FIELDS = ["type", "category", "status"]
MD_LINK_RE = re.compile(r"\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]")
FM_BLOCK_RE = re.compile(r"(?ms)^---\s*\n(.*?)\n---\s*\n")
TABLE_ROW_RE = re.compile(r"^\|.*\|$", re.M)
CAT_EOF_RE = re.compile(r"cat <<\s*'EOF'\s*>\s*(\S+)")


def read_input(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def extract_note_names(text: str) -> set:
    """从清单表格与目录树代码块中提取 .md 笔记名（不带路径前缀的尾段 + 全路径）。"""
    names = set()
    for m in re.finditer(r"([\w\-\u4e00-\u9fff/]*[\w\-\u4e00-\u9fff]+\.md)", text):
        full = m.group(1).strip()
        names.add(full)
        names.add(full.rsplit("/", 1)[-1])
    return {n for n in names if n.endswith(".md")}


def strip_code_blocks(text: str) -> str:
    return re.sub(r"(?s)```.*?```", "", text)


def parse_frontmatter_blocks(text: str):
    """返回 [(起始行号, 字典)]。"""
    blocks = []
    for m in FM_BLOCK_RE.finditer(text):
        line_no = text[: m.start()].count("\n") + 1
        fm = {}
        for line in m.group(1).splitlines():
            if ":" in line:
                k, _, v = line.partition(":")
                fm[k.strip()] = v.strip()
        blocks.append((line_no, fm))
    return blocks


def check(markdown_text: str, script_text: str = None):
    results = []

    def rec(hid, name, ok, detail=""):
        results.append((hid, name, bool(ok), detail))

    raw = markdown_text
    body = strip_code_blocks(raw)

    # H1 MOC 双链零死链（只扫正文，排除代码块中的示例）
    links = [l.strip() for l in MD_LINK_RE.findall(body)]
    notes = extract_note_names(raw)
    note_stems = {n[:-3] for n in notes}
    dead = [l for l in links if l not in note_stems and l not in notes]
    # 双链目标也允许匹配路径尾段
    if dead:
        dead = [l for l in dead if l.rsplit("/", 1)[-1] not in note_stems and l.rsplit("/", 1)[-1] not in notes]
    rec("H1", "MOC 双链零死链", not dead, f"双链 {len(links)} 条，死链 {len(dead)}: {dead[:5] if dead else '无'}")

    # H2/H3/H5 frontmatter 校验
    fms = parse_frontmatter_blocks(raw)
    if not fms:
        rec("H2", "type 枚举合规", False, "未找到任何 frontmatter 块")
        rec("H3", "frontmatter 必填字段", False, "未找到任何 frontmatter 块")
        rec("H5", "生命周期 valid_until/长期", False, "未找到任何 frontmatter 块")
    else:
        bad_types, missing_fields, missing_life = [], [], []
        for line_no, fm in fms:
            t = fm.get("type", "").strip().strip('"\'')
            if t and t not in TYPE_ENUM:
                bad_types.append((line_no, t))
            absent = [k for k in REQUIRED_FM_FIELDS if not fm.get(k, "").strip()]
            if absent:
                missing_fields.append((line_no, absent))
            vu = fm.get("valid_until", "").strip()
            if not vu and "长期" not in fm.get("status", "") and "长期" not in fm.get("category", ""):
                missing_life.append(line_no)
        rec("H2", "type 枚举合规", not bad_types,
            f"检查 {len(fms)} 个 frontmatter；违规: {bad_types[:3] if bad_types else '无'}（合法枚举: {sorted(TYPE_ENUM)}）")
        rec("H3", "frontmatter 必填字段", not missing_fields,
            f"缺失: {missing_fields[:3] if missing_fields else '无'}（必填: {REQUIRED_FM_FIELDS}）")
        rec("H5", "生命周期 valid_until/长期", not missing_life,
            f"缺失行: {missing_life[:3] if missing_life else '无'}")

    # H4 密级闸门（出现 security_level 时校验枚举）
    bad_sec = []
    for line_no, fm in fms:
        s = fm.get("security_level", "").strip()
        if s and s not in SEC_ENUM:
            bad_sec.append((line_no, s))
    rec("H4", "密级闸门", not bad_sec,
        f"违规: {bad_sec[:3] if bad_sec else '无'}（合法: 公开/内部/秘密/机密；未标注视为不校验）")

    # H6 落地脚本一致性（可选）
    if script_text:
        script_files = set()
        for m in CAT_EOF_RE.finditer(script_text):
            p = m.group(1).strip()
            script_files.add(p)
            script_files.add(p.rsplit("/", 1)[-1])
        plan_files = {n for n in notes if n.endswith(".md")}
        plan_stems = {n[:-3] for n in plan_files}
        extra = [p for p in script_files
                 if p not in plan_files and p not in plan_stems
                 and p.rsplit("/", 1)[-1] not in plan_stems
                 and p.endswith(".md")]
        rec("H6", "落地脚本与方案清单一致", not extra,
            f"脚本多创建: {extra[:5] if extra else '无'}；脚本文件数 {len(script_files)}，清单 .md 数 {len(plan_files)}")
    else:
        rec("H6", "落地脚本与方案清单一致", True, "未提供 --script，跳过（仅当落地模式=生成脚本时必跑）")

    # H7 知识网络方案完整性（方案声明知识网络/混合检索能力时必检）
    NETWORK_TRIGGERS = ["知识网络", "混合检索", "向量检索", "相似聚类", "清重", "指纹引擎"]
    NETWORK_KEYS = ["指纹", "阈值", "BM25", "向量", "答案溯源", "保护", "清理授权"]
    if any(k in raw for k in NETWORK_TRIGGERS):
        missing_net = [k for k in NETWORK_KEYS if k not in raw]
        rec("H7", "知识网络方案完整性", not missing_net,
            f"方案声明知识网络能力；缺失关键要素: {missing_net if missing_net else '无'}（要求: 指纹/阈值/BM25/向量/答案溯源/保护/清理授权）")
    else:
        rec("H7", "知识网络方案完整性", True, "未声明知识网络能力，跳过")

    # H8 保护与清理授权声明（方案涉及删除/清理/自动运营时必检）
    OPS_TRIGGERS = ["删除", "清理", "归档", "自动运营", "清重", "回收区"]
    OPS_SAFETY = ["请示", "授权", "保护", "备份", "引用检查"]
    if any(k in raw for k in OPS_TRIGGERS):
        missing_safety = [k for k in OPS_SAFETY if k not in raw]
        rec("H8", "保护与清理授权声明", not missing_safety,
            f"方案涉及删除/清理；缺失安全要素: {missing_safety if missing_safety else '无'}（要求: 请示/授权/保护/备份/引用检查）")
    else:
        rec("H8", "保护与清理授权声明", True, "方案不涉及删除/清理，跳过")

    return results


def main():
    ap = argparse.ArgumentParser(description="kb-end-to-end harness 验证器")
    ap.add_argument("input", help="方案 Markdown 文件路径，或 - 读 stdin")
    ap.add_argument("--script", help="落地脚本路径（可选，启用 H6 一致性校验）")
    args = ap.parse_args()

    try:
        text = read_input(args.input)
    except Exception as e:
        print(f"[INPUT-ERROR] {e}")
        sys.exit(2)

    script_text = None
    if args.script:
        try:
            with open(args.script, "r", encoding="utf-8") as f:
                script_text = f.read()
        except Exception as e:
            print(f"[INPUT-ERROR] script: {e}")
            sys.exit(2)

    results = check(text, script_text)
    total_fail = 0
    print("=" * 62)
    print("kb-end-to-end harness 验证报告")
    print("=" * 62)
    for hid, name, ok, detail in results:
        mark = "PASS" if ok else "FAIL"
        total_fail += 0 if ok else 1
        print(f"[{mark}] {hid} {name} — {detail}")
    print("-" * 62)
    if total_fail == 0:
        print(f"结论：✅ 全部通过（{len(results)} 项）— 方案可交付")
        sys.exit(0)
    else:
        print(f"结论：❌ {total_fail} 项未通过 — 请修正后重跑，全绿才可交付")
        sys.exit(1)


if __name__ == "__main__":
    main()
