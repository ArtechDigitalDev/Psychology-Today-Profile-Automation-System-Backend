"""
playwright_automation.py
Browser automation for Psychology Today profile management using Playwright.
"""
import random
from playwright.sync_api import sync_playwright
from app.services.ai_content import personal_statement_content
import time
import asyncio
import sys
from app.config import settings  # Import settings for LOGIN_URL
from typing import Dict, Optional, Tuple
from app.automation.profile_sections import (
    update_personal_statement,
    update_specialties,
    update_top_specialties,
    update_my_identity,
    update_availability,
    update_additional_location,
    update_fees,
)

# Fix for Windows asyncio subprocess issue
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


# Custom Exceptions for different error types
class LoginError(Exception):
    """Raised when login fails"""
    pass

class NavigationError(Exception):
    """Raised when page navigation fails"""
    pass

class ElementNotFoundError(Exception):
    """Raised when required element is not found"""
    pass

class ContentGenerationError(Exception):
    """Raised when AI content generation fails"""
    pass

class ProfileUpdateError(Exception):
    """Raised when profile update fails"""
    pass

class NetworkError(Exception):
    """Raised when network issues occur"""
    pass


# Use LOGIN_URL from config
# WEBSITE_URL = settings.WEBSITE_URL
WEBSITE_URL = "https://member.psychologytoday.com/us"


def handle_login_errors(page, username: str) -> Tuple[bool, Optional[str]]:
    """
    Check for various login error scenarios and return (is_error, error_message)
    """
    try:
        # Check for invalid credentials error (multiple variations)
        invalid_creds_selectors = [
            'text=Invalid username or password',
            'text=Invalid credentials',
            'text=Username or password is incorrect',
            'text=Login failed',
            'text=Authentication failed',
            'text=Wrong username or password',
            'text=Incorrect username or password',
            'text=Invalid login',
            'text=Login error'
        ]
        
        for selector in invalid_creds_selectors:
            try:
                invalid_creds = page.locator(selector)
                if invalid_creds.count() > 0:
                    return True, f"Invalid credentials for user '{username}'"
            except:
                continue
        
        # Check for account locked error
        account_locked_selectors = [
            'text=Account locked',
            'text=Account suspended',
            'text=Account disabled',
            'text=Account temporarily locked'
        ]
        
        for selector in account_locked_selectors:
            try:
                account_locked = page.locator(selector)
                if account_locked.count() > 0:
                    return True, f"Account locked for user '{username}'"
            except:
                continue
        
        # Check for too many attempts error
        too_many_attempts_selectors = [
            'text=Too many login attempts',
            'text=Too many failed attempts',
            'text=Maximum login attempts exceeded',
            'text=Please try again later'
        ]
        
        for selector in too_many_attempts_selectors:
            try:
                too_many_attempts = page.locator(selector)
                if too_many_attempts.count() > 0:
                    return True, f"Too many login attempts for user '{username}'"
            except:
                continue
        
        # Check for captcha
        captcha_selectors = [
            'text=CAPTCHA',
            'text=Captcha',
            'text=Verify you are human',
            'text=Security check'
        ]
        
        for selector in captcha_selectors:
            try:
                captcha = page.locator(selector)
                if captcha.count() > 0:
                    return True, f"CAPTCHA required for user '{username}'"
            except:
                continue
        
        # Check for general error messages
        error_selectors = [
            'text=error',
            'text=Error',
            'text=ERROR',
            'text=failed',
            'text=Failed',
            'text=FAILED',
            'text=invalid',
            'text=Invalid',
            'text=INVALID'
        ]
        
        for selector in error_selectors:
            try:
                error_elem = page.locator(selector)
                if error_elem.count() > 0:
                    error_text = error_elem.first.text_content()
                    if len(error_text) < 100:  # Only short error messages
                        return True, f"Login error for user '{username}': {error_text}"
            except:
                continue
        
        # Check if still on login page after login attempt
        current_url = page.url
        if "/login" in current_url:
            return True, f"Still on login page after login attempt for user '{username}'"
        
        # Check if redirected to error page
        if "error" in current_url.lower():
            return True, f"Redirected to error page for user '{username}'"
        
        # Check page title for error indicators
        try:
            page_title = page.title()
            if "error" in page_title.lower() or "login" in page_title.lower():
                return True, f"Page title indicates error for user '{username}': {page_title}"
        except:
            pass
        
        return False, None
        
    except Exception as e:
        return True, f"Login error detection failed: {str(e)}"


