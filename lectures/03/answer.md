# 第3回 解答

## 演習

- 第1回（素のLLM）とエージェントの回答の違い：
    第1回の素のLLMのときは、講義資料と関係の無い、一般論的な回答を返していたのに対し、今回は、「3レベル」について質問したところ、「基礎・実装・発展」の3つを第一回の講義資料を示しながら正しく説明していた。

- `--trace` で見えたツール呼び出し（ツール名と引数）：
  「LoRAとQLoRAの違いは？」という質問では、`search_glossary({'query': 'LoRA'})` と `search_glossary({'query': 'QLoRA'})` がそれぞれ呼び出された。また、「第2回の内容から確認問題を1問出して」という質問では、追加した `make_quiz({'lecture': 2})` が呼び出された。

- 1つの質問での LLM 呼び出し回数（`requests`）：
    LoRAとQLoRAの比較では `requests=2`、`tool_calls=2` だった。確認問題の生成では `requests=2`、`tool_calls=1` だった。
- 追加したツールと、docstring に書いた説明：
  `make_quiz(lecture: int) -> str` を追加した。
    以下の説明を記載した。

    指定した回の用語から1つを選び、確認問題と答えを返す。
    「第2回の確認問題を出して」のように、
    特定の講義回について復習問題を求められたときに使う。
    lectureには講義回の番号を整数で指定する。


## 宿題

- 取り組んだレベル：実装
- やったこと：
    app/tools.py に、学習内容を learning_log/learning_log.md に追記する save_learning_log を実装した。また、app/agent.py で requires_approval=True を指定してツールを登録し、output_type に DeferredToolRequests を追加した。CLIでは、承認待ちの要求を受け取った際に利用者へ確認し、承認結果を DeferredToolResults として渡してエージェントの処理を再開するようにした。

- 結果：
    --trace を使った実行で、save_learning_log({'topic': 'Pydantic AIの承認機能', 'content': 'requires_approval=Trueにより、ファイル保存前に利用者の承認を求められることを学んだ'}) が呼び出されたことを確認した。保存を拒否（n）した場合はファイルが作成されず、承認（y）した場合は指定した内容がMarkdownファイルに保存された。
    また、uv run pytest -q を実行し、15件すべてのテストが成功した。

- 気づき・疑問：
    ツールを登録の際に、実行前に人間の承認を挟むように設定することで、LLMによる意図しないファイル操作を防げることを確認した。
    また、保存処理は成功していても、最終回答で関連回が誤って示される場合があり、ツール実行の成功とLLMの回答の正確性は別に確認する必要があると考えた。