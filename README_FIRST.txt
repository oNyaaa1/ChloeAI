ChloeAI - first real AI upgrade
================================

WHAT CHANGED
- Replaces the dummy LLM response with a real local Ollama chat API connection.
- Adds a multi-turn conversation context while Chloe is running.
- Adds persistent user-controlled notes in chloe_memory.txt.
- Logs answered conversations to chloe_history.txt.
- Adds /help, /remember, /memory, /forget, and /quit commands.
- Handles network/model errors instead of hanging in the old brainCompute loop.

SETUP (Windows)
1. Install Ollama from https://ollama.com/
2. Open a terminal and run:
       ollama pull qwen2.5:7b
   This model needs several GB of RAM. If your PC is lower-powered, edit MODEL in
   Chloe.cpp to a smaller model you have pulled, such as qwen2.5:3b.
3. Make sure Ollama is running. Usually it serves its local API at 127.0.0.1:11434.
4. Open Chloe.sln in Visual Studio.
5. Build the x64 configuration with the Windows SDK installed.
6. Run Chloe. Type /help for commands.

NOTES
- This version uses the Windows WinHTTP API and links winhttp.lib; no libcurl is needed.
- If Visual Studio reports that Windows headers are missing, install the Desktop
  development with C++ workload and a Windows 10/11 SDK.
- Memory is explicit: use /remember to save facts/notes. /forget clears notes only after
  typing YES. Conversation logs are local plain text in the program's working directory.
- This is a practical assistant prototype, not artificial superintelligence. It does not
  autonomously browse the web, modify its own source, or execute arbitrary shell commands.
  Those capabilities should be added separately with permissions, sandboxing, and tests.
