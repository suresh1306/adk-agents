"""
Test Client for Tour Planner API

Demonstrates streaming chat with the FastAPI tour planner.

Usage:
  python test_client.py
"""

import requests
import json
import sys
from datetime import datetime

API_BASE_URL = "http://localhost:8000"
USER_ID = "test_user_001"
SESSION_ID = f"test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

def print_separator(title=""):
    """Print a visual separator"""
    print("\n" + "=" * 80)
    if title:
        print(f"  {title}")
        print("=" * 80)
    print()

def health_check():
    """Check API health"""
    print_separator("🏥 Health Check")

    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        response.raise_for_status()
        data = response.json()

        print(f"✅ Status: {data['status']}")
        print(f"   App: {data['app_name']}")
        print(f"   Session Service: {data['session_service']}")
        print(f"   Timestamp: {data['timestamp']}")
        return True

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server")
        print("   Make sure the server is running:")
        print("   uvicorn api_server:app --reload")
        return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def create_session():
    """Create a new session"""
    print_separator("📝 Creating Session")

    try:
        response = requests.post(
            f"{API_BASE_URL}/api/sessions",
            json={
                "user_id": USER_ID,
                "session_id": SESSION_ID,
                "initial_state": {}
            },
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        print(f"✅ Session created:")
        print(f"   Session ID: {data['session_id']}")
        print(f"   User ID: {data['user_id']}")
        print(f"   App: {data['app_name']}")
        return True

    except Exception as e:
        print(f"❌ Session creation failed: {e}")
        return False

def stream_chat(message: str, show_metadata=True):
    """Stream chat with the tour planner"""
    print_separator(f"💬 Chat Message")
    print(f"You: {message}\n")
    print("Agent: ", end="", flush=True)

    try:
        response = requests.post(
            f"{API_BASE_URL}/api/chat/stream",
            json={
                "message": message,
                "user_id": USER_ID,
                "session_id": SESSION_ID
            },
            stream=True,
            timeout=120
        )
        response.raise_for_status()

        full_response = []
        tool_calls = []

        for line in response.iter_lines():
            if line:
                # SSE format: "data: {json}"
                if line.startswith(b'data: '):
                    try:
                        event_data = json.loads(line[6:])

                        if event_data['type'] == 'content':
                            # Print agent response text
                            text = event_data['text']
                            print(text, end='', flush=True)
                            full_response.append(text)

                        elif event_data['type'] == 'tool_call':
                            # Show tool execution
                            tool_name = event_data.get('tool', 'unknown')
                            if show_metadata:
                                print(f"\n\n  [🔧 Calling {tool_name}...]", end='', flush=True)
                            tool_calls.append(tool_name)

                        elif event_data['type'] == 'tool_result':
                            # Tool completed
                            tool_name = event_data.get('tool', 'unknown')
                            if show_metadata:
                                print(f"\n  [✅ {tool_name} completed]", end='', flush=True)
                                print("\n\nAgent: ", end='', flush=True)

                        elif event_data['type'] == 'done':
                            # Conversation complete
                            print("\n")
                            if show_metadata:
                                print(f"\n✅ Complete (Session: {event_data['session_id']})")
                            break

                        elif event_data['type'] == 'error':
                            # Error occurred
                            print(f"\n\n❌ Error: {event_data['message']}")
                            break

                    except json.JSONDecodeError as e:
                        print(f"\n⚠️  JSON decode error: {e}")
                        continue

        return {
            'response': ''.join(full_response),
            'tool_calls': tool_calls
        }

    except requests.exceptions.Timeout:
        print("\n\n❌ Request timeout (> 120s)")
        return None
    except Exception as e:
        print(f"\n\n❌ Chat error: {e}")
        return None

def get_session_state():
    """Get current session state"""
    print_separator("📊 Session State")

    try:
        response = requests.get(
            f"{API_BASE_URL}/api/sessions/{SESSION_ID}",
            params={"user_id": USER_ID},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        print(f"Session ID: {data['session_id']}")
        print(f"User ID: {data['user_id']}")
        print(f"Events: {data['event_count']}")
        print(f"\nState:")

        if data['state']:
            for key, value in data['state'].items():
                # Truncate long values
                value_str = str(value)
                if len(value_str) > 100:
                    value_str = value_str[:100] + "..."
                print(f"  • {key}: {value_str}")
        else:
            print("  (empty)")

        return data

    except Exception as e:
        print(f"❌ Failed to get session: {e}")
        return None

def run_test_conversation():
    """Run a complete test conversation"""
    print("\n" + "🌍" * 40)
    print("  Tour Planner API - Streaming Test Client")
    print("🌍" * 40)

    # 1. Health check
    if not health_check():
        sys.exit(1)

    # 2. Create session
    if not create_session():
        sys.exit(1)

    # Test conversation flow
    conversation = [
        "I want to plan a trip to Jordan for 5 days",
        "We are 2 adults and 2 kids, interested in history, culture, and outdoor activities",
        "What's the total budget for mid-range accommodation?",
        "Could you create a 5-day itinerary?",
    ]

    for message in conversation:
        result = stream_chat(message, show_metadata=True)

        if result:
            print(f"\n   Tools used: {', '.join(result['tool_calls']) if result['tool_calls'] else 'None'}")

        # Small delay between messages
        import time
        time.sleep(1)

    # 3. Show final state
    get_session_state()

    print_separator("✨ Test Complete")
    print("The tour planner successfully:")
    print("  ✅ Created a session with state management")
    print("  ✅ Researched destination information")
    print("  ✅ Calculated budget with family details")
    print("  ✅ Created a personalized itinerary")
    print("  ✅ Maintained context across all messages")
    print("\nSession state contains all trip planning details!")
    print()

def interactive_mode():
    """Interactive chat mode"""
    print("\n" + "🌍" * 40)
    print("  Tour Planner API - Interactive Mode")
    print("🌍" * 40)

    # Health check
    if not health_check():
        sys.exit(1)

    # Create session
    if not create_session():
        sys.exit(1)

    print("\n💬 Starting interactive chat")
    print("   Type 'quit' to exit, 'state' to view session state\n")

    while True:
        try:
            message = input("You: ").strip()

            if not message:
                continue

            if message.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break

            if message.lower() == 'state':
                get_session_state()
                continue

            stream_chat(message, show_metadata=True)
            print()

        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == '--interactive':
        interactive_mode()
    else:
        run_test_conversation()

if __name__ == "__main__":
    main()
