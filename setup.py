from cx_Freeze import setup, Executable

executables = [
    Executable("main.py", target_name="frlg_switch_seed_farmer"),
    Executable("process_seeds.py", target_name="frlg_switch_seed_processor"),
]

setup(
    name="FRLG Switch Seed Farmer",
    version="1.0",
    description="",
    executables=executables,
    options={"build_exe": {"build_exe": "dist", "include_files": ["config.json"]}},
)
