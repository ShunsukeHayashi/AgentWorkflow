#!/bin/bash

# 1. Read Job
JOB_FILE="miyabi_bridge/job.json"
TITLE=$(python3 -c "import json; print(json.load(open('$JOB_FILE'))['title'])")
BODY=$(python3 -c "import json; print(json.load(open('$JOB_FILE'))['body'])")

# 2. Open Chrome to Note
open -a "Google Chrome" "https://note.com/n/new"

# 3. Wait for load (Adjustable)
sleep 4

# 4. Use AppleScript to type Title and Body
osascript <<EOD
tell application "Google Chrome" to activate
tell application "System Events"
    delay 0.5
    
    -- Focus Title (Usually focused by default, but tab to be sure or click?)
    -- Note.com creates a draft with Title focused.
    
    -- Type Title
    keystroke "$TITLE"
    delay 0.5
    
    -- Move to Body (Enter or Tab)
    key code 36 -- Enter
    delay 0.5
    
    -- Type Body (Using clipboard is faster/safer for large text)
    set the clipboard to "$BODY"
    delay 0.2
    keystroke "v" using command down
    
end tell
EOD
