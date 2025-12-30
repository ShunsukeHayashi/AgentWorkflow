#!/bin/bash

# Configuration
JOB_FILE="miyabi_bridge/job.json"
NOTE_URL="https://note.com/n/new"

# 1. Load Data
if [ ! -f "$JOB_FILE" ]; then
    osascript -e 'display notification "Error: No Job Found" with title "Miyabi Bridge"'
    exit 1
fi

TITLE=$(python3 -c "import json; print(json.load(open('$JOB_FILE'))['title'])")
BODY=$(python3 -c "import json; print(json.load(open('$JOB_FILE'))['body'])")

# 2. Automation
osascript <<EOD
tell application "Google Chrome"
    activate
    open location "$NOTE_URL"
    
    -- Wait for load loop
    repeat with i from 1 to 20
        delay 0.5
        if (execute front window's active tab javascript "document.readyState") is "complete" then
            exit repeat
        end if
    end repeat
    
    delay 1 -- Extra stability
    
    -- CHECK: Are we on the login page or 404?
    set pageTitle to title of active tab of front window
    if pageTitle contains "404" or pageTitle contains "ログイン" then
        display dialog "Note.comへのログインが必要です。" & return & "ログインしてから、もう一度実行してください。" buttons {"OK"} default button "OK" with icon caution
        return
    end if
    
end tell

tell application "System Events"
    tell process "Google Chrome"
        set frontmost to true
        delay 0.5
        
        -- Type Title
        keystroke "$TITLE"
        delay 0.5
        
        -- Move to Body (Enter is safer than Tab for Note's new editor)
        key code 36 -- Enter
        delay 0.5
        
        -- Paste Body
        set the clipboard to "$BODY"
        delay 0.2
        keystroke "v" using command down
        
        display notification "記事の入力が完了しました" with title "Miyabi Bridge"
    end tell
end tell
EOD
