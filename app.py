from flask import Flask, render_template, request, send_file, redirect, url_for
import pdfkit, os, tempfile, datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

app = Flask(__name__)

LOCK_CODE = "8908"

def send_email(pdf_path, subject, to_email, from_email):
    message = Mail(
        from_email=from_email,
        to_emails=to_email,
        subject=subject,
        html_content=f"<strong>{subject}</strong>")
    with open(pdf_path, "rb") as f:
        data = f.read()
        f.close()
    message.add_attachment(data, "application/pdf", os.path.basename(pdf_path), "attachment")
    try:
        sg = SendGridAPIClient(os.environ.get("SENDGRID_API_KEY"))
        sg.send(message)
    except Exception as e:
        print(str(e))

@app.route("/", methods=["GET", "POST"])
def lock():
    if request.method == "POST":
        code = request.form.get("code")
        if code == LOCK_CODE:
            return redirect(url_for("menu"))
    return render_template("lock.html")

@app.route("/menu")
def menu():
    return render_template("menu.html")

@app.route("/form/<form_type>", methods=["GET", "POST"])
def form(form_type):
    if request.method == "POST":
        # Collect form data
        data = request.form.to_dict()
        html = render_template(f"{form_type}.html", data=data)
        pdf_fd, pdf_path = tempfile.mkstemp(suffix=".pdf")
        pdfkit.from_string(html, pdf_path)
        send_email(pdf_path, f"New {form_type.capitalize()} Submission", "nickkramer@prostarnow.com", "nickkramer@prostarnow.com")
        os.close(pdf_fd)
        os.remove(pdf_path)
        return "Form submitted and emailed successfully."
    return render_template(f"{form_type}.html", data={})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)