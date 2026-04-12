# src/lex_rs/parser.py
from cyrtranslit import to_latin  # pyright: ignore[reportMissingTypeStubs, reportUnknownVariableType]
from typing import cast

from .models import Law, Article, Paragraph, Point

def _all_upper_but_J(line : str) -> bool:
    ret_val = True
    for char in line:
        if char.isalpha() and char != "j":
            if not char.isupper():
                ret_val = False
    return ret_val

def _parse_law_name(txt: str):
    if txt:
        return txt.splitlines()[0].split(":")[-1].strip()
    else:
        return ""

def _parse_publication(txt: str):
    start_liners = [
        "Službeni glasnik RS", 
        "Službeni glasnik SRS", 
        "Službeni list SRJ", 
        "Službeni list SFRJ",
        ]
     
    for line in txt.splitlines():
        for start_word in start_liners:
            if line[1:].startswith(start_word):
                full_publication = line.split(",")[-1].strip()
                short_publication: str | None = None
                for word_idx, word in enumerate(full_publication.split()):
                    if word.isnumeric():
                        short_publication = full_publication.split()[word_idx]+"/"+full_publication.split()[word_idx+4]
                        break
                if short_publication is None: return full_publication
                while not short_publication[-1].isnumeric(): short_publication = short_publication[:-1]
                return short_publication
    return ""


def parse(txt: str) -> Law:
    """Parsira tekst i vraća listu članova"""
    
    law: Law = Law()
    
    # Konvertuj u latinicu
    latin_txt: str = cast(str, to_latin(string_to_transliterate=txt))
    
    # Očisti tekst
    latin_txt = latin_txt.strip("\n")
    latin_txt = '\n'.join([line.strip() for line in latin_txt.splitlines() if line.strip()])

    law.name = _parse_law_name(latin_txt)
    law.last_publication = _parse_publication(latin_txt)
    
    # Dodaj novu liniju pre svakog "Član" za lakše parsiranje
    latin_txt = latin_txt.replace("Član ", "\nČlan ")
    
    # Inicijalizacija
    current_article: Article | None = None
    current_paragraph: Paragraph | None = None
    
    for line_num, line in enumerate(latin_txt.splitlines()):
        if not line or line.startswith("*") or line.isupper() or _all_upper_but_J(line) or (line[0].isdigit() and line[1] == "."):
            # Proveri da li je linija ODDREDBE KOJE NISU UNETE U
            if line.startswith("ODREDBE KOJE NISU UNETE U"):
                break
            continue
        
        # Proveri da li je linija Član
        if line.startswith("Član "):
            # Sačuvaj prethodni član ako postoji
            if current_article is not None:
                if current_paragraph is not None:
                    current_article.append_paragraph(current_paragraph)
                    current_paragraph = None
                law.articles.append(current_article)
            
            # Kreiraj novi član
            article_number = line.replace("Član", "").strip()
            if article_number.endswith("."):
                article_number = article_number[:-1]
            
            current_article = Article(number=article_number, line=line_num)
            current_paragraph = None
        
        # Proveri da li je linija paragraf (počinje brojem)
        elif line and line[0].isdigit():
            # Ovo je tačka unutar paragrafa
            if current_paragraph is None:
                # Ako nema paragrafa, kreiraj jedan
                current_paragraph = Paragraph(line=line_num, text="")
            
            if current_paragraph.text and current_paragraph.text.endswith(":"):
                open_paren = line.find(")")
                number = line[:open_paren]
                point = Point(number=number,line=line_num, text=line[open_paren+2:])
                current_paragraph.append_point(point)
        
        # Inače, ovo je tekst paragrafa
        elif line and (not line[len(line)-1:].isalpha() or line.endswith(" ili")):
            # Sačuvaj prethodni paragraf ako postoji
            if current_paragraph is not None and current_article is not None:
                current_article.append_paragraph(current_paragraph)
            
            # Kreiraj novi paragraf
            current_paragraph = Paragraph(line=line_num, text=line)
    
    # Dodaj poslednji paragraf i član nakon petlje
    if current_paragraph is not None and current_article is not None:
        current_article.append_paragraph(current_paragraph)
    
    if current_article is not None:
        law.articles.append(current_article)
    
    return law

__all__ = ['parse']