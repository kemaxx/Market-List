# Zecool Hotels Monthly Market Bulk Purchase Prediction

## Project Overview

- **Author:** Kenneth Mark
- **Position:** Storekeeper
- **Location:** Zecool Hotels, Barnawa, Kaduna, Nigeria
- **Project Start Date:** November 20, 2023

## Project Description

The Zecool Hotels Monthly Market Bulk Purchase Prediction project, initiated by Kenneth Mark, aims to streamline the stock procurement process by predicting optimal quantities for the monthly market bulk purchase. Leveraging historical data and advanced analytics, the project assists in making informed decisions to maintain sufficient stock levels while minimizing excess inventory.

## Dependencies

The project relies on the following Python libraries and versions:

- cachetools==5.3.2
- certifi==2023.11.17
- charset-normalizer==3.3.2
- google-auth==2.23.4
- google-auth-oauthlib==1.1.0
- gspread==5.12.0
- idna==3.6
- numpy==1.26.2
- oauthlib==3.2.2
- pandas==2.1.3
- pyasn1==0.5.1
- pyasn1-modules==0.3.0
- python-dateutil==2.8.2
- pytz==2023.3.post1
- requests==2.31.0
- requests-oauthlib==1.3.1
- rsa==4.9
- six==1.16.0
- tzdata==2023.3
- urllib3==2.1.0

## Usage Instructions

1. **Google Sheets Credentials:**
   - Ensure that the Google Sheets service account credentials are securely set as the `STEAM_TALENT_SERVICE_ACCOUNT` environment variable.

2. **Running the Script:**
   - Execute the script to generate predictions for the monthly market bulk purchase.
   - The script retrieves and processes data from Google Sheets, calculates moving averages, and provides recommendations based on historical usage patterns.

3. **Reviewing Output:**
   - The output will be printed to the console, displaying the recommended quantities to purchase for various items.

## Notes and Recommendations

- **Confidentiality:**
  - Keep the service account credentials (`STEAM_TALENT_SERVICE_ACCOUNT`) confidential and avoid exposing them publicly.

- **Customization:**
  - Adjust the `x_days_period` parameter in the `create_market_list` function to customize the prediction period according to your specific requirements.

## Contact Information

For any inquiries, assistance, or feedback related to this project, please contact Kenneth Mark.

---

**Note:** This documentation serves as a guide for users and collaborators involved in the Zecool Hotels Monthly Market Bulk Purchase Prediction project.
