"""
profile_sections.py
Contains all the individual profile section update functions for Psychology Today automation.
"""
import random
import time
from typing import Dict
from app.services.ai_content import personal_statement_content


# Website URL
WEBSITE_URL = "https://member.psychologytoday.com/us"


def update_personal_statement(page, username: str) -> Dict[str, dict]:
    """
    Updates the personal statement section with AI-generated content.
    First retrieves current content for AI processing, then generates new content.
    Returns a dict of updated fields.
    """
    updated_fields = {}
    
    try:
        print(f"Starting personal statement update for {username}")
        
        # Navigate to the personal statement page
        page.goto(WEBSITE_URL + "/profile/statement", timeout=60000)
        time.sleep(random.uniform(8, 15))  # Human-like page load wait
        
        # Human-like scrolling and reading behavior
        page.mouse.wheel(0, random.randint(200, 500))  # Scroll down a bit
        time.sleep(random.uniform(2, 4))
        
        # Retrieve current content for AI processing
        current_content = {}
        
        # Get current ideal client field content
        ideal_client_field = page.locator('textarea[aria-label*="Imagine your ideal client"]')
        if ideal_client_field.count() > 0:
            current_ideal_client = ideal_client_field.input_value()
            current_content['ideal_client'] = current_ideal_client
            print(f"Retrieved current ideal client content: {current_ideal_client[:100]}...")
        
        # Get current how can help field content
        how_can_help_field = page.locator('textarea[aria-label*="How can you help?"]')
        if how_can_help_field.count() > 0:
            current_how_can_help = how_can_help_field.input_value()
            current_content['how_can_help'] = current_how_can_help
            print(f"Retrieved current how can help content: {current_how_can_help[:100]}...")
        
        # Get current empathy field content
        empathy_field = page.locator('textarea[aria-label*="Build empathy and invite the potential client to reach out to you."]')
        if empathy_field.count() > 0:
            current_empathy = empathy_field.input_value()
            current_content['empathy_invitation'] = current_empathy
            print(f"Retrieved current empathy content: {current_empathy[:100]}...")
        
        print(f"Retrieved current content for AI processing: {current_content}")
        
        # Generate new AI content using current content
        ai_content = personal_statement_content(
            ideal_client=current_content.get('ideal_client', ''),
            how_can_help=current_content.get('how_can_help', ''),
            empathy_invitation=current_content.get('empathy_invitation', '')
        )
        print(f"Generated AI content for {username}: {ai_content}")

        # Randomly select which field to update (only 1 out of 3)
        fields_to_update = ['ideal_client', 'how_can_help', 'empathy_invitation']
        selected_field = random.choice(fields_to_update)
        print(f"Randomly selected field to update: {selected_field}")

        # Fill ideal client field with human-like typing (only if selected)
        if selected_field == 'ideal_client' and ideal_client_field.count() > 0:
            ideal_client_field.click()
            time.sleep(random.uniform(1, 3))
            
            # Clear existing content first (human-like)
            page.keyboard.press("Control+a")
            time.sleep(random.uniform(0.5, 1.5))
            page.keyboard.press("Backspace")
            time.sleep(random.uniform(1, 2))
            
            # Type with human-like delays
            for char in ai_content["ideal_client"]:
                page.keyboard.type(char)
                time.sleep(random.uniform(0.01, 0.05))  # Random typing speed
                
            updated_fields['ideal_client'] = {
                "old": current_content.get('ideal_client', 'Previous Ideal Client'), 
                "new": ai_content["ideal_client"]
            }
            time.sleep(random.uniform(3, 7))  # Think before next field

        # Fill how can help field with human-like typing (only if selected)
        if selected_field == 'how_can_help' and how_can_help_field.count() > 0:
            how_can_help_field.click()
            time.sleep(random.uniform(1, 3))
            
            # Clear existing content
            page.keyboard.press("Control+a")
            time.sleep(random.uniform(0.5, 1.5))
            page.keyboard.press("Backspace")
            time.sleep(random.uniform(1, 2))
            
            # Type with human-like delays
            for char in ai_content["how_can_help"]:
                page.keyboard.type(char)
                time.sleep(random.uniform(0.01, 0.05))
                
            updated_fields['how_can_help'] = {
                "old": current_content.get('how_can_help', 'Previous How Can Help'), 
                "new": ai_content["how_can_help"]
            }
            time.sleep(random.uniform(3, 7))

        # Fill empathy invitation field with human-like typing (only if selected)
        if selected_field == 'empathy_invitation' and empathy_field.count() > 0:
            empathy_field.click()
            time.sleep(random.uniform(1, 3))
            
            # Clear existing content
            page.keyboard.press("Control+a")
            time.sleep(random.uniform(0.5, 1.5))
            page.keyboard.press("Backspace")
            time.sleep(random.uniform(1, 2))
            
            # Type with human-like delays
            for char in ai_content["empathy_invitation"]:
                page.keyboard.type(char)
                time.sleep(random.uniform(0.01, 0.05))
                
            updated_fields['empathy_invitation'] = {
                "old": current_content.get('empathy_invitation', 'Previous Empathy Invitation'), 
                "new": ai_content["empathy_invitation"]
            }
            time.sleep(random.uniform(5, 10))  # Longer pause before saving

        print(f"Successfully updated {selected_field} field with AI-generated content for {username}")
        print(f"Updated fields: {list(updated_fields.keys())}")
        print(f"Unchanged fields: {[field for field in fields_to_update if field != selected_field]}")

        # Human-like save behavior
        save_button = page.locator('#button-save-personal-statement')
        if save_button.count() > 0:
            # Hover over save button first
            save_button.hover()
            time.sleep(random.uniform(1, 3))
            
            # Click save
            save_button.click()
            time.sleep(random.uniform(8, 10))  # Wait for save confirmation
        
        # Refresh profile page after save (always, regardless of save button)
        page.goto(WEBSITE_URL + "/profile", timeout=60000)
        time.sleep(random.uniform(3, 5))  # Wait for page to load
        
    except Exception as e:
        print(f"Error updating personal statement for {username}: {e}")
    
    return updated_fields

