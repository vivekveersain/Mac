#!/bin/bash

cp ${HOME}/.zshrc ${HOME}/Github/Mac/zshrc
# Define the parent directory containing all your repositories
PARENT_DIR="${HOME}/Github/"

# Change to the parent directory
cd "$PARENT_DIR" || { echo "Directory not found: $PARENT_DIR"; exit 1; }

# Function to commit and pull changes
sync_repo() {
    cd "$1" || return
	git clean -fd

	# Pull the latest changes from the remote repository
    echo "\nPulling changes for $(basename "$1")..."
    git pull #origin main  # Change 'main' to your default branch if different

    # Check for uncommitted changes
    if [[ -n $(git status --porcelain) ]]; then
		git add .
		git reset -- .DS_Store .gitattributes
		git rm -r __pycache__ 2>/dev/null
        echo "Uncommitted changes found in $(basename "$1"). Committing..."
        git commit -m "Automated commit: $(date +'%Y-%m-%d %H:%M:%S')"
		git push
    else
        echo "No uncommitted changes in $(basename "$1")."
    fi

    cd ..
}

# Iterate over each directory in the parent directory
for dir in */; do
    if [ -d "$dir/.git" ]; then  # Check if it's a Git repository
        sync_repo "$dir"
    else
        echo "$dir is not a Git repository. Skipping..."
    fi
done

echo "\nSync complete!!"

