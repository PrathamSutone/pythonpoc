import base64, openai
from utils import encode_image
import os
import time

from playwright.sync_api import sync_playwright
client = openai.Client()

def take_screenshot(url, output_path, device):
    """Take a screenshot of the specified URL."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(url, timeout=60000)  # Wait up to 60 seconds for the page to load
            page.wait_for_load_state("networkidle")  # Wait for the page to fully load
            # Optional: Check for the selector if it's necessary
            # if not page.query_selector("main"):
            #     print("'main' selector not found. Proceeding with the screenshot.")
            # #Rename old screenshot based on timestamp old name is screenshot.png
            # Rename old screenshot based on timestamp if it exists
            if os.path.exists(output_path):
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                os.rename(output_path, f"{output_path}-{timestamp}.png")

            if device == "mobile":
                page.set_viewport_size({"width": 375, "height": 812})
            elif device == "tablet":
                page.set_viewport_size({"width": 1024, "height": 1366})
            else:
                page.set_viewport_size({"width": 1920, "height": 1080})
            page.screenshot(path=output_path, full_page=True)
            print(f"Screenshot saved to {output_path}")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            browser.close()

def get_ui_feedback(screenshot_path, design_image_path):
    """Use GPT-4 Vision to analyze the UI and provide feedback."""
    try:
        response = client.chat.completions.create(
        model="gpt-4o", 
        messages=[
            {"role": "user", 
             "content":  [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encode_image(design_image_path)}"}},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encode_image(screenshot_path)}"}},
                {"type": "text", "text": "Given the design (1st) and the code's output(2nd), Let's analyze the images step by step: 1. First, identify all distinct objects in the code's output and the design 2. For each object, describe its location relative to frame boundaries 3. Note the size of each object compared to others 4. Describe spatial relationships between objects 5. Based on this analysis, what can we fix in the code's output for it to better match the design."}
            ]},
        ],
        )
        result = response.choices[0].message.content
        print(result)
        return result
    except Exception as e:
        #logging.error(f"Error getting UI feedback: {e}")
        raise

def test_UI(url, screenshot_path, device):
    """Test the UI generated by the code."""
    take_screenshot(url, screenshot_path, device)
    return get_ui_feedback(screenshot_path, "./reference/reference.png")


if __name__ == "__main__":
    #feedback = test_UI("http://localhost:3000/playground", "screenshot.png")
    take_screenshot("http://localhost:3000/playground", "screenshot-test.png", "mobile")
    #print(feedback)

