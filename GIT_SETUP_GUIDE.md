this # 🚀 Git Setup & Push Guide for Flappy Penguin

## Step 1: Download and Install Git

1. Go to: https://git-scm.com/download/win
2. Download the latest Git for Windows
3. Run the installer and follow the default steps
4. **Important**: Check "Git Bash" during installation
5. Restart your computer after installation

## Step 2: Open Git Bash

1. Right-click on your PYgame folder
2. Select "Git Bash Here"
3. A terminal will open

## Step 3: Configure Git (First Time Only)

Run these commands in Git Bash:

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

Replace with your actual name and GitHub email.

## Step 4: Initialize and Push

Copy & paste these commands one by one in Git Bash:

```bash
# Navigate to your project folder
cd /c/Users/asus/OneDrive/Desktop/PYgame

# Initialize git
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Flappy Penguin Game"

# Add your GitHub repository
git remote add origin https://github.com/gksrinila2006-glitch/flappy-penguin.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

## Step 5: When Prompted

When you run the push command:
- A login window will appear
- Select "Authenticate with GitHub in your browser"
- Authorize the application
- Done! Your code is on GitHub!

## Step 6: Verify

1. Go to: https://github.com/gksrinila2006-glitch/flappy-penguin
2. You should see your files (index.html, game.html, main.py, etc.)

## Step 7: Enable GitHub Pages

1. Go to your GitHub repository
2. Click "Settings"
3. Go to "Pages" section
4. Under "Source", select "main" branch
5. Click "Save"
6. Wait 2-3 minutes
7. Your game will be live at: https://gksrinila2006-glitch.github.io/flappy-penguin/

## Files to Push

Make sure these files are in your PYgame folder:
- ✅ index.html (website)
- ✅ game.html (game version)
- ✅ main.py (Python version)
- ✅ highscores.json (scores)

## Troubleshooting

**If you get an error "remote already exists":**
```bash
git remote remove origin
git remote add origin https://github.com/gksrinila2006-glitch/flappy-penguin.git
```

**If authentication fails:**
1. Check your GitHub credentials
2. Or use a Personal Access Token instead of password

**Need help with GitHub authentication?**
See: https://docs.github.com/en/authentication

---

Good luck! Your game will soon be live! 🐧🎮
