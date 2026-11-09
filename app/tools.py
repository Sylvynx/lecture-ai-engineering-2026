"""第3回: エージェントに持たせるツール。

ここに書いた関数の docstring と型ヒントが、そのままモデルへの「ツールの説明文」になる。
説明文を書き換えると、モデルがツールを使うかどうか・どんな引数で呼ぶかが変わる。
"""

import json
import random
from functools import cache
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
MAX_RESULTS = 3


@cache
def load_glossary() -> list[dict]:
    with open(DATA_DIR / "glossary.json", encoding="utf-8") as f:
        return json.load(f)["terms"]


def _normalize(text: str) -> str:
    return text.casefold().replace(" ", "").replace("　", "")


def _names(entry: dict) -> list[str]:
    return [_normalize(entry["term"]), _normalize(entry["id"])] + [
        _normalize(a) for a in entry["aliases"]
    ]


def search_glossary(query: str) -> str:
    """講座の用語集から用語を検索し、定義と、どの回で扱うかを返す。

    AIエンジニアリングの用語や、この講座（AIE2026）に固有の言葉について
    答える前に使うこと。query には調べたい用語を1つだけ入れる（例: "LoRA"）。
    """
    q = _normalize(query)
    if not q:
        return "検索語が空です。調べたい用語を1つ指定してください。"
    glossary = load_glossary()

    exact = [e for e in glossary if q in _names(e)]
    # 「r」のような短い別名が何にでも当たらないよう、名前側が短いものは除く
    partial = [
        e for e in glossary
        if e not in exact and any(q in n or (len(n) >= 3 and n in q) for n in _names(e))
    ]
    in_definition = [
        e for e in glossary
        if e not in exact and e not in partial and q in _normalize(e["definition"])
    ]
    hits = (exact + partial + in_definition)[:MAX_RESULTS]

    if not hits:
        return f"用語集に「{query}」は見つかりませんでした。"
    return json.dumps(
        [
            {
                "term": e["term"],
                "lecture": e["lecture"],
                "definition": e["definition"],
                "related": e["related"],
            }
            for e in hits
        ],
        ensure_ascii=False,
    )


def get_lecture_summary(lecture: int) -> str:
    """指定した回（1始まりの整数）の講義の要点を返す。

    「第3回では何を学ぶ？」のように、回の内容や関係を聞かれたときに使う。
    """
    path = DATA_DIR / "lectures" / f"{lecture:02d}.md"
    if not path.exists():
        available = sorted(p.stem for p in (DATA_DIR / "lectures").glob("*.md"))
        return f"第{lecture}回の要点はまだありません。用意されている回: {', '.join(available)}"
    return path.read_text(encoding="utf-8")



def make_quiz(lecture: int) -> str:
    """指定した回の用語から1つを選び、確認問題と答えを返す。

    「第2回の確認問題を出して」のように、
    特定の講義回について復習問題を求められたときに使う。
    lectureには講義回の番号を整数で指定する。
    """
    # 1. 用語集から指定した講義回の用語を抽出
    glossary = load_glossary()
    terms = [
        entry for entry in glossary
        if entry["lecture"] == lecture
    ]

    # 2. 該当する用語が存在しない場合
    if not terms:
        return f"第{lecture}回の用語は見つかりませんでした。"

    # 3. 用語をランダムに1つ選択
    selected = random.choice(terms)

    # 4. 問題文と答えを作成
    quiz = {
        "question": f"「{selected['term']}」の意味は？",
        "answer": selected["definition"],
    }

    # 5. JSON形式の文字列として返す
    return json.dumps(quiz, ensure_ascii=False)



def save_learning_log(topic: str, content: str) -> str:
    """学習した内容を learning_log/ フォルダに保存する。

    「学習した内容を記録して」など、利用者が学習記録の保存を
    求めたときに使用する。
    ファイルへの書き込みを伴うため、実行前に利用者の承認が必要。
    topic は学習テーマ、content は記録する内容。
    """
    # 1. 入力が空でないか確認する
    if not topic.strip() or not content.strip():
        return "学習テーマと記録内容を指定してください。"

    # 2. 保存先のフォルダを指定する
    log_dir = Path(__file__).resolve().parent.parent / "learning_log"

    # 3. フォルダが存在しなければ作成する
    log_dir.mkdir(parents=True, exist_ok=True)

    # 4. 保存先ファイルを指定する
    log_path = log_dir / "learning_log.md"

    # 5. 学習記録を追記する
    with log_path.open("a", encoding="utf-8") as f:
        f.write(f"## {topic.strip()}\n\n")
        f.write(f"{content.strip()}\n\n")

    # 6. 保存結果を返す
    return "学習記録を learning_log/learning_log.md に保存しました。"
