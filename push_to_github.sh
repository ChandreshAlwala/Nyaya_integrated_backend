#!/bin/bash
# Git commands to push Nyaya backend to GitHub

# Initialize git if not already done
git init

# Add all files
git add .

# Commit changes
git commit -m "Nyaya integrated backend - production ready with all components"

# Add remote origin (replace with your GitHub repo URL)
git remote add origin https://github.com/yourusername/nyaya-backend.git

# Push to main branch
git branch -M main
git push -u origin main