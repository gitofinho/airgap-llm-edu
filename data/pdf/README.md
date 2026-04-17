# PDF 샘플

이 디렉터리는 캡스톤 및 실습용 **공개 PDF 문서**를 저장합니다. 저작권 문제로 바이너리는 포함하지 않으니, 수강생이 직접 내려받아 배치합니다.

## 권장 샘플

| 파일명 | 출처 | 다운로드 |
|--------|------|---------|
| `전자금융거래_표준약관.pdf` | 공정거래위원회 표준약관 | [공정위 표준약관 검색](https://www.ftc.go.kr/www/cop/bbs/selectBoardList.do?bbsId=BBSMSTR_000000002303) |
| `금융분야_AI_활용_안내서.pdf` | 금융감독원 | [금감원 공시](https://www.fss.or.kr/fss/main/main.do) |
| `개인정보_비식별_가이드라인.pdf` | 개인정보보호위원회 | [PIPC 자료실](https://www.pipc.go.kr/) |

## 대체 옵션

위 PDF를 구하기 어렵다면, `data/corpus_ko.txt`에 포함된 텍스트를 수동으로 PDF로 변환해 사용해도 실습 목적에는 충분합니다.

```python
# (선택) 텍스트 → PDF 변환 예
from reportlab.pdfgen import canvas
c = canvas.Canvas("data/pdf/corpus_ko.pdf")
for i, line in enumerate(open("data/corpus_ko.txt", encoding="utf-8")):
    c.drawString(50, 800 - i*20, line.strip())
c.save()
```
