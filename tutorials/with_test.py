import asyncio


async def get_number():
    print("get_number is running")
    return 42


async def main():
    # result = get_number()
    result = await get_number()

    print(result)


asyncio.run(main())