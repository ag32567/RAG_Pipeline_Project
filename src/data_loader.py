import os
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader

def load_all_documents(directory_path: str):
    """
    Load all PDF documents from the specified directory recursively.
    """
    all_documents = []
    dir_path = Path(directory_path)
    
    # Find all PDF files recursively
    pdf_files = list(dir_path.glob("**/*.pdf"))
    
    print(f"Found {len(pdf_files)} PDF files to process")
    
    for pdf_file in pdf_files:
        print(f"\nProcessing: {pdf_file.name}")
        try:
            loader = PyPDFLoader(str(pdf_file))
            documents = loader.load()
            
            # Adding more information to metadata
            for doc in documents:
                doc.metadata['source_file'] = pdf_file.name
                doc.metadata['file_type'] = 'pdf'
            
            all_documents.extend(documents)
            print(f"  [OK] Loaded {len(documents)} pages")
            
        except Exception as e:
            print(f"  [ERROR] Error loading {pdf_file.name}: {e}")
            
    print(f"\nTotal documents loaded: {len(all_documents)}")
    return all_documents
