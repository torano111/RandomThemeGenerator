import tkinter as tk
from tkinter import ttk
from AsyncThemeGenerator import AsyncThemeGenerator  # AsyncThemeGeneratorをインポート
import asyncio

class ThemeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("お題を作成")

        # AsyncThemeGeneratorクラスのインスタンスを作成
        self.generator = AsyncThemeGenerator()

        # 上部にタイトルラベルを配置
        self.title_label = ttk.Label(self.root, text="お題を作成", font=("Helvetica", 16))
        self.title_label.pack(pady=10)

        # 中央にお題を表示するテキストウィジェットを配置
        self.theme_text = tk.Text(self.root, font=("Helvetica", 12), wrap="word", height=5, width=50)
        self.theme_text.pack(pady=10)
        self.theme_text.config(state=tk.DISABLED)  # リードオンリーに設定

        # ボタンとスピンボックス、コンボボックスを配置するフレームを作成
        self.control_frame = ttk.Frame(self.root)
        self.control_frame.pack(pady=10, padx=40, fill=tk.X)

        # 数値選択用のスピンボックスを追加
        self.spinbox = tk.Spinbox(self.control_frame, from_=1, to=10, width=5)
        self.spinbox.pack(side=tk.LEFT, padx=(0, 10))

        # お題生成ボタンを配置
        self.generate_button = ttk.Button(self.control_frame, text="更新", command=self.generate_theme)
        self.generate_button.pack(side=tk.LEFT, padx=(0, 10))

        # ドロップダウン（コンボボックス）を追加
        self.combo_box = ttk.Combobox(self.control_frame, values=[pt for pt in self.generator.get_prompt_types()], state="readonly")
        self.combo_box.current(0)  # 初期選択を設定
        self.combo_box.pack(side=tk.LEFT, padx=(0, 10))

        # リセットボタンを配置
        self.reset_button = ttk.Button(self.control_frame, text="お題テーブルをリセット", command=self.reset_themes)
        self.reset_button.pack(side=tk.LEFT)
        
        # お題リストがないので、最初は無効に
        self.generate_button.config(state=tk.DISABLED)
        self.spinbox.config(state=tk.DISABLED)

    def set_interactables_state(self, new_state):
        self.generate_button.config(state=tk.NORMAL if new_state else tk.DISABLED)
        self.reset_button.config(state=tk.NORMAL if new_state else tk.DISABLED)
        self.combo_box.config(state="readonly" if new_state else "disabled")
        self.spinbox.config(state=tk.NORMAL if new_state else tk.DISABLED)

    def generate_theme(self):
        themes = self.generator.get_random(int(self.spinbox.get())) #スピンボックスに応じて取得するお題の数を設定
        self.theme_text.config(state=tk.NORMAL)  # テキストウィジェットを編集可能にする
        self.theme_text.delete(1.0, tk.END)  # 既存のテキストを削除
        self.theme_text.insert(tk.END, "、".join(themes))  # 新しいお題を挿入
        self.theme_text.config(state=tk.DISABLED)  # テキストウィジェットを再びリードオンリーにする

    def reset_themes(self):
        # 全てのボタンを無効化
        self.set_interactables_state(False)

        # ドロップダウンに応じてプロンプト変更
        selection = self.combo_box.get()
        self.generator.cur_prompt_idx = self.generator.get_prompt_index_from(selection)
        
        # 非同期タスクをイベントループで実行
        task = asyncio.create_task(self.async_reset_themes())
        task.add_done_callback(self.on_reset_complete)

    def on_reset_complete(self, task):
        # 全てのボタンを再度有効化
        self.set_interactables_state(True)
        self.generate_theme()

    async def async_reset_themes(self):
        # お題更新中のアニメーションを非同期で表示
        self.loading_task = asyncio.create_task(self.update_loading_text())
        
        # お題を非同期で生成
        await self.generator.generate()
        
        # ローディングタスクをキャンセル
        self.loading_task.cancel()
        try:
            await self.loading_task
        except asyncio.CancelledError:
            pass

        #全お題を出力。デバッグ用。
        print("\n".join(self.generator.get_all_themes()))
            

    async def update_loading_text(self):
        loading_texts = ["お題テーブル更新中.", "お題テーブル更新中..", "お題テーブル更新中..."]
        while not self.generator.check_generate_status():
            for text in loading_texts:
                self.theme_text.config(state=tk.NORMAL)  # テキストウィジェットを編集可能にする
                self.theme_text.delete(1.0, tk.END)  # 既存のテキストを削除
                self.theme_text.insert(tk.END, text)  # 新しいお題を挿入
                self.theme_text.config(state=tk.DISABLED)  # テキストウィジェットを再びリードオンリーにする
                await asyncio.sleep(1)

async def main():
    # Tkinterのルートウィンドウを作成
    root = tk.Tk()
    
    # ウィンドウサイズを設定
    root.geometry("500x300")
    
    # アプリケーションクラスのインスタンスを作成
    app = ThemeApp(root)
    
    # Tkinterのメインループを非同期で実行
    while True:
        try:
            root.update()
            await asyncio.sleep(0.01)
        except tk.TclError:
            break

if __name__ == "__main__":
    # 非同期イベントループを実行
    asyncio.run(main())
