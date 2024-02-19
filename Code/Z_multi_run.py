import subprocess

# List of your scripts to run
Clear_DB = ["ia_Clear_Collection.py", "ib_Clear_SQLdb.py"]
### Takes the code to where data is setting in the temp area in mongo ready to be processed
Current_Workflow  = ["ia_Clear_Collection.py", "ib_Clear_SQLdb.py","ic_generate_database.py",
                         "id_generate_topics.py","ie_request_data.py","ig_generate_story_records.py",
                         "ih_request_stories.py"]

for script in Current_Workflow:
    # Run each script
    print(f"Running {script}...")
    subprocess.run(["python", script])

print("All scripts executed.")