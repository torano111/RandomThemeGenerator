import os
import random
from openai import AsyncOpenAI
import openai
import configparser
import json

class AsyncThemeGenerator:
    def __init__(self, config_path='config.ini', prompt_json_path='prompt.json'):
        # 設定ファイルの読み込み
        self.config = configparser.ConfigParser()
        self.config.read(config_path, encoding='utf-8')

        # プロンプトJSONファイルの読み込み
        with open(prompt_json_path, 'r', encoding='utf-8') as prompt_json:
            data = json.load(prompt_json)
            self.prompt_prefix = data["prompt_prefix"]
            self.prompts = data["prompts"]  # 辞書データとしてself.promptsに格納
            self.prompt_suffix = data["prompt_suffix"]

            self.cur_prompt_idx = 0

            # 読み込んだpromptsを出力。デバッグ用。
            # for key, value in self.prompts.items():
            #     print(f"key: {key}, value: {value}")

        # 環境変数からAPIキーを取得
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.model = self.config['openai']['model']

        self.client = AsyncOpenAI(api_key=self.api_key)
        self.is_generated = False

    def get_prompt_types(self):
        return list(self.prompts.keys())
    
    def get_prompts_len(self):
        return len(self.get_prompt_types())
    
    def get_prompt_type_at(self, idx):
        return self.get_prompt_types()[idx]
    
    def get_prompt_index_from(self, prompt_type):
        list = self.get_prompt_types()
        if prompt_type in list: return list.index(prompt_type)
        else: return None
    
    def get_full_prompt_at(self, idx):
        return self.prompt_prefix + list(self.prompts.values())[idx] + self.prompt_suffix

    # ランダムなお題を生成する関数
    async def generate(self):
        self.is_generated = False
        
        try:
            self.response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": self.get_full_prompt_at(self.cur_prompt_idx)}
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