from app.core.security import auth_service

if __name__ == "__main__":
    print(f"1. Visit this URL: \n{auth_service.get_authorization_url()}")
    code = input("\n2. Paste the 'code' here: ").strip()
    
    auth_service.exchange_code_for_token(code)
    print("\nSuccess! Tokens stored in tokens.json.")