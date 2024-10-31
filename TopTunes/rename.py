import os

# Define the root directory of your project
project_root = 'C:/Users/Alex Shapiro/OneDrive/Desktop/VSCODE PROJECTS/TopTunes'  # Replace with the path to your project

# Define the word to be replaced and the replacement word
old_word = 'TopTunes'
new_word = 'TopTunes'

# Walk through the project directory
for root, dirs, files in os.walk(project_root):
    for file in files:
        if file.endswith(('.py', '.html', '.css', '.txt', '.md', '.env', '.json', '.yml', '.yaml')):
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Replace the old word with the new word
                updated_content = content.replace(old_word, new_word)
                
                # Write the updated content back to the file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                
                print(f"Updated {file_path}")
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

print("Replacement complete.")