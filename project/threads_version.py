from flask import Flask, request, render_template, jsonify, redirect, url_for
from weasyprint import HTML
from random import randint
from threading import Thread
import os
import time

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test'
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/submit_invoice', methods=['POST'])
    def submit_invoice():
        data = get_form_data(request.form)
        thread = Thread(target=generate_pdf, args=(data,))
        thread.start()
        pdf_url = f'/static/{data["invoice"]["invoiceNo"]}.pdf'
        return redirect(url_for('index'))
    
    @app.route('/submit_invoice_sync', methods=['POST'])
    def submit_invoice_sync():
        data = get_form_data(request.form)
        pdf_path = generate_pdf(data)
        pdf_url = f'/static/{data["invoice"]["invoiceNo"]}.pdf'
        return redirect(url_for('index'))

    @app.route('/generate_multiple_pdfs', methods=['POST'])
    def generate_multiple_pdfs():
        num_pdfs = request.form.get('numPdfs', type=int)
        threads = []

        for i in range(num_pdfs):
            data = get_form_data(request.form)
            data['invoice']['invoiceNo'] = f'OA-{i+1}'
            thread = Thread(target=generate_pdf, args=(data,))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        return redirect(url_for('index'))
    
    @app.route('/generate_multiple_pdfs_sync', methods=['POST'])
    def generate_multiple_pdfs_sync():
        num_pdfs = request.form.get('numPdfs', type=int)
        pdf_paths = []

        for i in range(num_pdfs):
            data = get_form_data(request.form)
            data['invoice']['invoiceNo'] = f'OA-{i+1}'
            pdf_path = generate_pdf(data)
            pdf_paths.append({'invoiceNo': data['invoice']['invoiceNo'], 'pdf_path': pdf_path})

        return redirect(url_for('index'))

    return app

app = create_app()

def get_form_data(form):
    qtdPermit = form.get('qtdPermit', type=int)
    totalLicense = form.get('totalLicense', type=float)
    qtdStaticPermit = form.get('qtdStaticPermit', type=int)
    totalStaticPermit = form.get('totalStaticPermit', type=float)
    qtdCmlCmsPermit = form.get('qtdCmlCmsPermit', type=int)
    totalCmlCmsPermit = form.get('totalCmlCmsPermit', type=float)
    signs = form.get('signs', '').split(',')

    return {
        'invoice': {
            'invoiceNo': 'OA-1',
            'qtdPermit': qtdPermit,
            'totalLicense': "{:,.2f}".format(totalLicense),
            'qtdStaticPermit': qtdStaticPermit,
            'totalStaticPermit': "{:,.2f}".format(totalStaticPermit),
            'qtdCmlCmsPermit': qtdCmlCmsPermit,
            'totalCmlCmsPermit': "{:,.2f}".format(totalCmlCmsPermit),
            'totalPartial': "{:,.2f}".format(totalLicense + totalStaticPermit + totalCmlCmsPermit),
            'year': 2024
        },
        'signs': [{'name': sign.strip()} for sign in signs if sign.strip()]
    }

def generate_pdf(data):
    # print("Received data:", data)
    base_text_block = "World War II[b] or the Second World War (1 September 1939 - 2 September 1945) was a global conflict between two alliances: the Allies and the Axis powers..."
    repeated_text = base_text_block * randint(1, 20)

    with app.app_context():
        html = render_template('invoicePDF.html', d=data, repeated_text=repeated_text)
        pdf_file = f'static/{data["invoice"]["invoiceNo"]}.pdf'
        HTML(string=html).write_pdf(pdf_file)
        return pdf_file

if __name__ == '__main__':
    app.run(debug=True)
 