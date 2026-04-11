from dataclasses import dataclass, field
from typing import override

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

__all__ = ['Article', 'Paragraph', 'Point']