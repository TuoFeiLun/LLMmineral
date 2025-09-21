"""
@Author      : Yujia LI <ituofeilun@qq.com>
@Created     : 2025/09/21 19:46  
@ModifiedBy  : Yujia LI
@Description : ${write description}
@Version     : 0.0.1
@License     : None
"""
from llama_index.core.readers.base import BaseReader
from llama_index.core import Document

from typing import List, Dict
import os
import re
import hashlib

class QLDStratigraphicReader(BaseReader):
    def load_data(self, file: str, extra_info: Dict = None) -> List[Document]:
        """Load QLD Stratigraphic TXT data (pipe-delimited) into Documents.

        This reader is tailored for the datasets under `datastore/sourcedata/QLDCurrent` and
        `datastore/sourcedata/QLDNotcurrent`, which are pipe-delimited text files with a header row.
        """
        documents: List[Document] = []

        try:
            with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                # Keep only non-empty lines
                raw_lines = [ln.rstrip("\n\r") for ln in f]
            lines = [ln for ln in raw_lines if ln and ln.strip()]
        except Exception as exc:
            print(f"Failed to open file {file}: {exc}")
            return documents

        if not lines:
            return documents

        # Parse header
        header_line = lines[0]
        headers = [h.strip().strip('"') for h in header_line.split('|')]
        num_headers = len(headers)

        # Infer status/topic from filename
        file_name = os.path.basename(file)
        lower_name = file_name.lower()
        if 'not current' in lower_name:
            qld_status = 'not_current'
        elif 'current' in lower_name:
            qld_status = 'current'
        else:
            qld_status = 'unknown'

        if 'name' in lower_name:
            qld_topic = 'names'
        elif 'definition' in lower_name:
            qld_topic = 'definition'
        elif 'reference' in lower_name:
            qld_topic = 'references'
        elif 'article' in lower_name:
            qld_topic = 'articles'
        else:
            qld_topic = 'general'

        # Utility to get a value by multiple possible header aliases
        def get_alias(row_dict: Dict, *candidates: str) -> str:
            for key in candidates:
                if key in row_dict and str(row_dict[key]).strip() != "":
                    return str(row_dict[key]).strip()
            return ""

        # Build documents row by row
        for row_index, line in enumerate(lines[1:], start=1):
            cols = [c.strip().strip('"') for c in line.split('|')]

            # Normalize column count
            if len(cols) < num_headers:
                cols += [''] * (num_headers - len(cols))
            elif len(cols) > num_headers:
                cols = cols[:num_headers]

            row_dict = dict(zip(headers, cols))

            # Extract common fields
            stratno = get_alias(row_dict, 'Stratno', 'Strat No', 'Strat No.')
            strat_name = get_alias(row_dict, 'Stratigraphic Name', 'Name')
            usage_no = get_alias(row_dict, 'Usage No', 'UsageNo')
            ref_id = get_alias(row_dict, 'Reference Id', 'ReferenceId', 'Ref Id')
            page_raw = get_alias(row_dict, 'Page Number', 'PageNumber', 'Page')

            # Extract numeric page, if present
            page_match = re.search(r"\d+", page_raw) if page_raw else None
            page_number = int(page_match.group()) if page_match else None

            # Compose compact, informative text for embedding
            preferred_keys = [
                'Stratigraphic Name', 'Stratno', 'Category', 'Rank', 'Status',
                'Usage', 'Parent Name', 'Parent Stratno', 'Lithology Description',
                'Primary Lithology Group', 'Secondary Lithology Group', 'Lithology',
                'Minimum Age Name', 'Maximum Age Name', 'Top Minimum Age Name',
                'Base Maximum Age Name', 'Numerical Age', 'Type Section State',
                'Definition Card', 'Contents'
            ]

            text_lines: List[str] = []
            # Always surface name first if present
            if strat_name:
                text_lines.append(f"Stratigraphic Name: {strat_name}")
            if stratno:
                text_lines.append(f"Stratno: {stratno}")

            seen_keys = set(['Stratigraphic Name', 'Stratno'])
            for key in preferred_keys:
                if key in seen_keys:
                    continue
                val = row_dict.get(key)
                if val is not None and str(val).strip() != "":
                    text_lines.append(f"{key}: {val}")
                    seen_keys.add(key)

            # Append remaining non-empty fields, excluding those already included
            for key, val in row_dict.items():
                if key in seen_keys:
                    continue
                if val is not None and str(val).strip() != "":
                    text_lines.append(f"{key}: {val}")
            text = "\n".join(text_lines) if text_lines else "Empty row"

            # Build compact metadata: only essential fields, truncate long values
            allowed_meta_keys = [
                'Stratigraphic Name', 'Stratno', 'Category', 'Rank', 'Status', 'Usage',
                'Parent Name', 'Parent Stratno', 'Primary Lithology Group', 'Secondary Lithology Group',
                'Minimum Age Name', 'Maximum Age Name', 'Top Minimum Age Name', 'Base Maximum Age Name',
                'Numerical Age', 'Type Section State', 'Reference Id', 'Usage No', 'Last Update'
            ]

            def truncate_value(value: str, max_len: int = 120) -> str:
                value = (value or "").strip()
                return value if len(value) <= max_len else value[: max_len - 3] + "..."

            filtered_meta: Dict = {}
            for key in allowed_meta_keys:
                if key in row_dict and str(row_dict[key]).strip() != "":
                    filtered_meta[key] = truncate_value(str(row_dict[key]))

            metadata: Dict = {
                "file_name": file_name,
                "file_path": file,
                "file_type": "txt",
                "qld_status": qld_status,
                "qld_topic": qld_topic,
                "row_index": row_index,
                "page_number": page_number,
            }
            metadata.update(filtered_meta)
            if extra_info:
                metadata.update(extra_info)

            # Stable document id
            stable_key = "|".join([
                file_name,
                stratno or "",
                strat_name or "",
                ref_id or "",
                usage_no or "",
                str(page_number) if page_number is not None else "",
                str(row_index),
            ])
            doc_id = hashlib.md5(stable_key.encode("utf-8")).hexdigest()

            documents.append(Document(text=text, metadata=metadata, doc_id=doc_id))

        return documents