def update_specialties(page, username: str) -> Dict[str, dict]:
    """
    Updates the specialties section by randomly unchecking 2-3 current selections
    and randomly selecting 2-3 new ones from unchecked options.
    Returns a dict of updated fields.
    """
    updated_fields = {}
    
    try:
        # Navigate to specialties page
        page.goto(WEBSITE_URL + "/profile/specialties", timeout=60000)
        time.sleep(random.uniform(2, 4))
        
        # Get all checkboxes
        checkboxes = page.locator('div[role="checkbox"]')
        total = checkboxes.count()
        print(f"Total checkboxes found: {total}")

        # Get specialty names and current states
        specialty_names = []
        currently_checked = []
        currently_unchecked = []
        selected_specialties = []  # Initialize selected_specialties list
        
        for i in range(total):
            try:
                checkbox = checkboxes.nth(i)
                specialty_text = checkbox.locator('xpath=..').text_content().strip()
                if specialty_text:
                    specialty_names.append(specialty_text)
                    
                    aria_checked = checkbox.get_attribute("aria-checked")
                    if aria_checked == "true":
                        currently_checked.append(i)
                    else:
                        currently_unchecked.append(i)
            except:
                pass

        print(f"Currently checked: {len(currently_checked)} specialties")
        print(f"Currently unchecked: {len(currently_unchecked)} specialties")

        # Step 1: Generate random number based on currently checked count
        if len(currently_checked) < 4:
            num_to_change = 1  # If less than 3 checked, only change 1
        else:
            num_to_change = random.randint(2, 3)  # Otherwise random 2-3

        if currently_checked:
            print(f"Will randomly change {num_to_change} specialties (uncheck {num_to_change}, check {num_to_change})")
            
            # Uncheck random specialties
            specialties_to_uncheck = random.sample(currently_checked, num_to_change)
            
            print(f"Randomly unchecking {num_to_change} specialties: {specialties_to_uncheck}")
            
            for i, index in enumerate(specialties_to_uncheck):
                checkbox = checkboxes.nth(index)
                
                # Hover over checkbox first
                checkbox.hover()
                time.sleep(random.uniform(0.3, 0.8))
                
                # Click checkbox to uncheck
                checkbox.click()
                time.sleep(random.uniform(0.5, 1.5))
                
                specialty_name = specialty_names[index] if index < len(specialty_names) else f"Specialty {index+1}"
                print(f"Unchecked: {specialty_name}")
                
                # Sometimes pause longer (human thinking)
                if random.random() < 0.2: # 20% chance
                    time.sleep(random.uniform(1, 3))

        # Step 2: Select new specialties using the same number variable
        if currently_unchecked:
            # Use the same number variable for consistency
            num_to_select = min(num_to_change, len(currently_unchecked))
            
            if num_to_select > 0:
                specialties_to_select = random.sample(currently_unchecked, num_to_select)
                
                print(f"Selecting {num_to_select} new specialties (matching unchecked count): {specialties_to_select}")
                print(f"Total checked specialties will remain: {len(currently_checked)}")
                
                selected_specialties = []
                
                for i, index in enumerate(specialties_to_select):
                    checkbox = checkboxes.nth(index)
                    
                    # Human-like thinking delays
                    if i % 2 == 0:
                        time.sleep(random.uniform(1, 3)) # Longer pause every 2nd selection
                    else:
                        time.sleep(random.uniform(0.8, 2.0))
                    
                    # Hover over checkbox first
                    checkbox.hover()
                    time.sleep(random.uniform(0.3, 0.8))
                    
                    # Click checkbox to select
                    checkbox.click()
                    time.sleep(random.uniform(0.5, 1.0))
                    
                    specialty_name = specialty_names[index] if index < len(specialty_names) else f"Specialty {index+1}"
                    selected_specialties.append(specialty_name)
                    print(f"Selected: {specialty_name}")
                    
                    # Sometimes pause to "read" the specialty name
                    if random.random() < 0.3: # 30% chance
                        time.sleep(random.uniform(1, 2))
            else:
                print(f"No unchecked specialties available to select")
                selected_specialties = []

        # Save specialties
        time.sleep(random.uniform(3, 6))
        print("Saving specialties...")
        page.click('#button-actionbar-save')
        time.sleep(random.uniform(5, 10))
        
        # Update the tracking
        if currently_checked and currently_unchecked:
            unchecked_names = [specialty_names[i] for i in specialties_to_uncheck] if 'specialties_to_uncheck' in locals() else []
            selected_names = selected_specialties if 'selected_specialties' in locals() else []
            
            updated_fields['specialties'] = {
                "old": f"Unchecked: {', '.join(unchecked_names[:3])}",
                "new": f"Newly selected: {', '.join(selected_names[:3])}"
            }
        else:
            updated_fields['specialties'] = {
                "old": "No changes made",
                "new": "No changes made"
            }
        
        print(f"Successfully updated specialties for {username}")
        if 'selected_specialties' in locals():
            print(f"Newly selected specialties: {', '.join(selected_specialties)}")
        
    except Exception as e:
        print(f"Error updating specialties for {username}: {e}")
    
    return updated_fields

