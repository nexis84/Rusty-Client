# Patch Notes — Version 1.2.6

Release date: 2025-08-25

This update focuses on significant user interface cleanup, improved logging clarity, and critical bug fixes to enhance the operator experience during live giveaways.

## Summary
- Streamlines the confirmation and ESI/IGN workflows to reduce visual clutter and prevent stale data from persisting between draws.
- Makes many noisy status and technical messages visible only when Debug Mode is enabled.
- Fixes critical prize removal and post-win command handling bugs.

---

## New Features & Improvements

### Cleaner User Interface
- Removed the blue horizontal bars and borders from the ESI character sheet display for a more streamlined and modern look.
- The large "WINNER CONFIRMED" block that previously appeared in the confirmation log has been removed to reduce visual clutter after a winner confirms.

### Smarter Status Bar
- On startup the status bar now immediately shows the Twitch channel the bot will connect to, replacing the generic "Initializing..." message.

### Improved Workflow
- The "Confirmation & Response" log is now automatically cleared at the start of every new draw, ensuring each winner begins with a fresh slate and avoiding confusion with earlier information.

---

## Bug Fixes

### Critical Fix: Prize Removal
- Fixed a bug where prizes selected for a giveaway (especially random or manually-entered prizes) were not always removed correctly from the prize lists after winner confirmation.
- The system now preserves the full original prize string when selecting random/mystery or manually-entered prizes so removal matches the configured lists exactly.

### Critical Fix: Post-Win Command Handling
- Fixed an issue where the app could continue to accept and process `!ign` commands from a winner even after their ESI data had been successfully fetched and the draw completed.
- The winner context is now cleared after the ESI/animation cycle completes, preventing duplicate or late processing of `!ign` commands for that giveaway.

---

## Log & Status Message Cleanup (Debug Mode)
A comprehensive cleanup of log messages has been performed. The following detailed status updates will now only appear when Debug Mode is enabled, resulting in a much quieter confirmation log during normal operation:

- Startup connection messages such as "Connecting to..." and "Successfully connected to...".
- Draw lifecycle messages: "Draw OPEN!" and "Entry added:" during the entry phase.
- Streamer/prize selection confirmations such as "Streamer selected prize...".
- The `--- WINNER: ---` header that appeared after animations complete.
- Technical EVE2Twitch and ESI lookup messages (for example: "Attempting automatic lookup...", "Fetching ESI data...", "ESI worker busy...").
- Clipboard confirmation messages.

---

## Operator Notes
- If you rely on detailed internal status messages for troubleshooting, enable `debug_mode_enabled` in the config to restore the verbose output.
- When testing prize removal or random prize flows, verify that the prize lists update in the Options → Prizes panel after a confirmed win.

---

If you'd like, I can:
- Commit this file to the repository and create a matching entry in `CHANGELOG.md`.
- Produce a short README section summarizing the configuration key `debug_mode_enabled` and recommended defaults.
- Run the application with `debug_mode_enabled` toggled to demonstrate the log gating.

