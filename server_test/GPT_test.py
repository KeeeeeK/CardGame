import asyncio
import aioconsole

async def player_action(player_name):
    while True:
        action = await aioconsole.ainput(f"{player_name}, введите ваше действие: ")
        print(f"{player_name} выбрал действие: {action}")

async def main():
    player1_task = asyncio.create_task(player_action("Игрок 1"))
    player2_task = asyncio.create_task(player_action("Игрок 2"))

    await asyncio.gather(player1_task, player2_task)

if __name__ == "__main__":
    asyncio.run(main())
