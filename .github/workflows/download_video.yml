name: Download Google Drive Videos

on:
  schedule:
    - cron: '0 7 * * *'  # يوميًا الساعة 7 صباحًا (بتوقيت UTC)

jobs:
  download-videos:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout repository
      uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.8'

    - name: Install dependencies
      run: |
        pip install google-api-python-client google-auth google-auth-httplib2 google-auth-oauthlib

    - name: Run video download script
      env:
        GOOGLE_APPLICATION_CREDENTIALS: ${{ secrets.GOOGLE_APPLICATION_CREDENTIALS }}  # سر client_secrets.json
      run: |
        python download_video.py
