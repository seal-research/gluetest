import os

# read all files in the "commons-cli" and "commons-csv" directories
# and loop over their paths
for project in ["commons-cli", "commons-csv"]:
    for root, dirs, files in os.walk(project):
        for file in files:
            # the file should be in "main" directory
            if not "/main/" in root:
                continue
            
            # the file should be a Java file
            if not file.endswith(".java"):
                continue

            # open the App.java file and replace "PUT_FILE_PATH_HERE" with the file path
            with open("graal-glue-generator/src/main/java/com/research/graalglue/App.java") as f:
                originalText = f.read()
                newText = originalText.replace("PUT_FILE_PATH_HERE", os.path.join(root, file))
            with open("graal-glue-generator/src/main/java/com/research/graalglue/App.java", "w") as f:
                f.write(newText)

            # call the automation script
            os.system("mvn -f graal-glue-generator/pom.xml install exec:java")
            
            # reset the App.java file
            with open("graal-glue-generator/src/main/java/com/research/graalglue/App.java", "w") as f:
                f.write(originalText)
