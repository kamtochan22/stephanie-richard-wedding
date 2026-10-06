/**
 * RSVP — Google Sheets Webhook (Google Apps Script)
 * Setup: sheets.new → rename tab to "RSVP" → Extensions → Apps Script →
 * paste this file → Deploy → New Deployment → Web App →
 * Execute as: Me / Access: Anyone → Deploy → open URL in browser to
 * authorize → RE-DEPLOY (new version) → paste final URL into
 * index.html (WEBHOOK_URL constant).
 */

const SHEET_NAME = "RSVP";
const HEADERS = [
  "Timestamp", "Date", "Name", "Email", "Attendance",
  "Guests", "Dietary", "Note", "Source"
];

function doPost(e) {
  try {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sheet = ss.getSheetByName(SHEET_NAME);
    if (!sheet) throw new Error("Sheet '" + SHEET_NAME + "' not found — rename the tab");

    const data = JSON.parse(e.postData.contents);

    // auto-create headers on first row
    if (sheet.getLastRow() === 0) sheet.appendRow(HEADERS);

    sheet.appendRow([
      new Date().toISOString(),
      Utilities.formatDate(new Date(), "GMT+8", "yyyy-MM-dd"),
      data.name || "",
      data.email || "",
      data.attendance || "",
      data.guests || "0",
      data.diet || "",
      data.note || "",
      data.source || "wedding-site"
    ]);

    return ContentService
      .createTextOutput(JSON.stringify({ success: true, row: sheet.getLastRow() }))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({ success: false, error: err.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function doGet() {
  return ContentService
    .createTextOutput(JSON.stringify({ status: "RSVP webhook live", sheet: SHEET_NAME }))
    .setMimeType(ContentService.MimeType.JSON);
}
