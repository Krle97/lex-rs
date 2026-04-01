# src/lex_rs/parser.py
from dataclasses import dataclass, field
from cyrtranslit import to_latin  # pyright: ignore[reportMissingTypeStubs, reportUnknownVariableType]
from typing import cast, override

@dataclass
class Point:
    number: str | None = None
    line: int | None = None
    text: str | None = None

    @override
    def __str__(self) -> str:
        return f"  \t{self.number}) {self.text}"

@dataclass
class Paragraph:
    number: int | None = None
    line: int | None = None
    text: str | None = None
    points: list[Point] = field(default_factory=list)
    _point_index: int = field(default=0, init=False) 

    def _increase_point_index(self) -> int:
        self._point_index += 1
        return self._point_index

    def reset_paragraph(self) -> None:
        self.number = None
        self.line = None
        self.text = None
        self.points.clear()
        self._point_index = 0

    def append_point(self, point: Point) -> None:
        # point.number = self._increase_point_index()
        self.points.append(point)

    @override
    def __str__(self) -> str:
        lines: list[str] = []
        lines.append(f"  {self.number}. {self.text}" if self.number else f"  (?) {self.text}")
        
        for point in self.points:
            lines.append(str(point))
        
        return "\n".join(lines)


@dataclass
class Article:
    number: str | None = None
    line: int | None = None
    paragraphs: list[Paragraph] = field(default_factory=list)
    _paragraph_index: int = field(default=0, init=False)

    def _increase_paragraph_index(self) -> int:
        self._paragraph_index += 1
        return self._paragraph_index

    def reset_article(self) -> None:
        self.number = None
        self.line = None
        self.paragraphs.clear() 
        self._paragraph_index = 0

    def append_paragraph(self, paragraph: Paragraph) -> None:
        paragraph.number = self._increase_paragraph_index()
        self.paragraphs.append(paragraph)

    @override
    def __str__(self) -> str:
        if self.number is None:
            return "Nepotpun član"
        
        lines: list[str] = [f"Član {self.number}."]
        
        for paragraph in self.paragraphs:
            lines.append(str(paragraph))
        
        return "\n".join(lines)

def _all_upper_but_J(line : str) -> bool:
    ret_val = True
    for char in line:
        if char.isalpha() and char != "j":
            if not char.isupper():
                ret_val = False
    return ret_val


def parse(txt: str) -> list[Article]:
    """Parsira tekst i vraća listu članova"""
    
    articles: list[Article] = []
    
    # Konvertuj u latinicu
    latin_txt: str = cast(str, to_latin(string_to_transliterate=txt))
    
    # Očisti tekst
    latin_txt = latin_txt.strip("\n")
    latin_txt = '\n'.join([line.strip() for line in latin_txt.splitlines() if line.strip()])
    
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
                articles.append(current_article)
            
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
        articles.append(current_article)
    
    return articles

    __all__ = ['parse', 'Article', 'Paragraph', 'Point']  # pyright: ignore[reportUnreachable]