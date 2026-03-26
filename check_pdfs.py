import os
import sys
import PyPDF2

folder = 'data/onboarding_agendas'
with open('results.txt', 'w', encoding='utf-8') as f:
    for file in os.listdir(folder):
        if file.endswith('.pdf'):
            path = os.path.join(folder, file)
            try:
                reader = PyPDF2.PdfReader(path)
                text = ''
                for page in reader.pages:
                    text += page.extract_text()
                
                # Check directly in text
                has_av = ' AV ' in text or '\nAV ' in text or ' AV\n' in text
                has_ms = ' MS ' in text or '\nMS ' in text or ' MS\n' in text
                has_msu = ' MSU ' in text or '\nMSU ' in text or ' MSU\n' in text
                f.write(f"File {file} -> AV: {has_av}, MS: {has_ms}, MSU: {has_msu}\n")
            except Exception as e:
                f.write(f"Error {file}: {e}\n")
