# sermon-stage-notes — 강단용 설교 노트 스킬

하올람센터처치 내부용. 구글 독스에 있는 설교문을 강단에서 보면서 할 노트로 줄여 **같은 문서에 새 탭**으로 넣는 Claude Code 스킬이다.

- 중요 문구와 성경 말씀만 남기고, 기호 없이 줄바꿈·굵기·들여쓰기로만 구조를 잡는다.
- 말씀 구절은 원고처럼 기울임 + 빨강으로 구분한다.
- 대지 앞에 A B C D를 붙인다.

절차는 [`SKILL.md`](SKILL.md), 노트 원고 예시는 [`example.txt`](example.txt).

## 준비물

- Claude 에 Google Drive · Google Docs 커넥터 연결
- Python 3 (표준 라이브러리만 씀)

## 쓰는 법

Claude Code 에서 설교문을 붙여넣고 "강단용 노트 만들어줘" 라고 하면 된다. 수동으로는:

```bash
python3 stage_notes.py 노트.txt --doc read_doc결과.json --tab t.xxxx > req.json
```

`req.json` 을 Google Docs 커넥터의 `update_doc` 에 그대로 넘긴다.
