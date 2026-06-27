import os, pathlib
with open("main.py", "r") as f:
    code = f.read()

debug_route = """
@app.get("/dashboard")
async def serve_dashboard():
    import pathlib
    files = [str(p) for p in pathlib.Path(".").glob("**/*") if "__pycache__" not in str(p) and ".git" not in str(p)]
    return {"current_working_directory": os.getcwd(), "files_found_in_container": files}
"""

# Cut the old function out and inject the file scanner
if 'def serve_dashboard():' in code:
    main_part = code.split('@app.get("/dashboard"')
    fixed_code = main_part + debug_route
    with open("main.py", "w") as f:
        f.write(fixed_code)
    print("Diagnostic patch applied locally.")
