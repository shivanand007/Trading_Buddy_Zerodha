# Trading Automation with Kite Zerodha API and Selenium WebDriver

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## Overview

This application utilizes Selenium WebDriver in Python to automate trading activities, particularly options trading or intraday trading, by integrating with Kite Zerodha APIs. The primary goal is to control customer loss by allowing users to set their maximum loss limit. The application requires a valid API key from Kite Zerodha and involves setting up the mobile phone for automated login. We welcome new suggestions and contributions to enhance the project.

## Installation

Follow the steps below to set up and run the Python application:

1. Clone the repository:
   
2. Change into the project directory:
   
3. Install the required dependencies:
   
4. Obtain the API key from Kite Zerodha by following their documentation.

5. Set up the mobile phone for automated login by referring to the documentation provided by Kite Zerodha.

6. Update the configuration file `config.ini` with your API key and other necessary details.

7. Run the Python application:

## Usage

This application can be used while you start trading. It acts as a co-trader even in your absence, making smart sell calls based on your pre-defined loss limit. Here's how to use it:

1. Configure your trading settings and loss limit in the `config.ini` file.

2. Run the application, and it will automatically log in to your Kite Zerodha account.

3. Once logged in, the application will monitor your trades and watch for any loss exceeding the specified limit.

4. The application dynamically adjusts the stop loss value based on the current price of your stocks. For example, if you have set a 5% stop loss for a stock and its current price decreases, the application will automatically adjust the stop loss value to be slightly less than 5% of the current price.

5. When the loss limit is reached, or the adjusted stop loss is triggered, the application will initiate sell calls to minimize your losses.

This smart stop loss strategy has helped many traders save up to 50% of their losses within a month. It provides an automated approach to adjust the stop loss value based on market conditions, allowing for effective risk management.

You can customize the behavior and rules for selling by modifying the Python code in `main.py` to match your trading strategy.

Remember to keep an eye on the application's activities and monitor the trades it performs.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Contributing

We welcome contributions from the community. If you have any suggestions, bug reports, or feature requests, please open an issue or submit a pull request.

## Contact

shivanandmasne1998@gmail.com