# Note on Top Specialties
def update_top_specialties(page, username: str) -> Dict[str, dict]:
    """
    Updates the top specialties section with AI-generated content.
    Returns a dict of updated fields.
    """
    updated_fields = {}
    
    try:
        # Navigate to top specialties page
        page.goto(WEBSITE_URL + "/profile/specialties-quote", timeout=60000)
        time.sleep(random.uniform(8, 15))  # Human-like page load wait
        
        # Human-like scrolling and reading behavior
        page.mouse.wheel(0, random.randint(200, 500))
        time.sleep(random.uniform(2, 4))
        
        # Retrieve current content from the top specialties textarea
        top_specialties_textarea = page.locator('textarea[id="specialties-quote"]')
        current_top_specialties = ""
        if top_specialties_textarea.count() > 0:
            current_top_specialties = top_specialties_textarea.input_value()
            print(f"Retrieved current top specialties content for {username}: {current_top_specialties}")
        
        # Generate AI content using the current content
        from app.services.ai_content import top_specialties_content
        ai_content = top_specialties_content(
            top_specialties=current_top_specialties
        )
        
        print(f"Generated AI content for top specialties: {ai_content}")
        
        # Fill the top specialties textarea with human-like typing
        if top_specialties_textarea.count() > 0:
            top_specialties_textarea.click()
            time.sleep(random.uniform(1, 3))
            
            # Clear existing content
            page.keyboard.press("Control+a")
            time.sleep(random.uniform(0.5, 1.5))
            page.keyboard.press("Backspace")
            time.sleep(random.uniform(1, 2))
            
            # Type with human-like delays
            for char in ai_content["top_specialties"]:
                page.keyboard.type(char)
                time.sleep(random.uniform(0.01, 0.05))  # Random typing speed
                
            updated_fields['top_specialties'] = {
                "old": current_top_specialties,
                "new": ai_content["top_specialties"]
            }
            print(f"Updated top specialties for {username}")
            
            time.sleep(random.uniform(3, 7))  # Think before saving
        
        # Human-like save behavior
        save_button = page.locator('#button-actionbar-save')
        if save_button.count() > 0:
            # Hover over save button first
            save_button.hover()
            time.sleep(random.uniform(1, 3))
            
            # Click save
            save_button.click()
            time.sleep(random.uniform(5, 10))  # Wait for save confirmation
            print(f"Saved top specialties for {username}")
            
    except Exception as e:
        print(f"Error updating top specialties for {username}: {e}")
    
    return updated_fields

