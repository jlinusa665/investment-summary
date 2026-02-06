#!/usr/bin/env python3
"""
Calendar Sync for Options Expiration

Syncs option expiration dates to Google Calendar with P&L tracking,
reminders, and action recommendations.
"""

import argparse
import os
import sys
from datetime import datetime, timedelta

# Google Calendar API imports
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    print("Error: Google API libraries not installed.")
    print("Run: pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    sys.exit(1)

from load_portfolio import load_full_portfolio

# =============================================================================
# Configuration
# =============================================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PRIVATE_DATA_DIR = os.path.join(SCRIPT_DIR, "private_data")
CREDENTIALS_FILE = os.path.join(PRIVATE_DATA_DIR, "google_credentials.json")
TOKEN_FILE = os.path.join(PRIVATE_DATA_DIR, "token.json")

# Google Calendar API scope
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# Calendar event settings
EVENT_TIME_HOUR = 9  # 9 AM
EVENT_DURATION_MINUTES = 30


# =============================================================================
# Authentication
# =============================================================================

def get_calendar_service():
    """
    Authenticate with Google Calendar API and return service object.

    Handles OAuth flow for first-time authentication and token refresh.
    """
    creds = None

    # Load existing token if available
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # Refresh or get new credentials if needed
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                print(f"Error: Credentials file not found at {CREDENTIALS_FILE}")
                print("Download OAuth credentials from Google Cloud Console")
                print("and save as 'google_credentials.json' in private_data folder.")
                sys.exit(1)

            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save credentials for next run
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)


# =============================================================================
# Event Generation
# =============================================================================

def generate_event_title(option):
    """Generate calendar event title for an option position."""
    underlying = option.get("underlying_symbol", "???")
    option_type = option.get("option_type", "Option")
    strike = option.get("strike_price", 0)
    is_short = option.get("is_short", False)
    position_prefix = "Short" if is_short else "Long"

    # Use emoji in calendar, but safe_title for console output
    return f"\U0001F4CA {underlying} ${strike} {option_type} expires ({position_prefix})"


