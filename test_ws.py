# test_ws_repl.py
import asyncio
import json
import websockets


async def send_loop(ws):
    loop = asyncio.get_running_loop()
    while True:
        # prompt for user message without blocking the event loop
        content = await loop.run_in_executor(None, input, "You: ")
        if content.lower().strip() == "exit":
            print("⮞ Closing connection…")
            await ws.close()
            break
        kb = await loop.run_in_executor(None, input, "KB (blank for none): ")
        payload = {"content": content, "knowledge_base": kb}
        await ws.send(json.dumps(payload))


async def recv_loop(ws):
    try:
        async for message in ws:
            print(f"⮞ Assistant chunk: {message}")
    except websockets.ConnectionClosedOK:
        print("⮞ Server closed connection")
    except Exception as e:
        print("⮞ Connection error:", e)


async def main():
    async with websockets.connect("ws://127.0.0.1:8000/api/v1/ws/sessions/24") as ws:
        send_task = asyncio.create_task(send_loop(ws))
        recv_task = asyncio.create_task(recv_loop(ws))

        done, pending = await asyncio.wait(
            [send_task, recv_task],
            return_when=asyncio.FIRST_COMPLETED,
        )
        for task in pending:
            task.cancel()


if __name__ == "__main__":
    asyncio.run(main())
