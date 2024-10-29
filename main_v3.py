import pymupdf, re, json

def parse_pdf_structure(pdf_path):
    with pymupdf.open(pdf_path) as pdf:
        book_structure = {}
        chapter = None
        section = None

        for page_num in range(3, pdf.page_count - 348): # pdf_page_count, только где содержание
            page = pdf[page_num]
            text = page.get_text("text")

            lines = text.splitlines()
            for i, line in enumerate(lines):
                line = line.strip()

                if line.lower().startswith("оглавление"):
                    continue


                # remove the лишние точки
                # print(line)
                line = re.sub(r"\.{2,}", "", line).strip()
                # print(line)

                chapter_match = re.match(r"^Глава\s+(\d+)\s*$", line)
                
                # section_match = re.match(r"^(\d+\.\d+)\s+(.+?)\s*\d*$", line)
                # не видит когда 2.1.
                # section_match = re.match(r"^(\d+\.\d+)(?:\.\s+)?(.+?)\s*\d*$", line)
                # не помогло 🙄
                # section_match = re.match(r"^(\d+\.\d+\.\s*)?(.+?)\s*\d*$", line)
                # теперь только видим когда есть точки после номеров 
                # section_match = re.match(r"^(\d+\.\d+\.)?\s+(.+?)\s*\d*$", line)
                # к черту 😒
                section_match = re.match(r"^(\d+\.\d+\.?)\s+(.+?)\s*\d*$", line)
                # о боже наконец то, 90% времени ушло на это
                
                
                subsection_match = re.match(r"^(\d+\.\d+\.\d+)\s+(.+?)\s*\d*$", line)

                if chapter_match:
                    chapter_number = chapter_match.group(1)
                    chapter = chapter_number
                    chapter_name = lines[i+2].strip()
                    chapter_name = re.sub(r"\.{2,}", "", chapter_name).strip()
                    chapter_name = chapter_name.rstrip("0123456789").strip()
                    book_structure[chapter] = {"title": f"{chapter_name}", "sections": {}}
                    section = None
                elif section_match and chapter:
                    # print(section_match)
                    section_key = section_match.group(1)
                    # print(section_match.group(1))
                    section_title = section_match.group(2).strip()
                    book_structure[chapter]["sections"][section_key] = {"title": section_title, "subsections": {}}
                    section = section_key
                elif subsection_match and chapter and section:
                    subsection_key = subsection_match.group(1).rstrip('.')
                    subsection_title = subsection_match.group(2).strip()
                    book_structure[chapter]["sections"][section]["subsections"][subsection_key] = subsection_title
                

        book_structure = {k: v for k, v in book_structure.items() if v} # clear

        return book_structure

def save_structure_to_json(structure, output_file="structure.json"):
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(structure, f, ensure_ascii=False, indent=4)


pdf_path = "Руководство_Бухгалтерия_для_Узбекистана_ред_3_0.pdf"
structure = parse_pdf_structure(pdf_path)
save_structure_to_json(structure)
