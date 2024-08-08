import os
import asyncio
import random
from openai import AsyncOpenAI
import openai
import configparser
import json
from enum import Enum

class ThemeMode(Enum):
    Word = 1
    Phrase = 2

    #文字列化
    @property
    def str(self):
        return {
            ThemeMode.Phrase: "フレーズ",
            ThemeMode.Word: "単語"
        }[self]


class AsyncThemeGenerator:
    def __init__(self, config_path='config.ini'):
        # 設定ファイルの読み込み
        self.config = configparser.ConfigParser()
        self.config.read(config_path, encoding='utf-8')

        # 環境変数からAPIキーを取得
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.model = self.config['openai']['model']

        self.client = AsyncOpenAI(api_key=self.api_key)
        self.is_generated = False
        self.themeMode = ThemeMode.Word

    def set_theme_mode(self, themeMode):
        self.themeMode = themeMode

    def get_prompt(self):
        if self.themeMode == ThemeMode.Word:
            return self.config['openai']['prompt_word']
        elif self.themeMode == ThemeMode.Phrase:
            return self.config['openai']['prompt_phrase']
        else:
            return ""

    # ランダムなお題を生成する関数
    async def generate(self):
        self.is_generated = False
        
        try:
            self.response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": self.get_prompt()}
                ],
                response_format={"type": "json_object"}
            )
            self.themes = json.loads(self.response.choices[0].message.content)['prompts']
            
            # 重複を排除
            self.themes = list(set(self.themes))
            self.is_generated = True
        except openai.APIConnectionError as e:
            print("The server could not be reached")
            print(e.__cause__)  # an underlying Exception, likely raised within httpx.
        except openai.RateLimitError as e:  
            print("A 429 status code was received; we should back off a bit.")
        except openai.APIStatusError as e:
            print("Another non-200-range status code was received")
            print(e.status_code)
            print(e.response)

    def check_generate_status(self):
        return self.is_generated

    def get_all_themes(self):
        if self.is_generated:
            return self.themes
        else:
            return []

    def get_random(self, num):
        if num > len(self.themes):
            n = len(self.themes)
        else:
            n = num

        if self.is_generated and n >= 1:
            return random.sample(self.themes, n)
        else:
            return "None"