// Netlify background function — fires on every guide-leads form submission
// Sends a personalized autoresponder email to the lead via Resend

export async function handler(event) {
  // Only handle form submission events for our guide-leads form
  if (event.body) {
    let payload;
    try {
      payload = JSON.parse(event.body);
    } catch {
      return { statusCode: 400, body: "Invalid payload" };
    }

    // Netlify sends form data under payload.data
    const data = payload.data || payload;
    const firstName = data.first_name || "there";
    const email = data.email;
    const guides = data.guides || "";

    if (!email) {
      console.log("No email address in submission, skipping autoresponder");
      return { statusCode: 200, body: "No email" };
    }

    // Build a friendly guide list for the email
    const guideMap = {
      student:    "Boone Student Housing Playbook",
      investment: "High Country Investment Property Guide",
      land:       "Buying Land in the High Country",
      relocation: "Welcome to the High Country",
    };

    const requestedGuides = guides
      .split(",")
      .map(g => guideMap[g.trim()] || g.trim())
      .filter(Boolean);

    const guideList = requestedGuides.length > 0
      ? requestedGuides.map(g => `• ${g}`).join("\n")
      : "• Your High Country Guide";

    const emailHtml = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
</head>
<body style="margin:0;padding:0;background:#F5F0E8;font-family:'Source Sans Pro',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#F5F0E8;padding:32px 16px;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.08);">

        <!-- Header -->
        <tr>
          <td style="background:#3B2F2F;padding:28px 36px;">
            <p style="margin:0;font-size:11px;font-weight:700;letter-spacing:0.2em;color:#C0622A;text-transform:uppercase;">plyler.realtor</p>
            <p style="margin:6px 0 0;font-size:22px;font-weight:700;color:#ffffff;font-family:Georgia,serif;">The High Country Realtor</p>
          </td>
        </tr>

        <!-- Body -->
        <tr>
          <td style="padding:36px 36px 28px;">
            <p style="margin:0 0 16px;font-size:16px;color:#3B2F2F;">Hi ${firstName},</p>

            <p style="margin:0 0 16px;font-size:15px;color:#4A3A3A;line-height:1.65;">
              Thanks for reaching out — your guide${requestedGuides.length > 1 ? "s are" : " is"} ready to download from the link you were just shown.
            </p>

            <div style="background:#F5F0E8;border-left:4px solid #C0622A;padding:16px 20px;margin:0 0 20px;border-radius:0 4px 4px 0;">
              <p style="margin:0 0 8px;font-size:13px;font-weight:700;color:#3B2F2F;text-transform:uppercase;letter-spacing:0.08em;">You requested:</p>
              <p style="margin:0;font-size:14px;color:#4A3A3A;line-height:1.8;white-space:pre-line;">${guideList}</p>
            </div>

            <p style="margin:0 0 16px;font-size:15px;color:#4A3A3A;line-height:1.65;">
              I put these guides together because I've seen too many people buy in the High Country without the full picture — and I'd rather you have it upfront. If anything in the guide raises a question, or if you'd like to talk through your specific situation, I'm happy to hop on a quick call. No pressure, just honest local advice.
            </p>

            <p style="margin:0 0 24px;font-size:15px;color:#4A3A3A;line-height:1.65;">
              I've had roots in these mountains my whole life. If you're thinking about buying here — whether it's a cabin, a piece of land, a student rental, or your forever home — I'd love to help you find the right corner of the High Country.
            </p>

            <table cellpadding="0" cellspacing="0">
              <tr>
                <td style="background:#C0622A;border-radius:5px;padding:12px 24px;">
                  <a href="https://plyler.realtor/contact" style="color:#ffffff;font-size:14px;font-weight:700;text-decoration:none;letter-spacing:0.04em;">Let's Talk →</a>
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <!-- Divider -->
        <tr><td style="padding:0 36px;"><hr style="border:none;border-top:1px solid #E8E0D5;"/></td></tr>

        <!-- Agent signature -->
        <tr>
          <td style="padding:24px 36px 32px;">
            <table cellpadding="0" cellspacing="0">
              <tr>
                <td style="padding-right:16px;vertical-align:top;">
                  <div style="width:52px;height:52px;border-radius:50%;overflow:hidden;border:2px solid #C0622A;">
                    <img src="https://plyler.realtor/assets/andrew-plyler-headshot.jpg" width="52" height="52" alt="Andrew Plyler" style="display:block;object-fit:cover;"/>
                  </div>
                </td>
                <td style="vertical-align:top;">
                  <p style="margin:0;font-size:15px;font-weight:700;color:#3B2F2F;font-family:Georgia,serif;">Andrew Plyler</p>
                  <p style="margin:2px 0 0;font-size:12px;color:#8C7B6B;">REALTOR®/Broker · Blue Ridge Realty &amp; Investments</p>
                  <p style="margin:4px 0 0;font-size:12px;color:#8C7B6B;">
                    <a href="tel:7706391233" style="color:#C0622A;text-decoration:none;">770.639.1233</a>
                    &nbsp;·&nbsp;
                    <a href="mailto:aplyler@brri.net" style="color:#C0622A;text-decoration:none;">aplyler@brri.net</a>
                    &nbsp;·&nbsp;
                    <a href="https://plyler.realtor" style="color:#C0622A;text-decoration:none;">plyler.realtor</a>
                  </p>
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <!-- Footer -->
        <tr>
          <td style="background:#3B2F2F;padding:14px 36px;text-align:center;">
            <p style="margin:0;font-size:11px;color:rgba(255,255,255,0.4);">
              Blue Ridge Realty &amp; Investments · 895 Blowing Rock Rd · Boone, NC 28607<br/>
              You're receiving this because you requested a guide at plyler.realtor.
            </p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>`;

    // Send via Resend
    const RESEND_API_KEY = process.env.RESEND_API_KEY;
    if (!RESEND_API_KEY) {
      console.error("RESEND_API_KEY not set — skipping email send");
      return { statusCode: 200, body: "No API key" };
    }

    try {
      const response = await fetch("https://api.resend.com/emails", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${RESEND_API_KEY}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          from: "Andrew Plyler <andrew@plyler.realtor>",
          to: [email],
          reply_to: "aplyler@brri.net",
          subject: `Your High Country Guide${requestedGuides.length > 1 ? "s are" : " is"} ready — Andrew Plyler`,
          html: emailHtml,
        }),
      });

      const result = await response.json();

      if (!response.ok) {
        console.error("Resend error:", JSON.stringify(result));
        return { statusCode: 500, body: "Email send failed" };
      }

      console.log(`Autoresponder sent to ${email} — guides: ${guides}`);
      return { statusCode: 200, body: "Email sent" };

    } catch (err) {
      console.error("Function error:", err);
      return { statusCode: 500, body: "Error" };
    }
  }

  return { statusCode: 200, body: "OK" };
}