def login_and_edit_profile(username: str, password: str, fee_toggle_positive: bool = True) -> Dict[str, dict]:
    """
    Logs into Psychology Today using Playwright, navigates to the dashboard, and updates profile with AI content.
    Returns a dict of updated fields: {field: {"old": old_value, "new": new_value}}
    
    Error Handling:
    - Login errors (invalid credentials, account locked, etc.)
    - Navigation errors (page load failures)
    - Element not found errors
    - AI content generation errors
    - Network errors
    - Profile update errors
    """
    updated_fields = {}
    error_details = []

    # Import scheduler to check stop signal
    from app.automation.weekly_maintenance import scheduler

    with sync_playwright() as p:
        # Use headless=True for production, headless=False for debugging
        browser = p.chromium.launch(
            headless=False,  # Use headless for better stability and performance
            args=[
                '--window-size=1366,768',  # Set browser window size
                '--no-sandbox',  # Required for AWS/Linux
                '--disable-dev-shm-usage',  # Required for AWS/Linux
                '--disable-gpu',  # Required for headless on AWS
                '--no-first-run',
                '--disable-extensions',
                '--disable-plugins',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--disable-blink-features=AutomationControlled',
                '--disable-ipc-flooding-protection',
                # AWS specific optimizations
                '--disable-setuid-sandbox',  # AWS security
                '--disable-background-networking',  # Reduce network usage
                '--disable-default-apps',  # Reduce memory usage
                '--disable-sync',  # Disable Chrome sync
                '--disable-translate',  # Disable translation
                '--hide-scrollbars',  # Hide scrollbars
                '--mute-audio',  # Mute audio
                '--no-default-browser-check',  # Skip default browser check
                '--disable-logging',  # Reduce logging
                '--disable-permissions-api',  # Disable permissions
                '--disable-notifications',  # Disable notifications
                '--disable-popup-blocking',  # Allow popups if needed
                '--disable-prompt-on-repost',  # Disable repost prompts
                '--disable-hang-monitor',  # Disable hang monitoring
                '--disable-client-side-phishing-detection',  # Disable phishing detection
                '--disable-component-update',  # Disable component updates
                '--disable-domain-reliability',  # Disable domain reliability
                '--disable-features=TranslateUI',  # Disable translate UI
                '--disable-ipc-flooding-protection',  # Disable IPC flooding protection
                '--memory-pressure-off',  # Disable memory pressure
                '--max_old_space_size=4096'  # Increase memory limit
            ]
        )

        context = browser.new_context(
            viewport={'width': 1366, 'height': 768},  # Page viewport size
            screen={'width': 1366, 'height': 768},    # Screen size
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = context.new_page()
        
        # Set longer timeouts
        page.set_default_timeout(60000)  # 60 seconds
        page.set_default_navigation_timeout(60000)  # 60 seconds

        try:
            # Step 1: Navigate to login page
            try:
                page.goto(WEBSITE_URL+"/login", timeout=60000)  # 60 seconds timeout
                print(f"Successfully loaded login page for {username}")
            except Exception as e:
                error_msg = f"Failed to load login page: {str(e)}"
                print(error_msg)
                error_details.append(error_msg)
                # Retry once
                time.sleep(5)
                try:
                    page.goto(WEBSITE_URL+"/login", timeout=60000)
                    print(f"Login page loaded on retry for {username}")
                except Exception as retry_e:
                    error_msg = f"Failed to load login page on retry: {str(retry_e)}"
                    print(error_msg)
                    error_details.append(error_msg)
                    raise NavigationError(error_msg)
            
            # Check stop signal before continuing
            if scheduler.should_stop:
                print(f"Stop signal received during login for {username}")
                return {}
            
            # Step 2: Login process with error handling
            try:
                # Human-like login behavior
                time.sleep(random.uniform(2, 5))
                
                # Type username with human-like delays
                try:
                    username_field = page.locator('input[name="username"]')
                    if username_field.count() == 0:
                        raise ElementNotFoundError("Username field not found")
                    
                    username_field.click()
                    time.sleep(random.uniform(1,5))
                    for char in username:
                        page.keyboard.type(char)
                        time.sleep(random.uniform(0.05, 0.15))
                    print(f"Username entered for {username}")
                except Exception as e:
                    error_msg = f"Failed to enter username: {str(e)}"
                    print(error_msg)
                    error_details.append(error_msg)
                    raise LoginError(error_msg)
                
                time.sleep(random.uniform(1, 5))
                
                # Type password with human-like delays
                try:
                    password_field = page.locator('input[name="password"]')
                    if password_field.count() == 0:
                        raise ElementNotFoundError("Password field not found")
                    
                    password_field.click()
                    time.sleep(random.uniform(1, 5))
                    for char in password:
                        page.keyboard.type(char)
                        time.sleep(random.uniform(0.05, 0.15))
                    print(f"Password entered for {username}")
                except Exception as e:
                    error_msg = f"Failed to enter password: {str(e)}"
                    print(error_msg)
                    error_details.append(error_msg)
                    raise LoginError(error_msg)
                
                time.sleep(random.uniform(2, 5))
                
                # Click login button
                try:
                    login_button = page.locator("#button-login-submit")
                    if login_button.count() == 0:
                        raise ElementNotFoundError("Login button not found")
                    
                    login_button.hover()
                    time.sleep(random.uniform(1, 5))
                    login_button.click()
                    print(f"Login button clicked for {username}")
                except Exception as e:
                    error_msg = f"Failed to click login button: {str(e)}"
                    print(error_msg)
                    error_details.append(error_msg)
                    raise LoginError(error_msg)
                
                time.sleep(random.uniform(12, 18))  # Wait for login
                
                # Enhanced error detection after login
                print(f"Checking login status for {username}...")
                
                # Check current URL and page content
                current_url = page.url
                page_title = page.title()
                print(f"Current URL after login: {current_url}")
                print(f"Page title after login: {page_title}")
                
                # Check for specific error messages in page content
                page_content = page.content()
                error_indicators = [
                    'Invalid username or password',
                    'Account locked',
                    'Too many attempts',
                    'CAPTCHA required',
                    'Verification needed',
                    'Security check',
                    'Two-factor authentication',
                    'Account suspended'
                ]
                
                for indicator in error_indicators:
                    if indicator.lower() in page_content.lower():
                        error_msg = f"Login error detected: {indicator} for user '{username}'"
                        print(error_msg)
                        error_details.append(error_msg)
                        raise LoginError(error_msg)
                
                # Check for login errors
                is_error, error_msg = handle_login_errors(page, username)
                if is_error:
                    print(f"Login error detected: {error_msg}")
                    error_details.append(error_msg)
                    raise LoginError(error_msg)
                
                # Additional verification: Check if we can access profile elements
                try:
                    # Wait a bit more for page to load completely
                    time.sleep(5)
                    
                    # Check if we're still on login page
                    current_url = page.url
                    if "/login" in current_url:
                        error_msg = f"Login failed for user '{username}' - still on login page"
                        print(error_msg)
                        error_details.append(error_msg)
                        raise LoginError(error_msg)
                    
                    # Try to find profile elements to confirm successful login
                    profile_elements = [
                        '.src-components-header-profileImageWrapper-3AXi',
                        'text=Profile',
                        'text=Logout',
                        '.profile-section'
                    ]
                    
                    login_successful = False
                    for selector in profile_elements:
                        try:
                            element = page.locator(selector)
                            if element.count() > 0:
                                login_successful = True
                                break
                        except:
                            continue
                    
                    if not login_successful:
                        error_msg = f"Login failed for user '{username}' - no profile elements found"
                        print(error_msg)
                        error_details.append(error_msg)
                        raise LoginError(error_msg)
                        
                except Exception as e:
                    if "LoginError" in str(type(e)):
                        raise
                    else:
                        error_msg = f"Login verification failed for user '{username}': {str(e)}"
                        print(error_msg)
                        error_details.append(error_msg)
                        raise LoginError(error_msg)
                
                print(f"Successfully logged in for {username}")
                
            except Exception as e:
                if isinstance(e, LoginError):
                    raise
                else:
                    error_msg = f"Unexpected login error: {str(e)}"
                    print(error_msg)
                    error_details.append(error_msg)
                    raise LoginError(error_msg)

            # Step 3: Navigate to profile page
            try:
                page.goto(WEBSITE_URL + "/profile", timeout=60000)
                print(f"Successfully navigated to profile page for {username}")
            except Exception as e:
                error_msg = f"Failed to load profile page: {str(e)}"
                print(error_msg)
                error_details.append(error_msg)
                # Retry once
                time.sleep(5)
                try:
                    page.goto(WEBSITE_URL + "/profile", timeout=60000)
                    print(f"Profile page loaded on retry for {username}")
                except Exception as retry_e:
                    error_msg = f"Failed to load profile page on retry: {str(retry_e)}"
                    print(error_msg)
                    error_details.append(error_msg)
                    raise NavigationError(error_msg)
            
            time.sleep(random.uniform(10, 15))
        
            # Step 4: Extract Mental Health Role
            # try:
            #     mental_health_role_element = page.locator('.label-value-pair:has-text("Mental Health Role:") .value')
            #     mental_health_role = "Mental Health Role element not defined"
            #     if mental_health_role_element.count() > 0:
            #         mental_health_role = mental_health_role_element.text_content()
            #         print(f"Mental Health Role extracted: {mental_health_role}")
            #     else:
            #         print("Mental Health Role element not found, using default")
            # except Exception as e:
            #     error_msg = f"Failed to extract Mental Health Role: {str(e)}"
            #     print(error_msg)
            #     error_details.append(error_msg)
            #     mental_health_role = "Mental Health Role element not defined"
            
            # time.sleep(random.uniform(3, 5))

# #############################################################################################################################################

            # Step 6: Update profile sections with error handling
            try:
                # Update Personal Statement
                # try:
                #     personal_statement_updates = update_personal_statement(page, username)
                #     updated_fields.update(personal_statement_updates)
                #     print(f"Personal statement updated for {username}")
                # except Exception as e:
                #     error_msg = f"Failed to update personal statement: {str(e)}"
                #     print(error_msg)
                #     error_details.append(error_msg)

                # # Update Identity
                # try:
                #     identity_updates = update_my_identity(page, username)
                #     updated_fields.update(identity_updates)
                #     print(f"Identity updated for {username}")
                # except Exception as e:
                #     error_msg = f"Failed to update identity: {str(e)}"
                #     print(error_msg)
                #     error_details.append(error_msg)

                # Update Additional Location
                # try:
                #     additional_location_updates = update_additional_location(page, username)
                #     updated_fields.update(additional_location_updates)
                #     print(f"Additional location updated for {username}")
                # except Exception as e:
                #     error_msg = f"Failed to update additional location: {str(e)}"
                #     print(error_msg)
                #     error_details.append(error_msg)


                # Update Availability
                # try:
                #     availability_updates = update_availability(page, username)
                #     updated_fields.update(availability_updates)
                #     print(f"Availability updated for {username}")
                # except Exception as e:
                #     error_msg = f"Failed to update availability: {str(e)}"
                #     print(error_msg)
                #     error_details.append(error_msg)

                # Update Fees
                try:
                    fees_updates = update_fees(page, username, fee_toggle_positive)
                    updated_fields.update(fees_updates)
                    print(f"Fees updated for {username}")
                except Exception as e:
                    error_msg = f"Failed to update fees: {str(e)}"
                    print(error_msg)
                    error_details.append(error_msg)
                
                # # Update Specialties
                # try:
                #     specialties_updates = update_specialties(page, username)
                #     updated_fields.update(specialties_updates)
                #     print(f"Specialties updated for {username}")
                # except Exception as e:
                #     error_msg = f"Failed to update specialties: {str(e)}"
                #     print(error_msg)
                #     error_details.append(error_msg)
                
                # # Update Top Specialties
                # try:
                #     # Generate AI content for top specialties
                #     top_specialties_updates = update_top_specialties(page, username)
                #     updated_fields.update(top_specialties_updates)
                #     print(f"Top specialties updated for {username}")
                # except Exception as e:
                #     error_msg = f"Failed to update top specialties: {str(e)}"
                #     print(error_msg)
                #     error_details.append(error_msg)

            except Exception as e:
                error_msg = f"Profile update failed: {str(e)}"
                print(error_msg)
                error_details.append(error_msg)
                raise ProfileUpdateError(error_msg)

            # Step 7: Logout
            try:
                time.sleep(random.uniform(8, 15))
                
                # Hover over profile image first - try multiple selectors
                profile_selectors = [
                    '.src-components-header-profileImageWrapper-3AXi',
                    '.src-components-header-text-2OQO', 
                    '.src-components-header-profileAvatarWrapper-2Emx'
                ]
                
                profile_image = None
                for selector in profile_selectors:
                    try:
                        element = page.locator(selector)
                        if element.count() > 0:
                            profile_image = element
                            print(f"Profile element found with selector '{selector}' for {username}")
                            break
                    except:
                        continue
                
                if profile_image and profile_image.count() > 0:
                    profile_image.hover()
                    time.sleep(random.uniform(1, 3))
                    profile_image.click()
                    time.sleep(random.uniform(3, 7))
                    
                    try:
                        logout_option = page.locator('text=Logout')
                        if logout_option.count() > 0:
                            logout_option.hover()
                            time.sleep(random.uniform(1, 2))
                            logout_option.click()
                            print(f"Successfully logged out for {username}")
                        else:
                            print(f"Logout option not found for {username}")
                    except Exception as e:
                        print(f"Logout failed: {str(e)}")
                else:
                    print(f"Profile image not found for logout for {username}")
                    
            except Exception as e:
                print(f"Logout error (non-critical): {str(e)}")

        except Exception as e:
            print(f"Critical error in automation for {username}: {str(e)}")
            error_details.append(f"Critical error: {str(e)}")
            # Re-raise the exception to ensure it's properly handled
            raise
            
        finally:
            # Always close browser
            try:
                browser.close()
                print(f"Browser closed for {username}")
            except Exception as e:
                print(f"Error closing browser: {str(e)}")
    
    print(f"Updated fields for {username}: {updated_fields}")
    if error_details:
        print(f"Error details for {username}: {error_details}")
    
    return updated_fields

# Example usage (remove or adapt for production)
# login_and_edit_profile("your_email", "your_password") 

if __name__ == "__main__":
    # Replace with real credentials or load from a secure source
    # username = "mosharof"
    # password = "12345678aA"
    username = "wickerpsych46"
    password = "Ilovejake10"
    login_and_edit_profile(username, password) 