def safe_print(text):
    """Print text, replacing non-ASCII characters if needed for Windows console."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', 'replace').decode('ascii'))


def generate_event_description(option, recommendation=None):
    """Generate detailed event description with P&L and action info."""
    lines = []

    # Basic position info
    lines.append(f"Symbol: {option.get('symbol', 'N/A')}")
    lines.append(f"Underlying: {option.get('underlying_symbol', 'N/A')}")
    lines.append(f"Option Type: {option.get('option_type', 'N/A')}")
    lines.append(f"Strike Price: ${option.get('strike_price', 0):.2f}")
    lines.append(f"Position: {option.get('position_type', 'N/A').upper()}")
    lines.append(f"Quantity: {option.get('quantity', 0)}")
    lines.append("")

    # P&L info
    lines.append("=== P&L ===")
    current_value = option.get("current_value", 0)
    total_gain = option.get("total_gain", 0)
    total_gain_pct = option.get("total_gain_percent", 0)

    lines.append(f"Current Value: ${current_value:,.2f}")
    lines.append(f"Total P&L: ${total_gain:,.2f} ({total_gain_pct:.2f}%)")
    lines.append(f"Cost to Close: ${abs(current_value):,.2f}")
    lines.append("")

    # Days info
    days_to_exp = option.get("days_to_expiration", 0)
    lines.append(f"Days to Expiration: {days_to_exp}")
    lines.append("")

    # Recommendation if available
    if recommendation:
        lines.append("=== ACTION RECOMMENDED ===")
        lines.append(f"Priority: {recommendation.get('urgency_level', 'N/A')}")
        lines.append(f"Score: {recommendation.get('combined_priority_score', 0):.1f}")
        lines.append(f"Action: {recommendation.get('recommended_action', 'N/A')}")
        lines.append("")

    # Timestamp
    lines.append(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    return "\n".join(lines)


def create_event_body(option, recommendation=None):
    """Create the full event body for Google Calendar API."""
    title = generate_event_title(option)
    description = generate_event_description(option, recommendation)

    # Parse expiration date
    exp_date_str = option.get("expiration_date", "")
    try:
        exp_date = datetime.strptime(exp_date_str, "%Y-%m-%d")
    except ValueError:
        print(f"Warning: Invalid expiration date '{exp_date_str}' for {option.get('symbol')}")
        return None

    # Set event time to 9 AM
    start_time = exp_date.replace(hour=EVENT_TIME_HOUR, minute=0, second=0)
    end_time = start_time + timedelta(minutes=EVENT_DURATION_MINUTES)

    # Create reminders
    reminders = {
        "useDefault": False,
        "overrides": [
            {"method": "popup", "minutes": 30 * 24 * 60},  # 30 days before
            {"method": "popup", "minutes": 7 * 24 * 60},   # 7 days before
            {"method": "popup", "minutes": 1 * 24 * 60},   # 1 day before
        ]
    }

    # Color based on P&L (green for profit, red for loss)
    total_gain = option.get("total_gain", 0)
    if total_gain >= 0:
        color_id = "10"  # Green
    else:
        color_id = "11"  # Red

    event = {
        "summary": title,
        "description": description,
        "start": {
            "dateTime": start_time.isoformat(),
            "timeZone": "America/New_York",
        },
        "end": {
            "dateTime": end_time.isoformat(),
            "timeZone": "America/New_York",
        },
        "reminders": reminders,
        "colorId": color_id,
    }

    return event


# =============================================================================
# Calendar Operations
# =============================================================================

def find_existing_event(service, title, date_str):
    """Find an existing event by title and date."""
    try:
        # Parse date and create time range for that day
        event_date = datetime.strptime(date_str, "%Y-%m-%d")
        time_min = event_date.replace(hour=0, minute=0, second=0).isoformat() + "Z"
        time_max = event_date.replace(hour=23, minute=59, second=59).isoformat() + "Z"

        events_result = service.events().list(
            calendarId="primary",
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            q=title[:50]  # Search by partial title
        ).execute()

        events = events_result.get("items", [])

        for event in events:
            if event.get("summary") == title:
                return event

        return None

    except HttpError as error:
        print(f"Error searching for event: {error}")
        return None


def create_event(service, event_body, dry_run=False):
    """Create a new calendar event."""
    if dry_run:
        safe_print(f"  [DRY RUN] Would create event: {event_body['summary']}")
        return None

    try:
        event = service.events().insert(calendarId="primary", body=event_body).execute()
        safe_print(f"  Created event: {event_body['summary']}")
        return event
    except HttpError as error:
        print(f"  Error creating event: {error}")
        return None


def update_event(service, event_id, event_body, dry_run=False):
    """Update an existing calendar event."""
    if dry_run:
        safe_print(f"  [DRY RUN] Would update event: {event_body['summary']}")
        return None

    try:
        event = service.events().update(
            calendarId="primary",
            eventId=event_id,
            body=event_body
        ).execute()
        safe_print(f"  Updated event: {event_body['summary']}")
        return event
    except HttpError as error:
        print(f"  Error updating event: {error}")
        return None


# =============================================================================
# Action Recommendations (imported logic)
# =============================================================================

def calculate_time_urgency_score(days_to_expiration):
    """Calculate time urgency score (0-100) based on days to expiration."""
    if days_to_expiration < 7:
        return 100
    elif days_to_expiration <= 14:
        return 80
    elif days_to_expiration <= 30:
        return 60
    elif days_to_expiration <= 60:
        return 40
    else:
        if days_to_expiration >= 180:
            return 0
        return max(0, 40 - ((days_to_expiration - 60) * 40 / 120))


def generate_recommendation(option, max_loss_dollars):
    """Generate action recommendation for a single option."""
    days_to_exp = option.get("days_to_expiration", 999)
    total_gain = option.get("total_gain", 0.0)
    total_gain_percent = option.get("total_gain_percent", 0.0)
    is_short = option.get("is_short", False)
    current_value = option.get("current_value", 0.0)

    # Calculate scores
    time_score = calculate_time_urgency_score(days_to_exp)

    loss_dollar_score = 0.0
    if total_gain < 0 and max_loss_dollars > 0:
        loss_dollar_score = (abs(total_gain) / max_loss_dollars) * 100

    loss_percent_score = 0.0
    if total_gain_percent < 0:
        loss_percent_score = min(100, abs(total_gain_percent))

    combined_score = (time_score * 0.4) + (loss_dollar_score * 0.3) + (loss_percent_score * 0.3)

    # Determine urgency level
    if combined_score >= 90:
        urgency_level = "CRITICAL"
    elif combined_score >= 70:
        urgency_level = "HIGH"
    elif combined_score >= 50:
        urgency_level = "MEDIUM"
    else:
        urgency_level = "LOW"

    # Determine recommended action
    if is_short and total_gain_percent >= 60:
        recommended_action = f"BUY TO CLOSE - Lock in {total_gain_percent:.1f}% profit (TAKE PROFIT NOW)"
    elif is_short and total_gain_percent >= 50:
        recommended_action = f"BUY TO CLOSE - Lock in {total_gain_percent:.1f}% profit (CONSIDER CLOSING)"
    elif total_gain < 0:
        if combined_score >= 90:
            recommended_action = "CLOSE IMMEDIATELY - Catastrophic loss, time running out"
        elif combined_score >= 70:
            recommended_action = "HIGH PRIORITY - Consider closing to stop losses"
        elif combined_score >= 50:
            recommended_action = "MONITOR - Review position, consider action if worsens"
        else:
            recommended_action = "WATCH - Track position for changes"
    else:
        recommended_action = "HOLD - Position is profitable, no immediate action needed"

    return {
        "time_urgency_score": round(time_score, 2),
        "loss_dollar_score": round(loss_dollar_score, 2),
        "loss_percent_score": round(loss_percent_score, 2),
        "combined_priority_score": round(combined_score, 2),
        "urgency_level": urgency_level,
        "recommended_action": recommended_action,
        "cost_to_close": round(abs(current_value), 2)
    }


# =============================================================================
# Main Sync Logic
# =============================================================================

def sync_options_to_calendar(create_all=False, update_all=False, dry_run=False):
    """
    Main function to sync options to Google Calendar.

    Args:
        create_all: Create events for all options
        update_all: Update existing events with latest data
        dry_run: Show what would happen without making changes
    """
    # Load portfolio
    print("Loading portfolio...")
    portfolio = load_full_portfolio()

    if portfolio is None:
        print("Error: Could not load portfolio. Check if portfolio.csv exists.")
        sys.exit(1)

    options = portfolio.get("options_portfolio", [])

    if not options:
        print("No options found in portfolio.")
        return

    print(f"Found {len(options)} options positions.")

    # Calculate max loss for recommendations
    max_loss_dollars = 0.0
    for opt in options:
        total_gain = opt.get("total_gain", 0.0)
        if total_gain < 0:
            max_loss_dollars = max(max_loss_dollars, abs(total_gain))

    # Connect to Google Calendar
    if not dry_run:
        print("Connecting to Google Calendar...")
        service = get_calendar_service()
    else:
        print("[DRY RUN MODE - No changes will be made]")
        service = None

    # Process each option
    print("\nProcessing options...")
    created_count = 0
    updated_count = 0
    skipped_count = 0

    for option in options:
        symbol = option.get("symbol", "Unknown")
        exp_date = option.get("expiration_date", "")

        print(f"\n{symbol} (expires {exp_date}):")

        # Generate recommendation
        recommendation = generate_recommendation(option, max_loss_dollars)

        # Create event body
        event_body = create_event_body(option, recommendation)
        if event_body is None:
            print("  Skipped - invalid date")
            skipped_count += 1
            continue

        title = event_body["summary"]

        if dry_run:
            if create_all:
                safe_print(f"  [DRY RUN] Would create: {title}")
                created_count += 1
            elif update_all:
                safe_print(f"  [DRY RUN] Would update: {title}")
                updated_count += 1
            continue

        # Check if event exists
        existing_event = find_existing_event(service, title, exp_date)

        if existing_event:
            if update_all:
                update_event(service, existing_event["id"], event_body)
                updated_count += 1
            else:
                print(f"  Skipped - event already exists")
                skipped_count += 1
        else:
            if create_all:
                create_event(service, event_body)
                created_count += 1
            else:
                print(f"  Skipped - no existing event and --create-all not specified")
                skipped_count += 1

    # Summary
    print(f"\n{'='*50}")
    print("Summary:")
    print(f"  Created: {created_count}")
    print(f"  Updated: {updated_count}")
    print(f"  Skipped: {skipped_count}")
    if dry_run:
        print("\n[DRY RUN - No actual changes were made]")


# =============================================================================
# CLI
# =============================================================================

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Sync options expiration dates to Google Calendar"
    )
    parser.add_argument(
        "--create-all",
        action="store_true",
        help="Create calendar events for all options"
    )
    parser.add_argument(
        "--update-all",
        action="store_true",
        help="Update existing events with latest P&L data"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would happen without making changes"
    )

    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_arguments()

    if not args.create_all and not args.update_all:
        print("Error: Must specify --create-all or --update-all")
        print("Use --help for usage information.")
        sys.exit(1)

    sync_options_to_calendar(
        create_all=args.create_all,
        update_all=args.update_all,
        dry_run=args.dry_run
    )


if __name__ == "__main__":
    main()