def update_availability(page, username: str) -> Dict[str, dict]:
    """
    Updates the availability section by selecting one of the three radio button options.
    Returns a dict of updated fields.
    """
    updated_fields = {}
    
    try:
        # Navigate to availability page
        page.goto(WEBSITE_URL + "/profile/availability", timeout=60000)
        time.sleep(random.uniform(2, 4))
        
        # Define the three availability options
        availability_options = [
            "Both in person and online",
            "Online only"
        ]
        
        # First, check which option is currently selected
        currently_selected = None
        for option in availability_options:
            radio_button = page.locator(f'div[role="radio"][aria-label="{option}"]')
            if radio_button.count() > 0:
                aria_checked = radio_button.get_attribute("aria-checked")
                if aria_checked == "true":
                    currently_selected = option
                    print(f"Currently selected option for {username}: {currently_selected}")
                    break
        
        # Select a different option than the currently selected one
        if currently_selected:
            # Remove the currently selected option from available choices
            available_options = [opt for opt in availability_options if opt != currently_selected]
            selected_option = random.choice(available_options)
        else:
            # If no option is currently selected, choose any option
            selected_option = random.choice(availability_options)
        
        print(f"Selected availability option for {username}: {selected_option}")
        
        # Find and click the selected radio button
        radio_button = page.locator(f'div[role="radio"][aria-label="{selected_option}"]')
        if radio_button.count() > 0:
            # Human-like behavior: hover first, then click
            radio_button.hover()
            time.sleep(random.uniform(0.5, 1.5))
            
            # Click the radio button
            radio_button.click()
            time.sleep(random.uniform(1, 3))
            
            # Sometimes pause to "think" about the selection
            if random.random() < 0.3:  # 30% chance
                time.sleep(random.uniform(2, 4))
            
            updated_fields['availability_accepting'] = {
                "old": currently_selected,
                "new": selected_option
            }
            
            print(f"Successfully updated availability for {username} from '{currently_selected}' to: {selected_option}")
            
            # Save the selection
            time.sleep(random.uniform(3, 6))
            save_button = page.locator('#button-actionbar-save')
            if save_button.count() > 0:
                # Hover over save button first
                save_button.hover()
                time.sleep(random.uniform(1, 3))
                
                # Click save
                save_button.click()
                time.sleep(random.uniform(8, 10))  # Wait for save confirmation
                print(f"Saved availability for {username}")
        else:
            print(f"Could not find radio button for option: {selected_option}")
            
    except Exception as e:
        print(f"Error updating availability for {username}: {e}")
    
    return updated_fields

