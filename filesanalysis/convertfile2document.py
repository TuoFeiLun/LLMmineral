from llama_index.core import Document
from llama_index.core.readers.base import BaseReader
from typing import List
import pandas as pd
import os

class CSVReader(BaseReader):
    """CSV file reader class - compatible with LlamaIndex interface"""
    
    def load_data(self, file: str, extra_info: dict = None) -> List[Document]:
        """Load CSV file data"""
        try:
            df = pd.read_csv(file)
            
            # Convert DataFrame to text
            content = f"CSV file: {os.path.basename(file)}\n"
            content += f"Columns: {', '.join(df.columns.tolist())}\n"
            content += f"Rows: {len(df)}\n\n"
            
            # Check for geological related columns
            geo_keywords = ['depth', 'formation', 'lithology', 'well', 'log', 'gamma', 'epm', 'permit', 'mineral']
            geo_columns = [col for col in df.columns if any(keyword.lower() in col.lower() for keyword in geo_keywords)]
            
            if geo_columns:
                content += f"Geological columns: {', '.join(geo_columns)}\n\n"
            
            # Add data content
            content += "Data content:\n"
            content += df.to_string(max_rows=100)  # Limit displayed rows
            
            # If too much data, add statistical information
            if len(df) > 100:
                content += f"\n\n... (showing first 100 rows, total {len(df)} rows)"
                content += "\n\nData statistics:\n"
                content += df.describe().to_string()
            
            # Create metadata
            metadata = {
                "file_name": os.path.basename(file),
                "file_type": "csv",
                "rows": len(df),
                "columns": len(df.columns),
                "geo_columns": ", ".join(geo_columns) if geo_columns else ""
            }
            
            if extra_info:
                metadata.update(extra_info)
            
            return [Document(text=content, metadata=metadata)]
            
        except Exception as e:
            print(f"Failed to read CSV file {file}: {e}")
            return []

class XLSXReader(BaseReader):
    """XLSX file reader class - compatible with LlamaIndex interface"""
    
    def load_data(self, file: str, extra_info: dict = None) -> List[Document]:
        """Load XLSX file data"""
        try:
            # Read all worksheets
            excel_file = pd.ExcelFile(file)
            documents = []
            
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(file, sheet_name=sheet_name)
                
                if df.empty:
                    print(f"Worksheet '{sheet_name}' is empty, skipping")
                    continue
                
                # Convert each worksheet to document
                content = f"Excel file: {os.path.basename(file)}\n"
                content += f"Worksheet: {sheet_name}\n"
                content += f"Columns: {', '.join(df.columns.astype(str).tolist())}\n"
                content += f"Rows: {len(df)}\n\n"
                
                # Check geological related content
                geo_keywords = ['depth', 'formation', 'lithology', 'well', 'log', 'gamma', 'mineral', 'soil']
                geo_columns = [col for col in df.columns if any(keyword.lower() in str(col).lower() for keyword in geo_keywords)]
                
                if geo_columns:
                    content += f"Geological columns: {', '.join(geo_columns)}\n\n"
                
                # Add data content
                content += "Data content:\n"
                content += df.to_string(max_rows=100)
                
                if len(df) > 100:
                    content += f"\n\n... (showing first 100 rows, total {len(df)} rows)"
                    content += "\n\nData statistics:\n"
                    content += df.describe().to_string()
                
                # Create metadata
                metadata = {
                    "file_name": os.path.basename(file),
                    "file_type": "xlsx",
                    "sheet_name": sheet_name,
                    "rows": len(df),
                    "columns": len(df.columns),
                    "geo_columns": ", ".join(geo_columns) if geo_columns else ""
                }
                
                if extra_info:
                    metadata.update(extra_info)
                
                doc = Document(text=content, metadata=metadata)
                documents.append(doc)
            
            return documents
            
        except Exception as e:
            print(f"Failed to read XLSX file {file}: {e}")
            return []





if __name__ == "__main__":
    # Create reader instances for external use
    csv_reader = CSVReader()
    xlsx_reader = XLSXReader()

    # Keep original function interface for compatibility with existing code
    def csv_reader_func(file_path):
        """Compatibility function"""
        return csv_reader.load_data(file_path)

    def xlsx_reader_func(file_path):
        """Compatibility function"""
        return xlsx_reader.load_data(file_path)

    # Test CSV reader
    print("Testing CSV reader...")
    csv_docs = csv_reader.load_data("/Users/yjli/QUTIT/semester4/ifn712/datacollect/databytype/csv/EPM application_wkid_GDA 2020.csv")
    print(f"CSV document count: {len(csv_docs)}")
    if csv_docs:
        print(f"First document content preview: {csv_docs[0].text[:200]}...")
    
    # Test XLSX reader
    print("\nTesting XLSX reader...")
    xlsx_docs = xlsx_reader.load_data("/Users/yjli/QUTIT/semester4/ifn712/datacollect/databytype/xlsx/cr_3546_25 Soil data entry v2.xlsx")
    print(f"XLSX document count: {len(xlsx_docs)}")
    if xlsx_docs:
        print(f"First document content preview: {xlsx_docs[0].text[:200]}...")
    
    print("✅ Testing completed")
 