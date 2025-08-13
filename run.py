# run.py
import os
import uvicorn
import asyncio

# Define a política de loop de eventos antes de qualquer coisa
# Isso resolve o NotImplementedError no Windows
if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)