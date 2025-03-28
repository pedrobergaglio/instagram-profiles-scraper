# Plan

# Objective

Develop a robust and scalable Instagram scraper to extract contact information from the followers of specified Instagram business accounts. This tool will be used internally to gather potential customer data.

# Implementation Priority:

1. Set up SQLAlchemy database integration
2. Implement basic Streamlit UI
3. Add parallel processing with account rotation
4. Implement data validation
5. Add progress tracking and watchdog
6. Integrate AI filtering system

### Testing Strategy:

Write unit tests for each component

Create integration tests

Set up CI/CD pipeline

# Core Requirements

1.  **Error Handling and Robustness:**

    * Write comprehensive unit tests to cover all potential error scenarios during the scraping process. This includes network errors, Instagram API changes, invalid user inputs, and rate limiting.

    * Implement error handling to gracefully manage these scenarios without crashing. Log errors with sufficient detail for debugging.

    * Develop a robust error recovery strategy:

        * Implement a mechanism to track progress and resume scraping from the last successfully scraped point if an error occurs (e.g., account blocked temporarily). This should persist across restarts.

        * Define a retry mechanism with exponential backoff and jitter to handle temporary issues like network errors or rate limits.

        * Implement a watchdog timer to monitor the main scraping process and automatically restart it if it becomes unresponsive.

    * Incorporate data validation checks to ensure the integrity of scraped data. This includes:

        * Verifying the format of email addresses and phone numbers.

        * Checking for duplicate entries.

        * Ensuring that scraped profiles are indeed business accounts (to the extent possible).

2.  **Rate Limiting Scraping:**

    * Implement delays (time.sleep) between requests to simulate human behavior and avoid triggering Instagram's rate limits. The delays should be configurable.

    * The scraper implements backoff strategies but may still hit limits, we want to avoid this to happen.

3.  **Functionality:**

    * Scraping Scope:

        * The scraper should ONLY target the *followers* of a given Instagram business account.

        * Exclude scraping data from:

            * Following lists.

            * Private accounts.

            * Media content (posts, stories, etc.).

    * Data Extraction:

        * Extract all the data, but remove the columns as in @cleaner.py

        * Store all extracted profile data, even if some fields are empty.

    * Filtering:

        * Apply hardcoded rules and integrate with an AI model (details below) to analyze the scraped data and filter potential customers.

        * The user should be able to provide guidelines or criteria for the AI to use during the filtering process (e.g., "Look for profiles in the marketing industry," "Prioritize accounts with more than 1000 followers").

    * Status Tracking:

        * Maintain a status for each scraped profile in the database (e.g., "Pending," "Contacted," "Not Interested," "Error").

        * Display this status in the UI.

4.  **Software Architecture:**

    * UI Framework:

        * Develop a user interface using Streamlit.

        * The UI should be part of the same service/application, not separated.

        * The UI should allow users to:

            * Manage scraping jobs: start, stop, and monitor progress.

            * Manage and monitor Instagram account credentials for scraping. Support the use of multiple accounts for parallel processing.

            * View the scraped data in a table or dashboard, with the ability to filter and sort based on status and other criteria.

    * Instagram Library:

        * Use a modified version of the instapy library. The code will reside in a local folder, not installed from pip. This is necessary to implement custom delays and other modifications.

    * Data Storage:

        * Store all scraped data in a MySQL database.

        * The user will provide the necessary credentials to connect to the database.

        * The database schema should include:

            * All extracted profile data as columns.

            * A "status" column to track the contact status.

            * A boolean column indicating whether the profile was filtered in or out by the system.

5.  **Parallel Processing:**

    * Implement parallel processing to scrape data from multiple Instagram accounts concurrently.

    * The system should manage the distribution of scraping tasks across these accounts.

    * Implement a mechanism to handle account blocks or other issues that may arise with individual accounts without halting the entire process.

# Clarifications and Assumptions:

* **Testing:** I will write unit tests using Python's `unittest` or `pytest` framework. These tests will cover the core scraping logic, error handling, and data validation. I will also include integration tests to ensure that the different components of the system (scraper, database, UI) work together correctly.

* **Sleep Implementation:** I will use `time.sleep()` with configurable delays at various points in the scraping process, such as between requests for different followers, between different pages of followers, and after encountering errors. I will also add jitter to the delays to make the scraping behavior appear more human-like.

* **Instagpy Modification:** I understand that the `instagpy` library will be modified locally. I will ensure that these modifications (primarily related to adding delays) are implemented in a way that does not break the library's core functionality and are well-documented.

* **UI Architecture:** I understand that the Streamlit UI will be part of the same application. This simplifies deployment but may impact scalability for very large workloads. I will design the application with modularity in mind to facilitate future scaling if needed.

* **Data Storage:** I will use a library like `SQLAlchemy` to interact with the MySQL database. This will provide an abstraction layer and make it easier to manage database operations.

* **AI Integration:** The prompt mentions using AI for filtering, but the specifics are vague. I assume that a separate AI model or service will be used. I will need more information about the AI model's API, input/output format, and filtering criteria to integrate it effectively. I will design the scraper to be modular, so it can be easily integrated with different AI models. I will add a placeholder for this functionality, and implement the data passing.

* **Error Recovery:** I will implement a robust error recovery strategy that includes:

    * Logging: Detailed logging of all errors and warnings.

    * Retry mechanism: Automatic retries with exponential backoff and jitter for transient errors.

    * Progress tracking: Storing the last successfully scraped user and offset in the database to resume after an interruption.

    * Watchdog timer: A separate thread to monitor the main scraping process and restart it if it becomes unresponsive.

* **Data Validation:** I will implement data validation checks using regular expressions and other techniques to ensure data quality.

* **Backoff Strategies**: I will implement backoff strategies using a combination of  `time.sleep()` and retry logic. The goal is to avoid hitting rate limits by progressively increasing the delay between requests.

* **Parallel Processing**: I will use Python's `threading` or `asyncio` to implement parallel processing. Each thread or coroutine will handle the scraping process for one Instagram account.

# Doubts and Further Questions:

* What are the specific hardcoded rules for filtering potential customers? For now lets just create a mockup function for future further development, there we will first filter by hardcoded rules, and then show the info to an LLM to decide if the customer is of our interest or not.

* The performance requirements for the scraper: maintain 2 scraped profiles per minute with a perfect robustesness would be perfect.

* Expected behavior when an account is blocked, the scraper should:

    * Temporarily stop scraping with that account and move to the next, marking it as blocked

* Desired frequency for saving progress:

    * After scraping each user