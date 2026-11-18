# -*- coding: utf-8 -*-
"""品牌落款补丁：把"由 RustDesk 提供支持"改为唐意文化落款，并去掉点击跳转官网。"""
import io, sys

def edit(path, old, new, label, required=True):
    try:
        s = io.open(path, encoding="utf-8").read()
    except FileNotFoundError:
        print("[footnote] SKIP (missing): " + path, flush=True)
        return not required
    if old not in s:
        print("[footnote] WARN: pattern not found in " + path + " (" + label + ")", flush=True)
        return not required
    s = s.replace(old, new, 1)
    io.open(path, "w", encoding="utf-8").write(s)
    print("[footnote] patched: " + label, flush=True)
    return True

# 1) 中文文案
edit("src/lang/cn.rs",
     '("powered_by_me", "由 RustDesk 提供支持"),',
     '("powered_by_me", "由唐意文化提供技术支持"),',
     "cn.rs footnote text")

# 2) 英文文案（兜底：界面切成英文时也显示唐意）
edit("src/lang/en.rs",
     '("powered_by_me", "Powered by RustDesk"),',
     '("powered_by_me", "Technical support by Tangyi Culture"),',
     "en.rs footnote text")

# 3) 去掉点击跳转官网：把 GestureDetector 的 onTap 置空，保留文字样式。
#    直接替换 onTap 块内容，避免动整体结构。
p = "flutter/lib/common.dart"
try:
    s = io.open(p, encoding="utf-8").read()
    old = """    child: GestureDetector(
      onTap: () {
        launchUrl(Uri.parse('https://rustdesk.com'));
      },"""
    new = """    child: GestureDetector(
      onTap: () {},"""
    if old in s:
        s = s.replace(old, new, 1)
        io.open(p, "w", encoding="utf-8").write(s)
        print("[footnote] patched: removed rustdesk.com tap", flush=True)
    else:
        print("[footnote] WARN: tap pattern not found, leave as-is", flush=True)
except FileNotFoundError:
    print("[footnote] SKIP (missing): " + p, flush=True)

print("[footnote] DONE", flush=True)