def update_additional_location(page, username: str) -> Dict[str, dict]:
    """
    Updates only the zip code in the additional location section with a randomly selected zip code.
    Returns a dict of updated fields.
    """
    updated_fields = {}
    
    try:
        # Navigate to additional location page
        page.goto(WEBSITE_URL + "/profile/additional-location", timeout=60000)
        time.sleep(random.uniform(2, 4))
        
        # Define zip codes for random selection
        zip_codes = [
            # Manhattan
            10003,  # East Village / Union Square
            10011,  # Chelsea / West Village
            10025,  # Upper West Side
            10009,  # Alphabet City / East Village
            10001,  # Hudson Yards / Midtown South
            10012,  # SoHo / NoHo / Greenwich Village
            10002,  # Lower East Side / Chinatown

            # Brooklyn
            11215,  # Park Slope
            11201,  # Brooklyn Heights / Downtown Brooklyn
            11211,  # Williamsburg
            11217,  # Boerum Hill / Gowanus
            11222,  # Greenpoint
            11231,  # Carroll Gardens / Red Hook
            11238,  # Prospect Heights / Crown Heights (West)

            # Queens
            11101,  # Long Island City
            11106,  # Astoria (Southwest)
            11377,  # Woodside (diverse, growing young population)
            11375,  # Forest Hills (more residential, still relevant)
            11385,  # Ridgewood (bordering Bushwick; growing with creatives)
            11369   # Jackson Heights (increasing mental health awareness)
        ]
        
        # Get current zip code first
        current_zip_input = page.locator('#postalCodeInput')
        if current_zip_input.count() > 0:
            current_zip = current_zip_input.input_value()
            print(f"Current zip code for {username}: {current_zip}")
            
            # Filter out the current zip code to avoid selecting the same one
            available_zip_codes = [zip_code for zip_code in zip_codes if str(zip_code) != current_zip]
            
            if available_zip_codes:
                # Randomly select a new zip code
                new_zip_code = random.choice(available_zip_codes)
                print(f"Selected new zip code for {username}: {new_zip_code}")
                
                # Click on the zip code input field
                current_zip_input.click()
                time.sleep(random.uniform(0.5, 1))
                
                # Clear the current zip code
                current_zip_input.fill("")
                time.sleep(random.uniform(0.3, 0.8))
                
                # Type the new zip code with human-like delays
                for char in str(new_zip_code):
                    current_zip_input.type(char)
                    time.sleep(random.uniform(0.01, 0.03))
                
                updated_fields['additional_location_zip'] = {
                    "old": current_zip,
                    "new": str(new_zip_code)
                }
                
                print(f"Successfully updated zip code for {username}: {current_zip} -> {new_zip_code}")
                
                # Save the location
                time.sleep(random.uniform(3, 6))
                save_button = page.locator('#button-actionbar-save')
                if save_button.count() > 0:
                    # Hover over save button first
                    save_button.hover()
                    time.sleep(random.uniform(1, 3))
                    
                    # Click save
                    print("clicking save")
                    save_button.click()
                    print("clicked save")
                    time.sleep(random.uniform(5, 10))  # Wait for save confirmation
                    print(f"Saved updated zip code for {username}")
                else:
                    print(f"Save button not found for {username}")
                
                # Refresh profile page after save (always, regardless of save button)
                page.goto(WEBSITE_URL + "/profile", timeout=60000)
                time.sleep(random.uniform(5, 7))  # Wait for page to load
            else:
                print(f"No different zip codes available for {username} (all zip codes are the same as current)")
        else:
            print(f"Zip code input field not found for {username}")
            page.goto(WEBSITE_URL + "/profile", timeout=60000)
            time.sleep(random.uniform(5, 7))  # Wait for page to load
            

            
    except Exception as e:
        print(f"Error updating zip code for {username}: {e}")
    
    return updated_fields


