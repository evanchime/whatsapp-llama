# WhatsApp Llama

Welcome to WhatsApp Llama! This project aims to create a AI chat bot application on WhatsApp.

## Features

- Real-time messaging
- Remembers previous conversation

## Getting Started with WhatsApp Business Cloud API

First, open the [WhatsApp Business Platform Cloud API Get Started Guide](https://developers.facebook.com/docs/whatsapp/cloud-api/get-started#set-up-developer-assets) and follow the first four steps to:

1.  Add the WhatsApp product to your business app;
2.  Add a recipient number;
3.  Send a test message;
4.  Configure a webhook to receive real time HTTP notifications. For this step, follow `How to Set Up the Webhook` below

## Installation

1. Clone the repository: `git clone https://github.com/evanchime/whatsapp-llama.git`
2. Install the dependencies: `pip install requests flask langchain python-dotenv`
3. Start the application: `flask --app main run --port 5000` 
4. If successful you should see a message that reads: `* Running on http://127.0.0.1:5000`
5. Run `ngrok http 5000` to obtain a URL that maps to your application. Copy the link

## How to Set Up the Webhook

1.  In your developer account on Meta for Developers, click the Configuration menu under WhatsApp in the left navigation pane.
2.  In the Webhook card, click Edit.
3.  Then, in the Callback URL field of the dialog that opens, paste the copied URL from `Installation` step 5, and append /webhook to it.
4.  Add the meta token into the Verify token field. Click Verify and save to close the dialog.
5.  Now, from the same card, click Manage and check the messages field. The webhook is now ready

## Contributing

Contributions are welcome! If you'd like to contribute to WhatsApp Llama, please follow these steps:

1. Fork the repository
2. Create a new branch: `git checkout -b feature/your-feature`
3. Make your changes and commit them: `git commit -m 'Add your feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Submit a pull request

## License

This project is licensed under the MIT License. See the LICENSE file for more information.

## Contact

If you have any questions or suggestions, feel free to reach out to us at evanchime@yahoo.co.uk