# Event Horizon Testing

This document records the testing carried out for Event Horizon.

Testing combines automated Django tests with manual browser-based testing. Automated tests cover repeatable backend behaviour, authentication, booking rules, Stripe boundaries and webhook handling. Manual testing covers complete user journeys, administrator functionality, visual behaviour, validation, responsiveness, accessibility and external-service behaviour that cannot be fully demonstrated through unit tests alone.

Testing results in this document reflect tests that were actually carried out. Items that have not yet been tested, such as final production deployment checks and event-image verification, are clearly marked as pending.

---

## Table of Contents

- [Automated Testing](#automated-testing)
- [Manual Testing](#manual-testing)
  - [A. Authentication](#a-authentication)
  - [B. Navigation, Search and Event Discovery](#b-navigation-search-and-event-discovery)
  - [C. Booking Flow and Capacity](#c-booking-flow-and-capacity)
  - [D. Payment, Confirmation and Cancellation](#d-payment-confirmation-and-cancellation)
  - [E. Administrator Functionality](#e-administrator-functionality)
  - [F. Validation, Feedback and Error Handling](#f-validation-feedback-and-error-handling)
  - [G. Responsive Design, Accessibility, Static Files and Media](#g-responsive-design-accessibility-static-files-and-media)
- [Issues Identified and Regression Tested](#issues-identified-and-regression-tested)
- [Pending Testing](#pending-testing)
- [Testing Summary](#testing-summary)

---

# Automated Testing

Automated tests are implemented in the `tests.py` files for the `home`, `profiles`, `events` and `bookings` apps.

The suite uses Django's `TestCase` together with `unittest.mock.patch` where external Stripe and email behaviour needs to be isolated. This allows payment, refund, webhook and failure-handling behaviour to be tested without contacting Stripe, creating real charges or relying on an external email provider during the automated test run.

The full suite can be run with:

```bash
python manage.py test
```

Latest verified result:

```text
Ran 54 tests

OK
```

All **54 automated tests passed**.

| App        |  Tests | Areas Covered                                                                                                                                                                                                                                                                                                  |
| ---------- | -----: | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `home`     |      4 | Home page rendering, active and upcoming event filtering, featured-event limits and About page rendering.                                                                                                                                                                                                      |
| `profiles` |      9 | Registration, required email validation, anonymous-only login and registration access, protected profiles, booking ownership, profile updates and password changes.                                                                                                                                            |
| `events`   |     17 | Model behaviour, capacity calculations, event discovery, inactive-event handling, booking access, sold-out behaviour, booking ownership, cancellation/refund handling, graceful email failure handling, idempotent cancellation refunds and minimum booking-quantity enforcement.                              |
| `bookings` |     24 | Stripe Checkout validation and failure handling, quantities and capacity, reversed absolute URLs, booking-confirmation ownership and processing states, webhook validation, refund handling, missing-user/event recovery, duplicate and concurrent webhook protection and confirmation-email failure handling. |
| **Total**  | **54** | **Core application, authentication, booking, payment, refund, webhook, failure-recovery and data-integrity behaviour.**                                                                                                                                                                                        |

## Automated Test Coverage

The automated suite verifies behaviour including:

* public home and About page rendering;
* upcoming and active event filtering;
* featured-event limits;
* registration page access;
* authenticated-user redirects away from login and registration;
* required registration email validation;
* valid user registration;
* protected profile access;
* profile booking ownership;
* profile email updates;
* password changes while preserving the session;
* category and event string representations;
* booked and remaining capacity calculations;
* confirmed bookings being counted while cancelled bookings are excluded;
* booking total-price calculation;
* database enforcement preventing zero-quantity bookings;
* active-only event listings;
* search by event name, description, location and category;
* category filtering;
* inactive event 404 handling;
* authenticated booking access;
* sold-out booking prevention;
* GET-only booking-form behaviour;
* prevention of access to another user's cancellation route;
* successful refund and booking cancellation;
* graceful handling of cancellation email failures;
* deterministic Stripe idempotency keys for cancellation refunds;
* safe cancellation retry when Stripe has refunded but the local booking update initially fails;
* authenticated access to Stripe Checkout;
* invalid, zero, negative and malformed checkout quantities;
* requests above remaining event capacity;
* missing customer email handling;
* valid Stripe Checkout Session creation;
* graceful handling of Stripe Checkout Session creation failures;
* reversed absolute success and cancellation URLs;
* booking-success session requirements;
* booking-confirmation ownership;
* delayed webhook handling after a successful Stripe redirect;
* separate confirmed, processing and cancelled/refunded booking-success states;
* malformed Stripe webhook payloads;
* invalid Stripe webhook signatures;
* ignored unrelated webhook event types;
* ignored unpaid checkout sessions;
* successful paid booking creation;
* graceful handling of booking-confirmation email failures;
* duplicate webhook protection;
* concurrent duplicate webhook protection after acquiring the event lock;
* webhook-side capacity enforcement;
* automatic refunds when capacity becomes unavailable after payment;
* retry-safe refunds when an automatic capacity refund temporarily fails;
* automatic refunds when the booking user no longer exists;
* automatic refunds when the referenced event becomes unavailable;
* confirmation email triggering only for successfully fulfilled bookings.

## Stripe Mocking

External Stripe calls are mocked during automated testing.

This allows the application to verify what would be sent to Stripe and how simulated Stripe responses are handled while ensuring the test suite:

* does not create real payments;
* does not issue real refunds;
* does not require network access;
* does not rely on a live Stripe account;
* can reliably reproduce success, failure and retry scenarios;
* can verify Stripe idempotency keys without creating duplicate refund operations.

Manual Stripe testing is also carried out separately using Stripe's test environment.

---

# Manual Testing

Manual testing was carried out using the local development application. Tests were performed through the browser using realistic visitor, registered-user and administrator journeys.

Each result below records:

- the action tested;
- the expected result;
- the observed result;
- the final status.

A total of **64 completed manual checks currently pass**. One media-related check remains pending because final event images have not yet been uploaded.

---

## A. Authentication

| ID | Test | Expected Result | Actual Result | Status |
|---|---|---|---|:---:|
| A1 | Open the login page while logged out. | Login form displays normally. | Login page loaded correctly. | Pass |
| A2 | Open the registration page while logged out. | Registration form displays normally. | Registration page loaded correctly. | Pass |
| A3 | Submit registration without an email address. | Registration is rejected and email validation is shown. | Form remained on the page and required-email validation appeared. | Pass |
| A4 | Register a valid new account. | Account is created and user is redirected to login. | Account was created and login page was shown. | Pass |
| A5 | Log in with the new account. | Login succeeds and user is redirected to the homepage. | Login completed successfully. | Pass |
| A6 | While logged in, manually open the login URL. | Authenticated user is redirected home. | User was redirected to the homepage. | Pass |
| A7 | While logged in, manually open the registration URL. | Authenticated user is redirected home. | User was redirected to the homepage. | Pass |
| A8 | While logged out, manually open the profile URL. | User is redirected to login. | Protected profile redirected to login. | Pass |
| A9 | Log in and use Logout. | Session ends and anonymous state is restored. | Logout completed correctly. | Pass |

**Authentication result: 9/9 passed.**

---

## B. Navigation, Search and Event Discovery

| ID | Test | Expected Result | Actual Result | Status |
|---|---|---|---|:---:|
| B1 | Open the homepage. | Homepage loads with featured/upcoming events. | Homepage loaded correctly with event content. | Pass |
| B2 | Use navigation to open the event catalogue. | Event list loads correctly. | Event catalogue opened successfully. | Pass |
| B3 | Open the About page. | About page loads normally. | About page loaded correctly. | Pass |
| B4 | Search for an event by name. | Matching event appears. | Matching event was returned. | Pass |
| B5 | Search using a description keyword. | Matching event appears. | Matching event was returned. | Pass |
| B6 | Search by location. | Matching event appears. | Matching event was returned. | Pass |
| B7 | Search by category name. | Matching event appears. | Matching event was returned. | Pass |
| B8 | Filter the catalogue by category. | Only events from the selected category are shown. | Category filtering worked correctly. | Pass |
| B9 | Search for a value with no matches. | A sensible empty-results state appears without an error. | Empty-results state displayed correctly. | Pass |
| B10 | Open an active event from the catalogue. | Correct event detail page loads with availability information. | Correct event detail page loaded. | Pass |

**Navigation, search and discovery result: 10/10 passed.**

---

## C. Booking Flow and Capacity

| ID | Test | Expected Result | Actual Result | Status |
|---|---|---|---|:---:|
| C1 | While logged out, click Book Now. | User is redirected to login. | Login redirect occurred. | Pass |
| C2 | While logged in, open Book Now for an available event. | Booking form loads. | Booking form loaded correctly. | Pass |
| C3 | Enter quantity `0`. | Booking is rejected and Stripe does not open. | User was returned to the event page and Stripe did not open. | Pass |
| C4 | Enter a negative quantity. | Booking is rejected and Stripe does not open. | Invalid quantity was rejected. | Pass |
| C5 | Enter a quantity above remaining capacity. | Booking is rejected and Stripe does not open. | User was returned to the event page and Stripe did not open. | Pass |
| C6 | Enter a valid quantity within remaining capacity. | Stripe Checkout opens with the correct booking. | Stripe Checkout opened correctly. | Pass |
| C7 | Cancel from Stripe Checkout. | User returns to the event detail page and no confirmed booking is created. | User returned correctly and no confirmed booking was created. | Pass |
| C8 | Attempt to book a sold-out event. | Sold-out state is clear and booking cannot proceed. | Sold-out state displayed and booking was unavailable. | Pass |
| C9 | With exactly one place remaining, book one place. | Booking is allowed. | Booking was allowed. | Pass |
| C10 | With exactly one place remaining, try to book two places. | Booking is rejected. | User was returned to the event page and Stripe did not open. | Pass |

**Booking flow and capacity result: 10/10 passed.**

---

## D. Payment, Confirmation and Cancellation

| ID | Test | Expected Result | Actual Result | Status |
|---|---|---|---|:---:|
| D1 | Complete a valid Stripe test payment. | Payment succeeds and user returns to the booking-success flow. | Test payment completed and success flow loaded. | Pass |
| D2 | Check the booking-success page. | Correct event, quantity and booking details are displayed. | Booking details displayed correctly. | Pass |
| D3 | Open the profile after payment. | New confirmed booking appears. | Booking appeared on the user's profile. | Pass |
| D4 | Check event availability after payment. | Remaining places decrease by the purchased quantity. | Availability decreased correctly. | Pass |
| D5 | Check the booking confirmation email. | Correct booking information is received. | Confirmation email was received correctly. | Pass |
| D6 | Open the cancellation page for the user's own eligible booking. | Cancellation confirmation page loads. | Cancellation page loaded correctly. | Pass |
| D7 | Cancel the booking. | Refund succeeds, booking is cancelled and user returns to profile. | Initial test exposed an email-delivery exception after successful cancellation. The application was fixed and retested; cancellation now completes and returns to profile even if email delivery fails. | Pass after fix |
| D8 | Check the booking after cancellation. | Booking is marked cancelled. | Booking status changed to cancelled. | Pass |
| D9 | Check event capacity after cancellation. | Cancelled places become available again. | Capacity was restored correctly. | Pass |
| D10 | Check the cancellation/refund email. | Cancellation details are received correctly. | Initial test address was rejected by the email provider. Retesting with a valid test address completed successfully. | Pass after retest |

**Payment, confirmation and cancellation result: 10/10 passed after the D7/D10 email-handling issue was corrected and retested.**

---

## E. Administrator Functionality

| ID | Test | Expected Result | Actual Result | Status |
|---|---|---|---|:---:|
| E1 | Log into Django Admin. | Admin dashboard loads successfully. | Admin dashboard loaded. | Pass |
| E2 | Open Events in Admin. | Event records and configured columns/filters are visible. | Event list displayed correctly. | Pass |
| E3 | Create a valid new event. | Event saves and appears on the customer-facing site. | Event saved and appeared publicly. | Pass |
| E4 | Edit an event. | Changes save and appear on the public event page. | Changes appeared correctly. | Pass |
| E5 | Change event capacity. | Remaining availability reflects the new capacity. | Availability updated correctly. | Pass |
| E6 | Create/edit a category and assign an event. | Category saves and event appears under it. | Category assignment worked correctly. | Pass |
| E7 | Open Bookings in Admin. | Booking records are visible with useful information. | Booking records displayed correctly. | Pass |
| E8 | Create an event with required data missing. | Admin rejects the invalid event and shows validation errors. | Validation prevented the invalid save. | Pass |

**Administrator functionality result: 8/8 passed.**

---

## F. Validation, Feedback and Error Handling

| ID | Test | Expected Result | Actual Result | Status |
|---|---|---|---|:---:|
| F1 | Submit registration without a username. | Form is rejected with a clear validation error. | Validation error appeared and account was not created. | Pass |
| F2 | Register using an existing username. | Registration is rejected with useful feedback. | Duplicate username was rejected. | Pass |
| F3 | Register with mismatched passwords. | Account is not created and password validation appears. | Password mismatch was rejected correctly. | Pass |
| F4 | Log in with an incorrect password. | Login is rejected and no authenticated session is created. | Invalid login was rejected. | Pass |
| F5 | Edit the profile with a valid new email. | Email saves and success feedback appears. | Profile email updated correctly. | Pass |
| F6 | Open a nonexistent event URL. | A 404 response is returned rather than a server error. | Django's development 404 page was returned while running locally with debug enabled. | Pass |
| F7 | Open another user's booking cancellation URL. | Access is denied without exposing the booking. | A 404 response was returned. | Pass |
| F8 | Perform an action that displays normal success/error feedback. | Feedback is visible and understandable. | User feedback displayed clearly. | Pass |

**Validation, feedback and error-handling result: 8/8 passed.**

---

## G. Responsive Design, Accessibility, Static Files and Media

| ID | Test | Expected Result | Actual Result | Status |
|---|---|---|---|:---:|
| G1 | View homepage at desktop width. | Layout displays without overlap, clipping or document-level horizontal overflow. | Layout displayed correctly. DevTools confirmed `viewport`, `htmlScrollWidth` and `bodyScrollWidth` were all 1920px, with no overflowing page element detected. The intentionally wide ticker remained contained by `overflow-x: hidden`. | Pass |
| G2 | View homepage at tablet width. | Layout adapts with usable navigation and readable content. | Tablet layout displayed correctly. | Pass |
| G3 | View homepage at mobile width. | Navigation works, content fits and no horizontal scrolling occurs. | Mobile homepage worked correctly. | Pass |
| G4 | View event catalogue at mobile width. | Cards reflow cleanly and controls remain usable. | Catalogue displayed correctly. | Pass |
| G5 | View event detail and booking pages at mobile width. | Details, quantity controls and buttons remain usable. | Pages displayed and functioned correctly. | Pass |
| G6 | View login, registration and profile pages at mobile width. | Forms fit the screen and controls remain usable. | Forms remained usable. Further visual centring/polish is planned but no functional responsive defect was found. | Pass |
| G7 | Navigate primary controls using the Tab key. | Interactive controls can be reached in a sensible order and focus is visible. | Keyboard navigation and visible focus worked correctly. | Pass |
| G8 | Verify event images. | Event images load correctly and are not broken. | Final event images have not yet been uploaded, so this cannot yet be meaningfully tested. | Pending |
| G9 | Check CSS and JavaScript behaviour. | Styling and interactive effects function correctly. | Styling and JavaScript, including special-event effects/navigation, worked correctly. | Pass |
| G10 | Zoom a normal page to approximately 200%. | Core content remains readable and usable without major overlap or loss of information. | Content remained readable and usable. | Pass |

**Responsive/accessibility result: 9 completed checks passed, 1 media check pending.**

---

# Issues Identified and Regression Tested

Testing and the subsequent robustness audit identified several failure paths that were not apparent during the initial successful user journeys. Each issue below was corrected and backed by automated regression coverage.

## Cancellation Email Failure After Successful Refund

During manual cancellation testing, the email provider rejected a recipient address using the reserved `example.com` domain and raised an SMTP error:

```text
SMTPDataError
550 Invalid `to` field
```

The refund itself had already succeeded, the booking had been marked as cancelled and the released places had been returned to the event capacity. However, the email exception propagated through the request and caused a server error instead of returning the user to the profile.

Cancellation email delivery was changed so SMTP and connection failures are logged without undoing or obscuring the successful refund and cancellation.

Manual tests D7 and D10 were repeated after the fix and passed.

## Additional Robustness Regression Coverage

| Issue / Risk                                                                              | Resolution                                                                                                                                                            | Regression Evidence                                                                                                           |
| ----------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| Booking confirmation email fails after a successful webhook booking.                      | Confirmation-email failures are logged without changing the successful booking or causing the webhook to fail.                                                        | Test verifies the webhook still returns success and preserves the confirmed booking when email delivery raises an SMTP error. |
| Event capacity disappears after a customer has already paid.                              | An over-capacity paid booking is recorded as cancelled and an automatic Stripe refund is requested. Failed refund attempts are retried safely.                        | Tests verify successful automatic refund and retry after a temporary Stripe API failure.                                      |
| Stripe Checkout Session creation fails because of an API/network error.                   | Stripe exceptions are caught and the user is returned safely to the event page instead of receiving a server error.                                                   | Test simulates a Stripe API connection failure.                                                                               |
| Stripe redirects the browser before the webhook has created the booking.                  | The success page displays a processing state instead of returning a false 404. Confirmed and cancelled/refunded bookings have separate states.                        | Tests cover delayed booking creation, confirmed ownership and cancelled/refunded presentation.                                |
| The user account referenced by a paid webhook no longer exists.                           | The payment is automatically refunded rather than attempting an invalid booking insert.                                                                               | Test verifies no booking is created and the correct idempotent refund is requested.                                           |
| The event referenced by a paid webhook is deleted or becomes inactive before fulfilment.  | The payment is automatically refunded and the webhook returns successfully when the refund succeeds.                                                                  | Test verifies an inactive event produces no booking and requests the correct refund.                                          |
| Two copies of the same Stripe webhook arrive at nearly the same time.                     | The event row is locked and the booking session is checked again after acquiring the lock. Existing bookings are returned safely without duplicate creation or email. | Test simulates the first duplicate check missing the booking and the post-lock check finding it.                              |
| Stripe successfully refunds a cancellation but the local booking save subsequently fails. | Cancellation refunds use a deterministic idempotency key based on the booking ID. A retry therefore refers to the same Stripe refund operation.                       | Test simulates a failed local save followed by a successful retry and verifies the same idempotency key is used twice.        |
| A zero-quantity booking is created outside the normal checkout validation path.           | `Booking.quantity` now uses `MinValueValidator(1)` and a database `CheckConstraint` requiring `quantity >= 1`.                                                        | Test verifies a direct zero-quantity ORM insert raises `IntegrityError`.                                                      |

These regression tests supplement the original functional tests by exercising failure recovery, retry safety, payment integrity and database-level business rules.

---

# Pending Testing

The following checks are deliberately not marked as passed because the necessary final conditions do not yet exist.

## Event Images

**G8 remains pending.**

Final event imagery still needs to be selected and uploaded so that it matches the event catalogue and descriptions. Once images are present, testing should verify:

- images load successfully;
- no broken image links appear;
- event cards and detail pages use the correct image;
- media is served correctly from the configured storage backend;
- image dimensions do not damage responsive layouts;
- image alternatives/accessibility are appropriate.

## Production / Heroku

Production-specific testing will be completed after the final application is deployed to Heroku.

The production acceptance pass should include:

| ID | Production Test | Expected Result | Status |
|---|---|---|:---:|
| P1 | Open deployed homepage. | Application loads over HTTPS without server errors. | Pending |
| P2 | Test deployed navigation and internal links. | All major links resolve correctly. | Pending |
| P3 | Register, log in and log out in production. | Authentication works correctly with secure production settings. | Pending |
| P4 | Search and filter deployed events. | Search/filter behaviour matches local development. | Pending |
| P5 | Complete a Stripe test payment against the deployed application. | Checkout, webhook and confirmation flow work correctly. | Pending |
| P6 | Cancel a deployed test booking. | Refund, cancellation state, capacity restoration and email handling work correctly. | Pending |
| P7 | Verify production media. | S3-hosted event images load correctly. | Pending |
| P8 | Verify static assets. | CSS and JavaScript load without missing-file errors. | Pending |
| P9 | Test production 404 behaviour. | Production-safe 404 page/response appears with `DEBUG=False`. | Pending |
| P10 | Verify responsive layouts on the deployed site. | Production presentation matches the tested local application. | Pending |

---

# Testing Summary

Current verified testing status:

| Testing Area                             |                 Result |
| ---------------------------------------- | ---------------------: |
| Automated Django tests                   |       **54/54 passed** |
| Authentication manual tests              |         **9/9 passed** |
| Navigation/search manual tests           |       **10/10 passed** |
| Booking/capacity manual tests            |       **10/10 passed** |
| Payment/cancellation manual tests        |       **10/10 passed** |
| Administrator manual tests               |         **8/8 passed** |
| Validation/error-handling manual tests   |         **8/8 passed** |
| Responsive/accessibility completed tests |         **9/9 passed** |
| Media tests                              |          **1 pending** |
| Production deployment tests              | **Pending deployment** |

**Current completed manual testing: 64/64 passed.**

Automated coverage now includes successful application behaviour together with regression tests for payment-service failures, email failures, refund retry safety, delayed webhook processing, concurrent duplicate webhook delivery and database-level booking validation.

The local automated and manual testing phases are complete for the functionality tested so far, apart from final event-image verification. Production-specific acceptance checks will be completed after the final Heroku deployment.
