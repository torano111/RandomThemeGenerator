from AsyncThemeGenerator import AsyncThemeGenerator
import asyncio

async def exec_test():
    tgen = AsyncThemeGenerator()
    await tgen.generate()

    # 生成されたお題を全て出力（デバッグ用）
    print("全てのお題:")
    for thm in tgen.get_all_themes():
        print(thm)

    # ランダムで1つ選択して出力
    print("\n選ばれたお題:")
    print(tgen.get_random())

if __name__ == "__main__":
    asyncio.run(exec_test())