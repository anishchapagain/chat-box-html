# WhatsApp Business API Integration - Q&A Help Guide

This document summarizes the steps and troubleshooting we performed to set up the WhatsApp ChatBot.

## 1. Access Tokens
**Q: What is the difference between a Temporary and Permanent token?**
*   **Temporary Token**: Generated on the "API Setup" page. Lasts only 24 hours. Good for initial testing.
*   **Permanent Token**: Generated via **Meta Business Settings > System Users**. It never expires. Requires assigning the App asset to the System User first.

## 2. Sending Messages
**Q: How do I send a message from Python?**
*   Use the `requests` library to POST to `https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages`.
*   Include the `Authorization: Bearer {TOKEN}` header.
*   **Templates**: Use `type: "template"` for the first message (e.g., `hello_world`).
*   **Free-text**: Use `type: "text"` to reply to a user who has messaged you in the last 24 hours.

## 3. Receiving Messages (Webhooks)
**Q: How do I receive messages in my script?**
1.  **Server**: Run a FastAPI/Flask server with a `GET` (for verification) and `POST` (for data) endpoint.
2.  **Public URL**: Use **ngrok** (`ngrok http 8000`) to expose your local server to Meta.
3.  **Configuration**: Set the Callback URL in Meta Dashboard (e.g., `https://xxx.ngrok-free.app/webhook`).
4.  **Subscription**: In Meta Dashboard, you **must** click "Manage" and subscribe to the `messages` field.

## 4. Troubleshooting Delivery
**Q: Why did Meta say "Success" but I didn't receive the message?**
*   Check your **Status Updates** in the Webhook. Meta sends a notification when a message is `sent`, `delivered`, `read`, or `failed`.
*   **Error 131031 (Business Account locked)**: Meta has restricted the account. Usually requires adding a payment method or reviewing an alert in the **WhatsApp Manager**.
*   **24-Hour Window**: You can only send free-text replies if the user has messaged your business number in the last 24 hours.

## 5. Development Tips
**Q: Do I need to "Publish" the app to test?**
*   No. You can test in "Development" mode as long as you use the **verified phone numbers** you added in the "API Setup" > "To" field.

## 6. Key IDs to Remember
*   **App ID**: Your unique Facebook App identifier.
*   **Phone Number ID**: Identifies the sender number in the API.
*   **WABA ID**: WhatsApp Business Account ID (for higher-level settings).
*   **Verify Token**: A secret string you create to secure your Webhook verification.


--- 📨 NEW MESSAGE FROM 9779840065449 ---
💬 Body: 'Where is my reply?'
🚀 Sending reply...
✅ Reply accepted by Meta. ID: wamid.HBgNOTc3OTg0MDA2NTQ0ORUCABEYEjQyNjBCMkNBMkJFRTNDMzEyNQA=
INFO:     2a03:2880:10ff:51:::0 - "POST /webhook HTTP/1.1" 200 OK
📊 Status Update: Message to 9779840065449 is now 'failed'
❌ Delivery Failed: Business Account locked (Code: 131031)
INFO:     2a03:2880:10ff:59:::0 - "POST /webhook HTTP/1.1" 200 OK


We found the problem!

Error 131031: Business Account locked means Meta has temporarily restricted your WhatsApp Business Account. This is common when first setting up a permanent system user.

How to unlock it:
Go back to your Facebook Developer Dashboard.
At the top of the page, you likely see a red or yellow banner that says "You have alerts that need review" or "Go to WhatsApp Manager".
Click that link to go to the WhatsApp Manager.
Look for a section called "Account Issues" or "Account Status".
Common reasons it's locked:
Payment Method: Even though you are in the "Free Tier," Meta often requires you to add a credit card to the "Business Account" to verify you are a real business. (You won't be charged for the first 1,000 messages per month).
Onboarding: You might need to click a "Finish Setup" button to accept the latest Terms of Service.
Business Verification: Sometimes they just need you to confirm your email or business name.
You have succeeded in the technical part!
Your code is perfect, your webhook is live, and your token is valid. The only thing stopping you now is Meta's "Account Review."

Once you resolve the alert in the WhatsApp Manager, your bot will immediately start sending those "Beep Boop" replies without any changes to your code!

Do you see any specific alert or "Review" button in your WhatsApp Manager?

5:18 PM
Save our current conversations with Q and A, as help.md inside ChatBotWhats
I have saved our full integration journey as 
help.md
 inside your ChatBotWhats directory. This covers everything from Token types to the "Business Account Locked" error we just solved.

Summary of what we did today:
Navigated the Dashboard: Found the WhatsApp product and the API Setup page.
Built the Client: Created test_whatsapp.py to prove we could talk to the API.
Built the Server: Created webhook_server.py to listen for your messages.
Secured the Connection: Moved from a 24-hour token to a Permanent System User Token.
Identified the Blocker: Used Status Tracking to find that your Business Account is currently locked (Error 131031).
Next Step: Visit your WhatsApp Manager in the Facebook Dashboard to resolve the account alert. Once that is green, your bot will start replying immediately!

Do you have any other questions, or should I leave you to fix the Meta account alerts?