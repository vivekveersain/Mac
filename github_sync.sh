#!/bin/bash

cp ${HOME}/.zshrc ${HOME}/Github/Mac/zshrc
# Define the parent directory containing all your repositories
PARENT_DIR="${HOME}/Github/"

# Change to the parent directory
cd "$PARENT_DIR" || { echo "Directory not found: $PARENT_DIR"; exit 1; }

# Function to commit and pull changes
sync_repo() {
    cd "$1" || return

    # Check for uncommitted changes
    if [[ -n $(git status --porcelain) ]]; then
        echo "Uncommitted changes found in $(basename "$1"). Committing..."
        git add .
        git commit -m "Automated commit: $(date +'%Y-%m-%d %H:%M:%S')"
    else
        echo "No uncommitted changes in $(basename "$1")."
    fi

    # Pull the latest changes from the remote repository
    echo "Pulling changes for $(basename "$1")..."
    git pull origin main  # Change 'main' to your default branch if different
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

echo "Sync complete!"

