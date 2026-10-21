#!/usr/bin/env python3
"""강단용 노트 원고(.txt) → 구글 독스 update_doc 인자(JSON).

원고 한 줄 = 문단 하나. 줄 머리로 종류를 정한다.
  # 제목            설교 제목 (TITLE)
  ## A  대지 제목   대지 (HEADING_2)
  > 창18:8  구절    성경 구절 — 기울임 + 빨강, 들여쓰기, 본문보다 1pt 작게
  >> 인용·기도문    들여쓰기만
  ** 핵심 문장      굵게 (대지마다 하나)
  그 밖             본문
빈 줄은 무시한다(간격은 문단 서식이 만든다).

사용:
  python3 stage_notes.py 원고.txt --doc 읽은문서.json --tab t.xxxx > req.json
읽은문서.json 은 read_doc 결과를 저장한 파일. 탭 본문을 통째로 지우고 원고로 채운다.
"""
import argparse, json, sys

SIZE = {"title": 21, "head": 19, "body": 17, "verse": 16}  # 오너 확정 2026-10-21
MARGIN, LINE_SPACING = 18, 130
RED = {"color": {"rgbColor": {"red": 0.8, "green": 0, "blue": 0}}}  # 오너 원고의 말씀 색


def parse(path):
    out = []
    for raw in open(path, encoding="utf-8"):
        s = raw.rstrip("\n").strip()
        if not s:
            continue
        for mark, kind in (("## ", "H"), ("# ", "T"), (">> ", "Q"), ("> ", "S"), ("** ", "K")):
            if s.startswith(mark):
                out.append((kind, s[len(mark):].strip()))
                break
        else:
            out.append(("N", s))
    return out


def u16(s):
    return len(s.encode("utf-16-le")) // 2


def build(lines, doc, tab):
    t = next(x for x in doc["tabs"] if x["tabProperties"]["tabId"] == tab)
    end = t["documentTab"]["body"]["content"][-1]["endIndex"]
    pt = lambda m: {"magnitude": m, "unit": "PT"}
    R = lambda a, b: {"startIndex": a, "endIndex": b, "tabId": tab}

    text, spans = "", []
    for kind, s in lines:
        a = 1 + u16(text)
        text += s + "\n"
        spans.append((kind, a, 1 + u16(text)))
    E = 1 + u16(text)

    req = []
    if end - 1 > 1:
        req.append({"deleteContentRange": {"range": R(1, end - 1)}})
    req += [
        {"insertText": {"text": text, "location": {"index": 1, "tabId": tab}}},
        {"deleteParagraphBullets": {"range": R(1, E)}},
        {"updateParagraphStyle": {"range": R(1, E), "paragraphStyle": {
            "namedStyleType": "NORMAL_TEXT", "lineSpacing": LINE_SPACING, "spaceAbove": pt(0),
            "spaceBelow": pt(4), "indentStart": pt(0), "indentFirstLine": pt(0)},
            "fields": "namedStyleType,lineSpacing,spaceAbove,spaceBelow,indentStart,indentFirstLine,shading"}},
        {"updateTextStyle": {"range": R(1, E - 1), "textStyle": {"fontSize": pt(SIZE["body"])},
                             "fields": "bold,italic,foregroundColor,fontSize"}},
        {"updateDocumentStyle": {"tabId": tab, "documentStyle": {
            k: pt(MARGIN) for k in ("marginTop", "marginBottom", "marginLeft", "marginRight")},
            "fields": "marginTop,marginBottom,marginLeft,marginRight"}},
    ]
    for kind, a, b in spans:
        if kind == "T":
            req += [{"updateParagraphStyle": {"range": R(a, b), "paragraphStyle": {"namedStyleType": "TITLE", "spaceBelow": pt(12)},
                                              "fields": "namedStyleType,spaceBelow"}},
                    {"updateTextStyle": {"range": R(a, b - 1), "textStyle": {"fontSize": pt(SIZE["title"]), "bold": True},
                                         "fields": "fontSize,bold"}}]
        elif kind == "H":
            req += [{"updateParagraphStyle": {"range": R(a, b), "paragraphStyle": {"namedStyleType": "HEADING_2", "spaceAbove": pt(28), "spaceBelow": pt(8)},
                                              "fields": "namedStyleType,spaceAbove,spaceBelow"}},
                    {"updateTextStyle": {"range": R(a, b - 1), "textStyle": {"fontSize": pt(SIZE["head"]), "bold": True},
                                         "fields": "fontSize,bold"}}]
        elif kind == "K":
            req += [{"updateTextStyle": {"range": R(a, b - 1), "textStyle": {"bold": True}, "fields": "bold"}},
                    {"updateParagraphStyle": {"range": R(a, b), "paragraphStyle": {"spaceAbove": pt(8), "spaceBelow": pt(8)},
                                              "fields": "spaceAbove,spaceBelow"}}]
        elif kind in ("S", "Q"):
            req.append({"updateParagraphStyle": {"range": R(a, b), "paragraphStyle": {
                "indentStart": pt(24), "indentFirstLine": pt(24), "spaceAbove": pt(4), "spaceBelow": pt(8)},
                "fields": "indentStart,indentFirstLine,spaceAbove,spaceBelow"}})
            if kind == "S":
                req.append({"updateTextStyle": {"range": R(a, b - 1), "textStyle": {
                    "italic": True, "fontSize": pt(SIZE["verse"]), "foregroundColor": RED},
                    "fields": "italic,fontSize,foregroundColor"}})
    return {"requests": req, "writeControl": {"requiredRevisionId": doc["revisionId"]}}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("script")
    ap.add_argument("--doc", required=True, help="read_doc 결과 JSON 파일")
    ap.add_argument("--tab", required=True, help="채울 탭 ID (addDocumentTab 응답의 tabId)")
    a = ap.parse_args()
    doc = json.load(open(a.doc, encoding="utf-8"))
    doc = doc.get("content", doc)  # 커넥터 저장본은 content 로 한 번 감싸져 있다
    lines = parse(a.script)
    if not lines:
        sys.exit("원고가 비어 있습니다")
    json.dump(build(lines, doc, a.tab), sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    main()