def update_my_identity(page, username: str) -> Dict[str, dict]:
    """
    Updates the identity section with race/ethnicity selections.
    Returns a dict of updated fields.
    """
    updated_fields = {}
    
    try:
        # Navigate to identity page
        page.goto(WEBSITE_URL + "/profile/identity", timeout=60000)
        time.sleep(random.uniform(2, 4))
        
        # Get all race/ethnicity checkboxes
        checkboxes = page.locator('div[role="checkbox"]')
        total = checkboxes.count()
        print(f"Total identity checkboxes found: {total}")

        # Get identity names for logging
        identity_names = []
        for i in range(total):
            try:
                checkbox = checkboxes.nth(i)
                aria_label = checkbox.get_attribute("aria-label")
                if aria_label:
                    identity_names.append(aria_label)
            except:
                pass

        # Uncheck all existing selections with human-like behavior
        print("Unchecking all existing identity selections...")
        for i in range(total):
            checkbox = checkboxes.nth(i)
            aria_checked = checkbox.get_attribute("aria-checked")
            if aria_checked == "true":
                # Hover over checkbox first
                checkbox.hover()
                time.sleep(random.uniform(0.3, 0.8))
                
                # Click checkbox
                checkbox.click()
                time.sleep(random.uniform(0.5, 1.5))
                
                # Sometimes pause longer (human thinking)
                if random.random() < 0.1:  # 10% chance
                    time.sleep(random.uniform(2, 4))

        # Select identities: 1 from first 9, 1 from next 8 (total 2 selections)
        time.sleep(random.uniform(3, 6))
        print("Selecting identity options...")
        
        selected_identities = []
        selected_indices = []
        
        # Select 1 from first 9 options (indices 0-8)
        if total >= 9:
            first_group_indices = list(range(9))
            first_selection = random.choice(first_group_indices)
            selected_indices.append(first_selection)
            print(f"Selected from first 9: index {first_selection}")
        elif total > 0:
            # If less than 9 options, select from available
            first_selection = random.randint(0, total - 1)
            selected_indices.append(first_selection)
            print(f"Selected from available {total}: index {first_selection}")
        
        # Select 1 from next 8 options (indices 9-16)
        if total >= 17:
            second_group_indices = list(range(9, 17))
            second_selection = random.choice(second_group_indices)
            selected_indices.append(second_selection)
            print(f"Selected from next 8: index {second_selection}")
        elif total > 9:
            # If between 9-16 options, select from remaining
            remaining_indices = list(range(9, total))
            second_selection = random.choice(remaining_indices)
            selected_indices.append(second_selection)
            print(f"Selected from remaining: index {second_selection}")
        
        print(f"Selected indices: {selected_indices}")
        
        # Process selections with human-like behavior
        for i, index in enumerate(selected_indices):
            checkbox = checkboxes.nth(index)
            aria_checked = checkbox.get_attribute("aria-checked")
            if aria_checked != "true":
                # Human-like thinking delays
                if i == 0:
                    time.sleep(random.uniform(2, 4))  # Longer pause for first selection
                else:
                    time.sleep(random.uniform(1.5, 3.0))  # Medium pause for second selection
                
                # Hover over checkbox first
                checkbox.hover()
                time.sleep(random.uniform(0.3, 0.8))
                
                # Click checkbox
                checkbox.click()
                time.sleep(random.uniform(0.5, 1.0))
                
                identity_name = identity_names[index] if index < len(identity_names) else f"Identity {index+1}"
                selected_identities.append(identity_name)
                
                # Sometimes pause to "read" the identity name
                if random.random() < 0.3:  # 30% chance
                    time.sleep(random.uniform(1, 3))

        # Save identity selections
        time.sleep(random.uniform(4, 7))
        print("Saving identity selections...")
        page.click('#button-actionbar-save')
        time.sleep(random.uniform(5, 10))
        
        updated_fields['identity'] = {
            "old": "Previous identity selections",
            "new": f"Updated to {len(selected_identities)} identity options: {', '.join(selected_identities)}"
        }
        
        print(f"Successfully updated identity for {username}")
        print(f"Selected identities: {', '.join(selected_identities)}")
        
    except Exception as e:
        print(f"Error updating identity for {username}: {e}")
    
    return updated_fields


