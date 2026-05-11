Feature: Stock Monitoring, Alerts and Authentication — TRT Invest
  The goal of this feature is to validate that the TRT Invest system
  correctly monitors stock prices, generates alerts when thresholds are
  exceeded, delivers push notifications via ntfy.sh, prevents duplicate
  alerts, and authenticates users securely.

  # REQ links: REQ-1, REQ-2, REQ-7, REQ-8, REQ-9, REQ-13, REQ-15

  # ─────────────────────────────────────────────
  # HAPPY PATH scenarios
  # ─────────────────────────────────────────────

  Scenario: Happy path — Add a valid US stock to the portfolio
    # REQ-1 (AC-1, AC-2, AC-5)
    Given the user is authenticated
    And the stock "AAPL" does not exist in the portfolio
    When the user submits the add stock form with symbol "AAPL" and type "stock_us"
    Then the stock "AAPL" appears in the portfolio list with status "Ativa"
    And the stock name is automatically filled from yfinance as "Apple Inc."
    And the record is persisted in the database after a server restart

  Scenario: Happy path — Push notification sent when price threshold is exceeded
    # REQ-7 (AC-1, AC-2, AC-3, AC-4), REQ-4
    Given the user has configured ntfy_topic as "trt-test-topic"
    And the stock "AAPL" has threshold_high set to "1.0" percent
    And the last recorded price for "AAPL" is "100.00"
    When the monitoring cycle runs and the new price for "AAPL" is "102.50"
    Then an Alert record is created with direction "high" and variation "+2.50%"
    And an HTTP POST is sent to "https://ntfy.sh/trt-test-topic"
    And the notification title contains "TRT Alerta - AAPL Alta"
    And the notification priority is "high"
    And "alert.email_sent" is set to True

  Scenario: Happy path — Alert history is accessible and complete
    # REQ-9 (AC-1, AC-2, AC-3)
    Given the user is authenticated
    And at least one alert exists with stock "AAPL", direction "high", variation "2.50", price "155.00"
    When the user navigates to "/alerts/"
    Then the page loads with HTTP status 200
    And the alert table displays the entry with symbol "AAPL", direction "Alta", variation "+2.50%", price "155.00"
    And each entry includes a timestamp

  Scenario: Happy path — Login using email address instead of username
    # REQ-15 (AC-2)
    Given a user account exists with username "levi" and email "levi@mail.com"
    When the user submits the login form with identifier "levi@mail.com" and password "pass1234"
    Then the user is authenticated successfully
    And the user is redirected to "/"
    And a session cookie is created

  # ─────────────────────────────────────────────
  # ALTERNATIVE FLOW scenarios
  # ─────────────────────────────────────────────

  Scenario: Alternative flow — Duplicate alert allowed after 60-minute window expires
    # REQ-8 (AC-3)
    Given the stock "AAPL" has threshold_high set to "1.0" percent
    And an alert with direction "high" for "AAPL" was created "61" minutes ago
    And the user has configured ntfy_topic as "trt-test-topic"
    When the monitoring cycle runs and the new price variation for "AAPL" is "+2.0%"
    Then "already_alerted()" returns False
    And a new Alert record is created with direction "high" for "AAPL"
    And a new push notification is sent to "https://ntfy.sh/trt-test-topic"

  Scenario: Alternative flow — No price stored when API returns fallback value
    # REQ-2 (fallback), REQ-13 (AC-3)
    Given the yfinance API fails for all 3 attempts for stock "AAPL"
    And the last recorded StockPrice for "AAPL" is "148.00"
    When the monitoring cycle runs for "AAPL"
    Then "fetch_price('AAPL')" returns None
    And the system uses the last recorded price "148.00" as fallback
    And the result contains "fallback: True"
    And no new StockPrice record is created for "AAPL"

  Scenario: Alternative flow — Guest user can access portfolio without registration
    # REQ-15 (AC-3)
    Given the user is not authenticated
    When the user navigates to "/guest/"
    Then the "visitante" account is created or retrieved automatically
    And the user is authenticated as "visitante"
    And the user is redirected to "/"

  # ─────────────────────────────────────────────
  # NEGATIVE / ERROR PATH scenarios
  # ─────────────────────────────────────────────

  Scenario: Negative — Reject adding a duplicate stock symbol
    # REQ-1 (AC-3)
    Given the user is authenticated
    And the stock "AAPL" already exists in the portfolio
    When the user submits the add stock form with symbol "AAPL" and type "stock_us"
    Then the form submission is rejected
    And the error message "AAPL já está na lista." is displayed
    And no duplicate record is created in the database

  Scenario: Negative — No notification sent when ntfy_topic is empty
    # REQ-7 (AC-5)
    Given "UserSettings.ntfy_topic" is empty
    And the stock "TSLA" has threshold_high set to "1.0" percent
    And the new price variation for "TSLA" is "+3.0%"
    When "send_ntfy_notification(alert, settings)" is called
    Then the function returns immediately without making any HTTP request
    And "alert.email_sent" remains False
    And no exception is raised

  Scenario: Negative — Duplicate push notification blocked within 60 minutes
    # REQ-8 (AC-1, AC-2)
    Given the stock "AAPL" has threshold_high set to "1.0" percent
    And an alert with direction "high" for "AAPL" was already sent "30" minutes ago
    When the monitoring cycle runs and the new price variation for "AAPL" is "+2.0%"
    Then "already_alerted()" returns True
    And "check_and_alert()" returns None
    And no new Alert record is created for "AAPL"
    And no HTTP POST is sent to ntfy.sh

  Scenario: Negative — Login rejected with incorrect password
    # REQ-15 (AC-1)
    Given a user account exists with username "levi"
    When the user submits the login form with identifier "levi" and password "wrongpassword"
    Then the user remains unauthenticated
    And the page stays on "/login/"
    And the error message "Utilizador ou password incorretos." is displayed

  Scenario: Negative — Monitoring interval outside valid range is rejected
    # REQ-3 (AC-3)
    Given the user is authenticated and on the settings page "/settings/"
    When the user submits the settings form with monitoring_interval "0"
    Then the form is rejected with error "Entre 1 e 3600 segundos."
    And the UserSettings record is not updated
    When the user submits the settings form with monitoring_interval "3601"
    Then the form is rejected with error "Entre 1 e 3600 segundos."

  # ─────────────────────────────────────────────
  # NFR / BOUNDARY scenarios
  # ─────────────────────────────────────────────

  Scenario: Boundary — Monitoring interval accepts minimum and maximum valid values
    # REQ-3 (AC-1, AC-3)
    Given the user is authenticated and on the settings page "/settings/"
    When the user submits the settings form with monitoring_interval "1"
    Then the form is accepted with message "Configurações guardadas!"
    And UserSettings.monitoring_interval is saved as "1"
    When the user submits the settings form with monitoring_interval "3600"
    Then the form is accepted with message "Configurações guardadas!"
    And UserSettings.monitoring_interval is saved as "3600"

  Scenario: NFR — API retries exactly 3 times before returning None
    # REQ-2, REQ-13 (AC-1, AC-2)
    Given the yfinance API raises an exception on every call for stock "MSFT"
    And no StockPrice record exists for "MSFT"
    When "fetch_price('MSFT')" is called
    Then the function attempts exactly 3 calls to yfinance
    And the function returns None after all 3 attempts fail
    And a warning is logged for each failed attempt
