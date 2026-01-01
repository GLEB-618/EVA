import asyncio


async def run_detached_windows(exe_path: str, *args: str) -> int:
    DETACHED_PROCESS = 0x00000008
    CREATE_NEW_PROCESS_GROUP = 0x00000200

    proc = await asyncio.create_subprocess_exec(
        exe_path, *args,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
        creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
        close_fds=True,
    )
    return proc.pid

async def main():
    pid = await run_detached_windows(r"C:\\Tools\\myapp.exe", "--run")
    print("Detached pid =", pid)

asyncio.run(main())