# def update_specialties(page, username: str) -> Dict[str, dict]:
#     """
#     Updates the specialties section with random selections.
#     Returns a dict of updated fields.
#     """
#     updated_fields = {}
    
#     try:
#         # Navigate to specialties page
#         page.goto(WEBSITE_URL + "/profile/specialties", timeout=60000)
#         time.sleep(random.uniform(2, 4))
        
#         # Get all checkboxes
#         checkboxes = page.locator('div[role="checkbox"]')
#         total = checkboxes.count()
#         print(f"Total checkboxes found: {total}")

#         # Get specialty names for logging
#         specialty_names = []
#         for i in range(total):
#             try:
#                 checkbox = checkboxes.nth(i)
#                 specialty_text = checkbox.locator('xpath=..').text_content().strip()
#                 if specialty_text:
#                     specialty_names.append(specialty_text)
#             except:
#                 pass

#         # Uncheck all existing specialties with human-like behavior
#         print("Unchecking all existing specialties...")
#         for i in range(total):
#             checkbox = checkboxes.nth(i)
#             aria_checked = checkbox.get_attribute("aria-checked")
#             if aria_checked == "true":
#                 # Hover over checkbox first
#                 checkbox.hover()
#                 time.sleep(random.uniform(0.3, 0.8))
                
#                 # Click checkbox
#                 checkbox.click()
#                 time.sleep(random.uniform(0.5, 1.5))
                
#                 # Sometimes pause longer (human thinking)
#                 if random.random() < 0.1:  # 10% chance
#                     time.sleep(random.uniform(2, 4))

#         # Select random specialties
#         time.sleep(random.uniform(3, 6))
#         print("Selecting new specialties...")
#         num_to_select = random.randint(15, min(25, total))
#         indices = random.sample(range(total), num_to_select)
#         print(f"Randomly selected {num_to_select} specialties from {total} total specialties {indices}")

#         selected_specialties = []
#         for i, index in enumerate(indices):
#             checkbox = checkboxes.nth(index)
#             aria_checked = checkbox.get_attribute("aria-checked")
#             if aria_checked != "true":
#                 # Human-like thinking delays
#                 if i % 3 == 0:
#                     time.sleep(random.uniform(2, 4))  # Longer pause every 3rd selection
#                 else:
#                     time.sleep(random.uniform(0.8, 2.0))
                
#                 # Hover over checkbox first
#                 checkbox.hover()
#                 time.sleep(random.uniform(0.3, 0.8))
                
#                 # Click checkbox
#                 checkbox.click()
#                 time.sleep(random.uniform(0.5, 1.0))
                
#                 specialty_name = specialty_names[index] if index < len(specialty_names) else f"Specialty {index+1}"
#                 selected_specialties.append(specialty_name)
                
#                 # Sometimes pause to "read" the specialty name
#                 if random.random() < 0.2:  # 20% chance
#                     time.sleep(random.uniform(1, 3))

#         # Save specialties
#         time.sleep(random.uniform(4, 7))
#         print("Saving specialties...")
#         page.click('#button-actionbar-save')
#         time.sleep(random.uniform(5, 10))
        
#         updated_fields['specialties'] = {
#             "old": "Previous specialties",
#             "new": f"Updated to {num_to_select} specialties: {', '.join(selected_specialties[:5])}"
#         }
        
#         print(f"Successfully updated specialties for {username}")
#         print(f"Selected specialties: {', '.join(selected_specialties)}")
        
#     except Exception as e:
#         print(f"Error updating specialties for {username}: {e}")
    
#     return updated_fields
