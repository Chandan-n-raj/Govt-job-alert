# govt-job-monitor

A production-ready Python 3.12 monitor for tracking official entry-level officer recruitment notifications from government and public-sector organizations.

## Overview

govt-job-monitor checks official recruitment pages, filters for relevant officer-level roles, and sends email alerts only when a notification has not been seen before. It uses JSON persistence to ensure duplicate detection survives repeated runs.

## Features

- Monitors official recruitment pages for the configured organizations
- Filters for entry-level officer roles such as Grade A, Grade B, Assistant Manager, Management Trainee, Executive Trainee, Officer, and similar titles
- Excludes consultant, contract, apprentice, internship, temporary, experienced, lateral, and senior leadership posts
- Persists seen notification IDs in notifications.json so duplicates are not re-sent
- Implements retry logic, request timeouts, user-agent headers, and graceful failure handling
- Supports SMTP-based email notifications
- Includes unit tests with coverage reporting

## Installation

### Prerequisites

- Python 3.12
- pip

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use .venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration

The application uses environment variables for email delivery. You can set them in your shell or in your GitHub repository secrets.

Required for email delivery:

- EMAIL_FROM
- EMAIL_TO
- SMTP_HOST
- SMTP_PORT
- SMTP_USERNAME
- SMTP_PASSWORD
- SMTP_USE_TLS

Example:

```bash
export EMAIL_FROM="you@example.com"
export EMAIL_TO="you@example.com"
export SMTP_HOST="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USERNAME="you@example.com"
export SMTP_PASSWORD="your-app-password"
export SMTP_USE_TLS="true"
```

## GitHub setup

### 1. Push the repository to GitHub

Push the repository to GitHub before you enable the workflow. The workflow file lives at [.github/workflows/monitor.yml](.github/workflows/monitor.yml), and GitHub Actions will only run it from the default branch.

### 2. Create GitHub repository secrets

Go to your repository in GitHub and create the secrets here:

1. Open your repository page.
2. Click Settings.
3. In the left sidebar, open Secrets and variables.
4. Select Actions.
5. Click New repository secret.
6. Add one secret at a time using the exact names below.

Add these repository secrets:

- EMAIL_FROM
- EMAIL_TO
- SMTP_HOST
- SMTP_PORT
- SMTP_USERNAME
- SMTP_PASSWORD
- SMTP_USE_TLS

The workflow in [.github/workflows/monitor.yml](.github/workflows/monitor.yml) uses these secrets automatically. If you do not provide them, the monitor will still run and skip email delivery gracefully.

### 3. Configure Gmail App Password

If you want email alerts through Gmail, create an App Password instead of using your normal Gmail password.

1. Sign in to your Google account at https://myaccount.google.com/security.
2. Turn on 2-Step Verification if it is not already enabled.
3. Search for App passwords.
4. Choose Mail as the app and Other (custom name) as the device.
5. Enter a name such as GitHub Monitor and click Generate.
6. Copy the 16-character password that Google shows.
7. Use that value as the SMTP_PASSWORD secret.
8. Use your Gmail address as both EMAIL_FROM and SMTP_USERNAME.

Example values for Gmail:

- EMAIL_FROM: yourname@gmail.com
- EMAIL_TO: yourname@gmail.com
- SMTP_HOST: smtp.gmail.com
- SMTP_PORT: 587
- SMTP_USERNAME: yourname@gmail.com
- SMTP_PASSWORD: your-16-character-app-password
- SMTP_USE_TLS: true

### 4. Enable the workflow

After the workflow file has been pushed to GitHub:

1. Open the Actions tab in your repository.
2. If GitHub shows a message about workflows being disabled, click the button to enable them.
3. If the workflow is already listed, select it and confirm it is enabled.

### 5. Test it manually

You can run the workflow immediately without waiting for the scheduled time:

1. Open the Actions tab.
2. Select the workflow named govt-job-monitor.
3. Click Run workflow.
4. Choose the branch and click Run workflow.
5. Watch the run log to confirm the monitor started and finished.

If you want to verify that the workflow can commit updates, make sure the repository has a default branch and the workflow has permission to write contents.

### 6. Change the schedule

The schedule is defined in [.github/workflows/monitor.yml](.github/workflows/monitor.yml) using a cron expression.

The current schedule is set to run daily at 08:00 AM Asia/Kolkata. GitHub Actions runs cron expressions in UTC, so the current expression is set to match that local time.

To change it:

1. Open [.github/workflows/monitor.yml](.github/workflows/monitor.yml).
2. Edit the cron line under the schedule section.
3. Commit and push the change.

Example cron values:

- `0 2 * * *` → 07:30 AM IST
- `30 2 * * *` → 08:00 AM IST
- `0 3 * * *` → 08:30 AM IST

If you want, you can also switch to a different timezone by adjusting the cron expression directly.

## Running locally

Run the monitor manually:

```bash
python main.py
```

To run the tests:

```bash
python -m pytest -q --cov=. --cov-report=term-missing
```

## Running on GitHub Actions

The workflow is configured to run on a schedule and can also be triggered manually.

### Schedule

The workflow runs daily using a cron expression defined in [.github/workflows/monitor.yml](.github/workflows/monitor.yml).

### Manual trigger

You can run it from the Actions tab in GitHub.

## Project architecture

```text
govt-job-monitor/
├── config.py                 # global settings and environment configuration
├── database.py               # JSON-based persistence for seen notifications
├── email_sender.py           # SMTP-based email delivery logic
├── filters/
│   └── job_filter.py         # notification relevance filtering
├── scrapers/
│   ├── base.py               # shared HTTP request and retry logic
│   ├── official_sites.py     # parsing and extraction from official pages
│   └── registry.py           # list of monitored organizations
├── main.py                   # orchestration entry point
├── tests/                    # unit and integration-style regression tests
├── requirements.txt          # Python dependencies
└── .github/workflows/monitor.yml
```

## Troubleshooting

### Emails are not being sent

- Confirm that all SMTP environment variables or GitHub secrets are set correctly.
- Ensure the SMTP provider allows app-password authentication if required.
- Check the workflow logs for delivery errors.

### Network failures

- The scraper retries requests and logs failures without crashing the whole run.
- If one site is unreachable, the monitor continues checking the rest.

### Duplicate alerts

- Duplicate detection is persisted in notifications.json.
- If you want to re-send alerts for existing notifications, remove the relevant IDs from the JSON file.

### Tests failing

- Reinstall dependencies with:

```bash
pip install -r requirements.txt
```

- Run the suite again:

```bash
python -m pytest -q --cov=. --cov-report=term-missing
```

## Screenshots placeholders

- Dashboard / workflow run screenshot: coming soon
- Email alert example: coming soon
- GitHub Actions run output: coming soon

## License

This project is intended for personal monitoring and automation use. Adjust it to fit your own environment and compliance requirements.
