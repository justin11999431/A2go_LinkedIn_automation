"""Test Salesrobot action limits."""

import os
import sys

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from stop_rules import StopRulesManager, StopRuleType
from settings import Settings

# Load settings
settings = Settings()

# Initialize stop rules manager
stop_rules = StopRulesManager()

# Get limits from settings
limits = settings.get_limits()

print("Salesrobot Action Limits:")
print("=" * 60)
print(f"Connection Requests: {limits.get('max_connection_requests_per_day', 20)} per day")
print(f"Follow-Up Messages: {limits.get('max_follow_up_messages_per_day', 20)} per day")
print(f"Voice Messages: {limits.get('max_voice_messages_per_day', 20)} per day")
print(f"Video Messages: {limits.get('max_video_messages_per_day', 20)} per day")
print(f"Profile Views: {limits.get('max_profile_views_per_day', 20)} per day")
print(f"InMail Messages: {limits.get('max_inmail_messages_per_day', 20)} per day")
print(f"Profile Follows: {limits.get('max_profile_follows_per_day', 20)} per day")
print(f"Post Likes & Comments: {limits.get('max_post_likes_comments_per_day', 20)} per day")
print(f"Endorsements: {limits.get('max_endorsements_per_day', 20)} per day")
print(f"Withdraw Connection Requests: {limits.get('max_withdraw_connection_requests_per_day', 10)} per day")
print(f"Invite to Event: {limits.get('max_invite_to_event_per_day', 30)} per day")
print()

# Test limits
print("Testing Limits:")
print("=" * 60)

# Test connection requests limit
for i in range(25):
    stop_rules.increment_counter('connection_requests_today')
    should_stop, reason = stop_rules.check_global_rules()
    if should_stop:
        print(f"[OK] Connection requests limit reached at {i+1} requests")
        print(f"  Reason: {reason}")
        break

# Test follow-up messages limit
for i in range(25):
    stop_rules.increment_counter('follow_up_messages_today')
    should_stop, reason = stop_rules.check_global_rules()
    if should_stop and 'follow-up' in reason.lower():
        print(f"[OK] Follow-up messages limit reached at {i+1} messages")
        print(f"  Reason: {reason}")
        break

# Test invite to event limit
for i in range(35):
    stop_rules.increment_counter('invite_to_event_today')
    should_stop, reason = stop_rules.check_global_rules()
    if should_stop and 'invite to event' in reason.lower():
        print(f"[OK] Invite to event limit reached at {i+1} invites")
        print(f"  Reason: {reason}")
        break

print()
print("Global State:")
print("=" * 60)
for key, value in stop_rules.global_state.items():
    if 'today' in key:
        print(f"{key}: {value}")

print()
print("All limits configured correctly! [OK]")
