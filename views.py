import streamlit as st
import fitz  # PyMuPDF
import nltk
import spacy
import re
import os

# Ensure that nltk data is downloaded
nltk.download('punkt')

def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += page.get_text()
    sentences = nltk.sent_tokenize(text)
    return sentences, text

def find_director_sentences(sentences):
    director_sentences = []
    for sentence in sentences:
        if 'director' in sentence.lower():
            director_sentences.append(sentence)
    return director_sentences

def find_person_names(sentences):
    nlp = None
    try:
        nlp = spacy.load('en_core_web_sm')
    except Exception as e:
        st.error(f"Error loading spaCy model: {e}")
        return []

    person_names = set()
    for sentence in sentences:
        if nlp is not None:
            doc = nlp(sentence)
            for ent in doc.ents:
                if ent.label_ == 'PERSON':
                    if len(ent.text.split()):
                        person_names.add(ent.text)
                    else:
                        if ent.text.istitle():
                            person_names.add(ent.text)
    return list(person_names)

def clean_director_names(director_names, blacklist):
    cleaned_names = set()
    for name in director_names:
        if name.lower() not in [item.lower() for item in blacklist]:
            cleaned_names.add(name)
    return cleaned_names

def find_din_and_status(director_names, all_sentences):
    director_info = {}
    for name in director_names:
        din = "DIN not found"
        status = "Status not specified"
        for sentence in all_sentences:
            if name in sentence:
                lines = sentence.split('\n')
                for line in lines:
                    if name in line:
                        din_match = re.search(r'\bDIN\s*:\s*(\d+)\b', line)
                        if din_match:
                            din = din_match.group(1)
                            break
                        words = line.split()
                        if name in words:
                            name_index = words.index(name)
                            if name_index + 2 < len(words):
                                din_match = re.search(r'\b(\d+)\b', words[name_index + 2])
                                if din_match:
                                    din = din_match.group(1)
                                    break
                        if 'independent' in line.lower():
                            status = "Independent"
                        elif 'executive' in line.lower():
                            status = "Executive"
                        elif 'whole-time' in line.lower():
                            status = "Whole-time"
                        elif 'non-executive' in line.lower():
                            status = "Non-Executive"
                        elif 'non-independent' in line.lower():
                            status = "Non-Independent"
                if din == "DIN not found" or status == "Status not specified":
                    if 'independent' in sentence.lower():
                        status = "Independent"
                    elif 'executive' in sentence.lower():
                        status = "Executive"
                    elif 'whole-time' in sentence.lower():
                        status = "Whole-time"
                    elif 'non-executive' in sentence.lower():
                        status = "Non-Executive"
                    elif 'non-independent' in sentence.lower():
                        status = "Non-Independent"
                director_info[name] = {'DIN': din, 'Status': status}
                break
    return director_info

st.title('Director Information Extractor')

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    with open('uploaded_file.pdf', 'wb') as file:
        file.write(uploaded_file.read())

    pdf_path = 'uploaded_file.pdf'
    pdf_sentences, text = extract_text_from_pdf(pdf_path)
    director_sentences = find_director_sentences(pdf_sentences)
    
    # Check if director sentences are found
    if not director_sentences:
        st.error("No director sentences found in the document.")
    else:
        director_names = find_person_names(director_sentences)
        
        # Check if person names are found
        if not director_names:
            st.error("No person names found in the director sentences.")
        else:
            blacklist = [
                'Chairperson', 'ALM', 'A-44 Hosiery Complex', 'BSEListingCentre Thru',
                'Asabove', 'Copyto', 'Dhruv M.', 'Sawhney', 'Homai A. Daruwalla',
                'Memberships/ Chairmanships', 'Noida Rajiv Sawhney', 'Date',
                'Dhruv M. Sawhney', 'Lagnam', 'Spintex India Ltd.', 'C. Laddha',
                'Qualifications B.Sc.', 'J. C. Laddha', 'and/or re -enactment(s',
                'w. e. f.', 'NA Appointment', 'Directorships', 'Bandra Kurla Complex',
                'Schedule III','Chairperson \nALM', 'A-44 Hosiery Complex', 'BSEListingCentre Thru', 'Asabove\nCopyto',  'Homai A. Daruwalla', 'Memberships/ Chairmanships',
                'Noida Rajiv Sawhney\nDate','Lagnam \nSpintex India Ltd.', 'Prashant Barve\nDirectorships','Lagnam \nSpintex India Ltd.','Mannepalli Lakshmi Kantam', 'M. Lakshmi','Jeet Singh Bagga',
                'Nikhil Sawhney','Tarun Sawhney','Dhruv M Sawhney','Dhruv M. \nSawhney','J','Kantam','modification(s','Schedule','RSWM','Bandra','Scrutinizer','Bhasin','Director','Bandra-KurlaComplex','Founder','Mumbai-400013',
                'Gangotra',
            ]
            cleaned_director_names = clean_director_names(director_names, blacklist)
            director_info = find_din_and_status(cleaned_director_names, director_sentences)

            for director, info in director_info.items():
                if info['Status'] == "Status not specified":
                    info['Status'] = "Whole-time"

            st.write("### Director Information")
            for director, info in director_info.items():
                st.write(f"**{director}**")
                st.write(f"  - DIN: {info['DIN']}")
                st.write(f"  - Status: {info['Status']}")
