# Event Horizon Testing

This document records the testing carried out for Event Horizon.

Testing combines automated Django tests with manual browser-based testing. Automated tests cover repeatable backend behaviour, authentication, booking rules, Stripe boundaries and webhook handling. Manual testing covers complete user journeys, administrator functionality, visual behaviour, validation, responsiveness, accessibility and external-service behaviour that cannot be fully demonstrated through unit tests alone.

Testing results in this document reflect tests that were actually carried out. Local testing, code validation, final event-image/media verification and the Heroku production acceptance pass are now complete for the functionality currently available.

---

## Table of Contents

- [Automated Testing](#automated-testing)
- [Test-Driven Development Evidence](#test-driven-development-evidence)
- [Code Validation](#code-validation)
- [Manual Testing](#manual-testing)
  - [A. Authentication](#a-authentication)
  - [B. Navigation, Search and Event Discovery](#b-navigation-search-and-event-discovery)
  - [C. Booking Flow and Capacity](#c-booking-flow-and-capacity)
  - [D. Payment, Confirmation and Cancellation](#d-payment-confirmation-and-cancellation)
  - [E. Administrator Functionality](#e-administrator-functionality)
  - [F. Validation, Feedback and Error Handling](#f-validation-feedback-and-error-handling)
  - [G. Responsive Design, Accessibility, Static Files and Media](#g-responsive-design-accessibility-static-files-and-media)
- [Issues Identified and Regression Tested](#issues-identified-and-regression-tested)
- [Final Media and Production Testing](#final-media-and-production-testing)
- [Testing Summary](#testing-summary)

---

# Automated Testing

Automated tests are implemented in the `tests.py` files for the `home`, `profiles`, `events` and `bookings` apps.

The suite uses Django's `TestCase` together with `unittest.mock.patch` where external Stripe and email behaviour needs to be isolated. This allows payment, refund, webhook and failure-handling behaviour to be tested without contacting Stripe, creating real charges or relying on an external email provider during the automated test run.

The full suite can be run with:

```bash
python manage.py test
```

Latest verified full-suite result:

```text
Ran 82 tests
OK
```

All **82 automated tests passed**.

| App        | Tests | Areas Covered |
| ---------- | ----: | ------------- |
| `home`     | 5 | Home page rendering, active/upcoming event filtering, featured-event limits, About rendering and unmatched-route handling. |
| `profiles` | 14 | Registration, required email validation, anonymous-only authentication access, protected profiles, booking ownership, profile updates, password changes, refund-state presentation and cancellation-action visibility for started/upcoming events. |
| `events`   | 30 | Model behaviour, capacity and price integrity, event timing including BST, protected relationships, admin restrictions, event discovery, sold-out behaviour, booking ownership, post-start booking/cancellation prevention, refunds and email-failure handling. |
| `bookings` | 33 | Validated checkout forms, Stripe Checkout creation and failure feedback, cancellation feedback, quantities/capacity, preserved payment values, booking-confirmation states, webhook validation, asynchronous payment success, refund handling, missing-user/event recovery, duplicate/concurrent webhook protection and refund-failure tracking. |
| **Total**  | **82** | **Core application, authentication, form validation, booking, payment, refund, webhook, failure recovery, timing, route handling and data integrity.** |

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
* event start-time evaluation using the configured Europe/London timezone, including British Summer Time;
* booked and remaining capacity calculations;
* confirmed bookings being counted while cancelled bookings are excluded;
* booking total-price and price-per-place calculations using the amount originally paid;
* database enforcement preventing zero-quantity bookings;
* validation and database enforcement preventing zero or negative event prices;
* prevention of reducing event capacity below confirmed booked places;
* protected event/category relationships where historical booking data would otherwise be deleted;
* view-only protection for Stripe-managed bookings in Django Admin;
* active-only event listings;
* search by event name, description, location and category;
* category filtering;
* inactive event 404 handling;
* authenticated booking access;
* prevention of booking events that have already started;
* sold-out booking prevention;
* GET-only booking-form behaviour;
* prevention of access to another user's cancellation route;
* prevention of cancellation after an event has started;
* successful refund and booking cancellation;
* graceful handling of cancellation email failures;
* deterministic Stripe idempotency keys for cancellation refunds;
* safe cancellation retry when Stripe has refunded but the local booking update initially fails;
* authenticated access to Stripe Checkout;
* invalid, zero, negative and malformed checkout quantities;
* requests above remaining event capacity;
* missing customer email handling;
* binding and validating `BookingForm` before Stripe Checkout is created;
* valid Stripe Checkout Session creation;
* user-facing feedback when Stripe Checkout Session creation raises a Stripe API/network error;
* reversed absolute success and cancellation URLs;
* cancelled Stripe Checkout returning to the event page with an explicit "no booking was created" message;
* booking-success session requirements;
* booking-confirmation ownership;
* delayed webhook handling after a successful Stripe redirect;
* separate confirmed, refund-requested, refund-processing and refund-failed presentation states;
* malformed Stripe webhook payloads;
* invalid Stripe webhook signatures;
* ignored unrelated webhook event types;
* ignored unpaid checkout sessions;
* successful immediate paid booking creation;
* successful delayed payment fulfilment through `checkout.session.async_payment_succeeded`;
* preservation of the amount originally paid if an event price later changes;
* graceful handling of booking-confirmation email failures;
* duplicate webhook protection;
* concurrent duplicate webhook protection after acquiring the event lock;
* webhook-side capacity enforcement;
* automatic refunds when capacity becomes unavailable after payment;
* retry-safe refunds when an automatic capacity refund temporarily fails;
* automatic refunds when the booking user no longer exists;
* automatic refunds when the referenced event becomes unavailable or has already started;
* recording of Stripe `refund.failed` events against the affected booking;
* user-facing failed-refund status presentation;
* confirmation email triggering only for successfully fulfilled bookings;
* unmatched URL routes redirecting to the homepage with `DEBUG=False`;
* genuine missing/inactive resources and ownership-protected resources retaining 404 responses.

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

# Test-Driven Development Evidence

The final robustness pass deliberately used RED → GREEN test-first cycles so the required behaviour was captured before each implementation change.

| Cycle | Requirement | RED commit | RED evidence | GREEN commit | Result |
|---|---|---|---|---|---|
| 1 | Show useful feedback if Stripe Checkout Session creation fails. | `0de00d7` | New test simulated `stripe.error.APIConnectionError` and failed because the expected message was not present. | `ecd0e5d` | Stripe errors are caught and the user is returned to the event page with a clear payment-start failure message. |
| 2 | Show feedback when the user cancels Stripe Checkout. | `1902d12` | New tests expected a cancellation query parameter and visible cancellation message. | `a9e8a72` | The cancel URL returns to the event detail page with `payment_cancelled=1`, which displays confirmation that no booking was created. |
| 3 | Use Django form validation in the checkout POST path. | `6320d11` | New test patched `BookingForm` and failed because the checkout view never instantiated it. | `d52da26` | Checkout binds `BookingForm(request.POST)`, requires `is_valid()` and reads `cleaned_data['quantity']` before Stripe is called. |
| 4 | Redirect an entirely unknown URL to the homepage. | `69ba4a3` | New `DEBUG=False` test expected a redirect but received HTTP 404. | `e7dcb51` | A custom top-level 404 handler redirects unmatched routes to `home`. |

The fourth change was then subjected to the **complete** suite rather than only its new focused test. That run exposed three regressions: inactive-event and ownership-protected resource tests were receiving redirects instead of their expected 404 responses. Commit `fac4ed6` changed the handler to redirect only `Resolver404` route misses and delegate genuine resource `Http404` responses to Django's normal `page_not_found` handling.

The focused regression tests then passed, followed by the complete result:

```text
Ran 80 tests in 122.506s
OK
```

This history is intentionally documented as four genuine test-first cycles. Earlier parts of Event Horizon were developed before this final TDD pass, so the documentation does not claim that the entire historical project was created using TDD.

---

# Code Validation

A final standards sweep was completed after the robustness, accessibility and feedback work.

## Python - Flake8

The project was checked with:

```bash
flake8 . --exclude=.venv,*/migrations/*,staticfiles
```

The first final sweep found only two formatting issues introduced by the new home-route test/handler work:

```text
./home/tests.py:100:1: W391 blank line at end of file
./home/views.py:55:1: E302 expected 2 blank lines, found 1
```

The trailing blank line was removed and the required top-level function spacing was added. A second full-project run completed with **no output**, confirming that no Flake8 findings remained.

The changes were formatting-only: no application logic was altered. The complete Django suite had already passed **80/80** after the functional 404 regression correction.

## HTML - W3C Nu HTML Checker

Rendered HTML was checked with the W3C Nu HTML Checker. Public pages were validated from the deployed site, while authenticated pages were checked using rendered page source so the validator received final HTML rather than Django template syntax.

The broader validation pass covered representative pages including:

- homepage;
- event catalogue;
- event detail, including a `Not for the Faint of Heart` event;
- About;
- login;
- registration;
- profile;
- edit profile;
- change password;
- booking form;
- cancellation confirmation.

Earlier validation identified invalid password-help nesting in the registration and change-password forms. Those templates were corrected and revalidated with no errors or warnings.

After the later shared-template changes for the accessible search label and global messages, the **live production homepage was validated again**. The checker reported:

```text
Document checking completed. No errors or warnings to show.
```

## CSS - W3C CSS Validation Service

The final `static/css/style.css`, including reduced-motion rules, keyboard ticker focus handling and global feedback-message styling, was checked again using the W3C CSS Validation Service.

Result:

```text
Congratulations! No Error Found.
```

## JavaScript - JSHint

The final `static/js/main.js`, including the reduced-motion preference handling, was checked again with JSHint.

JSHint reported **no errors or warnings**.

Final reported metrics:

- 14 functions;
- largest function signature: 1 argument;
- largest function: 24 statements;
- median function size: 3.5 statements;
- maximum cyclomatic complexity: 8;
- median cyclomatic complexity: 1.

---

# Manual Testing

Manual testing was carried out using both the local development application and the deployed Heroku application. Tests were performed through the browser using realistic visitor, registered-user and administrator journeys.

Each result below records:

- the action tested;

- the expected result;

- the observed result;

- the final status.

A total of **80/80 manual checks pass** across local and production testing.

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
| B11 | Allow a same-day event to pass its scheduled start time and refresh the homepage. | Started events no longer appear in the homepage upcoming or featured lists. | Production testing exposed date-only homepage filtering. The queryset was corrected to apply the event start time as well as the date, then retested locally and on Heroku; the affected started events disappeared from the homepage. | Pass after fix |

**Navigation, search and discovery result: 11/11 passed.**

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
| C7 | Cancel from Stripe Checkout. | User returns to the event detail page, receives clear cancellation feedback and no confirmed booking is created. | User returned correctly, the page displayed `Payment was cancelled. No booking was created.`, and the cancelled Checkout did not create a confirmed booking. | Pass |
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
| F8 | Perform an action that displays normal success/error feedback. | Feedback is visible and understandable. | Global Django feedback displayed in the shared styled message component and remained clearly readable. | Pass |

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
| G6 | View login, registration and profile pages at mobile width. | Forms fit the screen and controls remain usable. | Forms remained usable and displayed correctly at mobile width. No functional responsive defect was found. | Pass |
| G7 | Navigate primary controls using the Tab key. | Interactive controls can be reached in a sensible order and focus is visible. | Keyboard navigation and visible focus worked correctly. | Pass |
| G8 | Verify event images. | Event images load correctly and are not broken. | All 70 final event images were uploaded through Django Admin to the configured S3-backed media storage and checked category by category on the deployed site. Images loaded correctly on event cards and detail pages with no broken image links observed. | Pass |
| G9 | Check CSS and JavaScript behaviour. | Styling and interactive effects function correctly. | Styling and JavaScript, including special-event effects/navigation, worked correctly. | Pass |
| G10 | Zoom a normal page to approximately 200%. | Core content remains readable and usable without major overlap or loss of information. | Content remained readable and usable. | Pass |

**Responsive/accessibility/static/media result: 10/10 passed.**

---

# Issues Identified and Regression Tested

Testing and the subsequent robustness audit identified several failure paths and presentation issues that were not apparent during the initial successful user journeys. Each issue below was corrected and retested, with automated regression coverage added where appropriate.

## Cancellation Email Failure After Successful Refund

During manual cancellation testing, the email provider rejected a recipient address using the reserved `example.com` domain and raised an SMTP error:

```text

SMTPDataError

550 Invalid `to` field

```

The refund itself had already succeeded, the booking had been marked as cancelled and the released places had been returned to the event capacity. However, the email exception propagated through the request and caused a server error instead of returning the user to the profile.

Cancellation email delivery was changed so SMTP and connection failures are logged without undoing or obscuring the successful refund and cancellation.

Manual tests D7 and D10 were repeated after the fix and passed.

## Profile Booking Card Expanded to Full Width

During production acceptance testing after a successful Stripe booking, the profile page showed a single booking card stretched across the full available row rather than retaining a normal card width.

The cause was the profile booking grid using an `auto-fit` column definition with `minmax(280px, 1fr)`. With only one booking present, the single grid column expanded to consume all remaining horizontal space.

The grid was updated to cap desktop booking columns at 360px and align them from the start of the row while preserving the existing full-width mobile layout.

The fix was verified locally, committed, redeployed to Heroku and then retested on the live profile page. The booking card displayed at the intended card width in production.

## Category Filter Active State Did Not Highlight

During final production-polish testing, category filtering itself worked correctly, but the selected category chip did not receive the expected active styling. The view converted the `category` query-string value to an integer and passed that integer as `selected_category`, while the template compared it against a string-formatted category ID.

The template comparison was corrected to compare `selected_category` directly with `category.id`.

The fix was verified locally, the `events` test suite was rerun with **30/30 tests passing**, and the change was then deployed and confirmed on the live Heroku site.

## Missing Favicon

Production browser testing initially showed a missing favicon request. A dedicated `static/images/favicon.svg` asset was created and linked from the shared `base.html` template using Django's static-file handling.

The favicon was verified locally, committed, pushed to GitHub, deployed to Heroku and confirmed working on the live site.

## Started Events Remained on the Homepage

During final production follow-up testing, an event scheduled for 21:00 on the
current date was still visible on the homepage after 22:30, even though it had
correctly disappeared from the event catalogue.

A production shell check confirmed that Django was using the correct
`Europe/London` local time, the event's `has_started` property was `True`, and
the event no longer matched the event-list queryset. This isolated the problem
to the homepage query.

The homepage had been filtering with `date__gte=today`, which kept every event
dated today visible until midnight regardless of its start time. The homepage
query was updated to use the same rule as the event catalogue: future dates are
included, while events dated today are included only when their start time is
still in the future.

`home/views.py` passed Flake8, the `home` test suite passed, and the behaviour
was checked locally before deployment. After the fix was pushed to GitHub and
Heroku, the affected started events were confirmed absent from the live
homepage.


## Stripe Checkout Failure and Cancellation Feedback

A focused audit identified two payment paths where the backend behaved safely but the user received insufficient explanation.

First, a Stripe API/network error while creating Checkout returned the user away from the failed payment attempt but did not provide an explicit message. A test-first change added a global Django error message explaining that payment could not be started and that the user should try again.

Second, cancelling from Stripe Checkout returned to the event page but originally looked similar to ordinary navigation. A separate RED → GREEN cycle changed the Stripe `cancel_url` to return with `payment_cancelled=1`; the event-detail view then displays:

```text
Payment was cancelled. No booking was created.
```

The global message component was subsequently styled so information, success and error feedback have a consistent card treatment rather than appearing as isolated text at the top of the page. The cancellation message and its final styling were verified on the deployed site.

## BookingForm Was Not Used by the Checkout POST Path

The project already contained a Django `BookingForm`, but the Checkout view was still manually parsing the posted quantity. This meant the user-facing form existed without being the authoritative validation path for the paid request.

A test-first regression check patched `BookingForm` and failed because the Checkout view did not instantiate it. The implementation was then changed to bind `BookingForm(request.POST)`, require `is_valid()`, and read the cleaned quantity before creating the Stripe Checkout Session.

The form still does not call `save()` at this stage. That is deliberate: a paid `Booking` record is created only by the verified successful-payment webhook, preventing abandoned Checkout Sessions from occupying capacity.

## Unknown Route Redirect Initially Replaced Resource 404s

The qualification requirement for a nonexistent page prompted a test-first change so a completely unmatched URL redirects to the homepage when `DEBUG=False`.

The focused test passed after the first implementation, but the subsequent full 80-test suite exposed three regressions. The custom handler was also intercepting resource-level `Http404` responses, which meant inactive events and ownership-protected booking resources redirected rather than returning 404.

The handler was corrected to check for Django `Resolver404`. Only an unmatched URL route now redirects home; real matched routes that refer to missing, inactive or unauthorized resources are delegated to Django's standard `page_not_found` response.

The distinction was then verified in production:

```text
Unmatched URL route        -> homepage redirect
Matched missing event      -> HTTP 404 Not Found
```

## Reduced Motion and Keyboard Ticker Accessibility

The final accessibility pass found that the animated homepage ticker could move keyboard focus into links that were no longer visibly positioned on screen. The ticker now detects `:focus-within`, stops animating, wraps into a static list and gives each focused link a strong `:focus-visible` outline. When focus leaves the ticker, normal animation resumes.

`prefers-reduced-motion` support was also added across the animated experience. With reduced motion enabled, the homepage ticker becomes static, the special title stops glitching, the event image no longer follows the pointer and the whisper text remains static instead of repeatedly typing and erasing.

Both normal-motion and reduced-motion states were tested locally and on Heroku. Keyboard users were also able to tab through every ticker link visibly and then continue through the rest of the page.

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
| A zero-quantity booking is created outside the normal checkout validation path. | `Booking.quantity` uses `MinValueValidator(1)` and a database `CheckConstraint` requiring `quantity >= 1`. | Test verifies a direct zero-quantity ORM insert raises `IntegrityError`. |
| An invalid zero or negative event price is introduced outside the normal admin/form path. | Event prices use positive-value validation plus a database `CheckConstraint` requiring `price > 0`. | Tests verify model validation and direct database enforcement. |
| Event capacity is reduced below places already sold. | Model validation prevents capacity being set below confirmed booked places. | Test verifies `full_clean()` raises a capacity validation error. |
| An event or category with dependent booking/event records is deleted. | Critical relationships use `PROTECT` so historical booking data cannot be silently removed. | Tests verify protected deletion raises `ProtectedError`. |
| Booking or cancellation is attempted after the scheduled event start. | Event timing is enforced across booking, cancellation and webhook fulfilment. | Tests verify past events cannot be booked or cancelled and paid late fulfilment is refunded. |
| British Summer Time shifts the real event start relative to UTC. | The project uses `Europe/London`, and `Event.has_started` evaluates the stored local event time using Django's current timezone. | Regression test verifies an 18:00 July event has started by 17:30 UTC / 18:30 BST. |
| A delayed Stripe payment succeeds after Checkout initially completes unpaid. | The webhook handles `checkout.session.async_payment_succeeded` through the same paid-booking fulfilment path. | Test verifies the delayed-success event creates the confirmed booking and sends confirmation email. |
| An event price changes after a customer has already paid. | `Booking.total_paid` preserves the amount charged by Stripe so historical booking totals are not recalculated from the new event price. | Test verifies the booking continues to show the original paid amount. |
| A cancelled booking is still waiting for its automatic refund request to be recorded. | Customer-facing success/profile states distinguish refund processing from a refund request that has already received a Stripe refund ID. | Tests verify the correct wording for both states. |
| Stripe accepts a refund request but later reports that the refund failed. | The booking stores a `refund_status`; `refund.failed` records the failure and the profile shows `Refund Failed` instead of implying the refund succeeded. | Webhook and profile tests verify the failed-refund lifecycle end to end. |
| Stripe Checkout Session creation fails before the browser reaches Stripe. | The exception is caught and a global error message explains that payment could not be started. | RED/GREEN test cycle simulates `APIConnectionError` and verifies the visible feedback. |
| A user deliberately cancels Stripe Checkout. | The cancel URL returns to the event detail page with `payment_cancelled=1`; the page confirms that payment was cancelled and no booking was created. | RED/GREEN tests verify the cancel URL and message; production browser test confirms the live flow. |
| Checkout receives posted quantity data without using the Django form. | `BookingForm(request.POST)` is now the authoritative quantity-validation path before Stripe Session creation. | RED/GREEN test patches the form, verifies `is_valid()` and confirms Stripe is not called when the form is invalid. |
| A custom unknown-route redirect hides genuine resource 404 responses. | The 404 handler redirects only `Resolver404` route misses and preserves normal resource/ownership 404 responses. | Full-suite regression exposed the issue; focused route/resource tests and production checks verify the corrected split. |

These regression tests supplement the original functional tests by exercising failure recovery, retry safety, payment integrity, timezone correctness and database-level business rules.

---

# Final Media and Production Testing

Final event imagery and production media delivery were completed and verified after the main functional production acceptance pass.

## Event Images

**G8 and production media check P7 both pass.**

A complete set of **70 final event images** was uploaded through the live Django Admin across all seven event categories. Django stored the files using the configured S3-backed media storage.

Verification confirmed that:

- all 70 event images are present in production;
- images load successfully on the deployed site;
- no broken image links were observed during the category-by-category checks;
- event cards and event detail pages display the intended image;
- media is served correctly from the configured S3 storage backend;
- the event-card presentation remained visually consistent while the final imagery was added;
- image `alt` text uses the event name through the shared event-list template.

## Production / Heroku

Production-specific testing was carried out against the deployed Heroku application after the final functional, accessibility and feedback changes were released.

The deployed environment was also checked directly from the Heroku CLI:

```text
python manage.py migrate --check
Nothing pending
```

`python manage.py check --deploy` reported only Django's `security.W004` warning because `SECURE_HSTS_SECONDS` is not set. HSTS was intentionally not enabled merely to silence the warning; it should be introduced as a deliberate production policy. No additional deployment-check warnings were reported. HTTPS loaded correctly and HTTP redirected to HTTPS with a 301 response.

The production acceptance results are:

| ID | Production Test | Expected Result | Actual Result | Status |
|---|---|---|---|:---:|
| P1 | Open deployed homepage. | Application loads over HTTPS without server errors. | Homepage loaded successfully over HTTPS with normal styling and content. No application/server error occurred. | Pass |
| P2 | Test deployed navigation and internal links. | All major links resolve correctly. | Home/brand, Explore, About, account/profile and event-detail navigation all resolved correctly without unexpected 404 or 500 errors. | Pass |
| P3 | Register, log in and log out in production. | Authentication works correctly with secure production settings. | A new production test account was registered successfully, logged out successfully and then logged back in successfully. | Pass |
| P4 | Search and filter deployed events. | Search/filter behaviour matches local development. | Search and category filtering behaved correctly. Clearing the search term returned the full event catalogue as expected. | Pass |
| P5 | Complete a Stripe test payment against the deployed application. | Checkout, webhook and confirmation flow work correctly. | Stripe Checkout opened with the correct booking, the test payment completed, the booking-success page loaded and the confirmed booking appeared on the user's profile with the correct event, quantity and total. | Pass |
| P6 | Cancel a deployed confirmed booking. | Refund, cancellation state, capacity restoration and email handling work correctly. | Cancellation returned the user to the profile, the booking changed to Cancelled with Refund Requested, remaining capacity returned from 17 to 18 and the cancellation email was received. | Pass |
| P7 | Verify production media. | S3-hosted event images load correctly. | All 70 final event images were uploaded through live Django Admin to the configured S3-backed storage and checked on the deployed site. No broken event image links were observed. | Pass |
| P8 | Verify static assets. | CSS, JavaScript and favicon assets load without missing-file errors. | CSS and JavaScript loaded correctly across the deployed pages tested. The custom favicon also loaded correctly. | Pass |
| P9 | Verify unknown-route and real-resource 404 behaviour. | An unmatched URL redirects to the homepage, while a matched route for a missing resource returns HTTP 404. | `/definitely-not-a-real-page/` redirected home; `/events/999999/` returned the production `Not Found` response. | Pass |
| P10 | Verify responsive layouts on the deployed site. | Production presentation matches the tested local application. | Homepage, catalogue, event detail and profile layouts behaved correctly at desktop, tablet and mobile widths without clipping, overlap or horizontal layout failure. | Pass |
| P11 | Enable the operating system's reduced-motion/animation-off preference and refresh production. | Animated decorative effects stop or become static without removing content or functionality. | Homepage ticker became static; special title glitch and image-follow effects stopped; whisper text remained static. Normal motion returned when the preference was restored. | Pass |
| P12 | Navigate the production homepage ticker using only the keyboard. | Every ticker link is visibly focusable and the user can continue past the ticker. | Entering the ticker stopped the animation and presented a wrapped static list with visible focus. Every event link could be tabbed, after which normal ticker behaviour returned and tabbing continued down the page. | Pass |
| P13 | Start Stripe Checkout and use Stripe's cancel/back action. | User returns to the event page with explicit cancellation feedback and the final global-message styling is visible. | The event page displayed `Payment was cancelled. No booking was created.` and the styled global-message treatment was confirmed after deployment. Booking non-creation is separately covered by C7 and the automated checkout-cancellation tests. | Pass |
| P14 | Run production deployment/schema checks. | Database migrations are current and the deployment check reveals no unexpected configuration issues. | `migrate --check` reported nothing pending. `check --deploy` reported only the deliberate HSTS warning `security.W004`; HTTPS redirect behaviour was already functioning correctly. | Pass |

**Production acceptance result: 14/14 checks passed.**

---

# Testing Summary

Current verified testing status:

| Testing Area | Result |
|---|---:|
| Automated Django tests | **82/82 passed** |
| Authentication manual tests | **9/9 passed** |
| Navigation/search manual tests | **11/11 passed** |
| Booking/capacity manual tests | **10/10 passed** |
| Payment/cancellation manual tests | **10/10 passed** |
| Administrator manual tests | **8/8 passed** |
| Validation/error-handling manual tests | **8/8 passed** |
| Responsive/accessibility/static/media tests | **10/10 passed** |
| Production deployment tests | **14/14 passed** |
| Python / Flake8 validation | **Pass - no findings** |
| HTML / W3C Nu validation | **Pass - final live homepage no errors/warnings; representative pages previously passed** |
| CSS / W3C validation | **Pass - no errors** |
| JavaScript / JSHint validation | **Pass - no errors or warnings** |

**Current completed manual testing: 80/80 passed.**

Automated coverage includes successful application behaviour together with regression tests for payment-service failures, explicit checkout feedback, form binding/validation, email failures, refund retry safety, asynchronous payment completion, failed-refund tracking, event-start enforcement, British Summer Time handling, historical payment-value preservation, concurrent duplicate webhook delivery, database-level booking validation and the distinction between unmatched routes and missing/protected resources.

The latest full automated suite passes **82/82**. The earlier route-handler regression correction brought the suite to **80/80**, and the later profile-cancellation visibility tests increased the current automated total to 82. The Flake8 fixes changed only blank-line formatting and did not alter Python behaviour. Final Python, HTML, CSS and JavaScript validation all pass, production migrations are current, and the expanded Heroku acceptance pass is **14/14**.
