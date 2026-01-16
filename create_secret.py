from omniagentpay.onboarding import quick_setup
import os

# Your real Circle API key from .env or provided here
CIRCLE_API_KEY = "TEST_API_KEY:90b965fbffbeaa23edf585dbd960bbf0:f3613cf4b1e9f06e839d4ae7da27091a"

if __name__ == "__main__":
    print("--- OmniAgentPay Quick Onboarding ---")
    try:
        # This will:
        # 1. Generate a new secure Entity Secret
        # 2. Register it with Circle's API
        # 3. Create/Update your .env file
        # 4. Save a recovery backup file locally
        quick_setup(CIRCLE_API_KEY)
        
        print("\n✅ Setup Complete!")
        print("Your .env has been updated. Please restart your MCP server.")
        
    except Exception as e:
        print(f"\n❌ Setup Failed: {e}")