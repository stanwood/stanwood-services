import pdfkit

from flask import Flask, Response, request

app = Flask(__name__)


@app.route("/html2pdf", methods=["POST"])
def html2pdf():
    options = {
        "dpi": "300",
        "page-size": "A4",
        "orientation": "Portrait",
        "margin-left": "10mm",
        "margin-right": "5mm",
        "margin-top": "8mm",
        "margin-bottom": "13mm",
    }

    configuration = pdfkit.configuration(wkhtmltopdf="/app/wkhtmltopdf.sh")

    output = pdfkit.from_string(
        request.data.decode("utf-8"),
        output_path=False,
        options=options,
        configuration=configuration,
    )

    response = Response(
        headers={"Content-Disposition": 'attachment; filename="doc.pdf"'}
    )
    response.data = output
    return response
