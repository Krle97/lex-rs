# tests/test_parser.py
import pytest  # pyright: ignore[reportUnusedImport]
from lex_rs.parser import parse, Article, Paragraph, Point  # pyright: ignore[reportUnusedImport]


class TestParse:
    """Testovi za parse funkciju"""
    
    def test_parse_single_article(self):
        """Test parsiranja jednog člana"""
        text = """Član 1.
Prvi paragraf."""
        
        articles = parse(text)
        
        assert len(articles) == 1
        assert articles[0].number == "1"
        assert len(articles[0].paragraphs) == 1
        assert articles[0].paragraphs[0].text == "Prvi paragraf."
    
    def test_parse_article_with_points(self):
        """Test parsiranja člana sa tačkama"""
        text = """Član 1.
Prvi paragraf:
1) Prva tačka.
2) Druga tačka.
Drugi paragraf."""
        
        articles = parse(text)
        
        assert len(articles) == 1
        assert len(articles[0].paragraphs) == 2
        
        # Provera prvog paragrafa i tačaka
        p1 = articles[0].paragraphs[0]
        assert p1.text == "Prvi paragraf:"
        assert len(p1.points) == 2
        assert  p1.points[0].text == "Prva tačka."
        assert  p1.points[1].text == "Druga tačka."
        
        # Provera drugog paragrafa
        p2 = articles[0].paragraphs[1]
        assert p2.text == "Drugi paragraf."
        assert len(p2.points) == 0
    
    def test_parse_multiple_articles(self):
        """Test parsiranja više članova"""
        text = """Član 1.
Prvi član
Član 2.
Drugi član
Član 3.
Treći član"""
        
        articles = parse(text)
        
        assert len(articles) == 3
        assert articles[0].number == "1"
        assert articles[1].number == "2"
        assert articles[2].number == "3"
    
    def test_parse_with_roman_numerals(self):
        """Test parsiranja sa rimskim brojevima (treba da se preskoče)"""
        text = """II. ZASNIVANJE RADNOG ODNOSA
Član 1.
Prvi paragraf"""
        
        articles = parse(text)
        
        # Rimski broj treba da bude preskočen, samo član se parsira
        assert len(articles) == 1
        assert articles[0].number == "1"
    
    def test_parse_with_uppercase_section(self):
        """Test parsiranja sa naslovom velikim slovima (treba da se preskoči)"""
        text = """OPŠTE ODREDBE
Član 1.
Prvi paragraf"""
        
        articles = parse(text)
        
        assert len(articles) == 1
        assert articles[0].number == "1"
    
    def test_parse_empty_text(self):
        """Test sa praznim tekstom"""
        articles = parse("")
        
        assert articles == []
    
    def test_parse_without_articles(self):
        """Test teksta bez članova"""
        text = """Ovo je običan tekst
bez ikakvih članova"""
        
        articles = parse(text)
        
        assert articles == []
    
    def test_parse_article_number_with_dot(self):
        """Test člana sa tačkom u broju"""
        text = """Član 1a.
Prvi paragraf"""
        
        articles = parse(text)
        
        assert len(articles) == 1
        assert articles[0].number == "1a"
    
    def test_parse_article_with_colon_in_paragraph(self):
        """Test paragrafa koji se završava sa dvotačkom"""
        text = """Član 1.
Paragraf sa dvotačkom:
1) Prva tačka
2) Druga tačka"""
        
        articles = parse(text)
        
        assert len(articles) == 1
        p1 = articles[0].paragraphs[0]
        assert p1.text == "Paragraf sa dvotačkom:"
        assert len(p1.points) == 2

    def test_parse_real_text_1(self):
        text = """Члан 14.

Уговором о раду или одлуком послодавца може се утврдити учешће запосленог у добити оствареној у пословној години, у складу са законом и општим актом.

2) Обавезе запослених

Члан 15.

Запослени је дужан:

1) да савесно и одговорно обавља послове на којима ради;

2) да поштује организацију рада и пословања код послодавца, као и услове и правила послодавца у вези са испуњавањем уговорних и других обавеза из радног односа;

3) да обавести послодавца о битним околностима које утичу или би могле да утичу на обављање послова утврђених уговором о раду;

4) да обавести послодавца о свакој врсти потенцијалне опасности за живот и здравље и настанак материјалне штете.

3) Обавезе послодавца"""
        articles = parse(text)

        article1 = articles[0]
        article2 = articles[1]

        assert len(articles) == 2
        assert len(article1.paragraphs) == 1
        assert article1.paragraphs[0].text == "Ugovorom o radu ili odlukom poslodavca može se utvrditi učešće zaposlenog u dobiti ostvarenoj u poslovnoj godini, u skladu sa zakonom i opštim aktom."

        assert len(article2.paragraphs) == 1
        assert len(article2.paragraphs[0].points) == 5
        assert article2.paragraphs[0].points[4].text == "Obaveze poslodavca"

    def test_parse_real_text_2(self):
        text = """Члан 276а

Пропуштање прописаног рока за подношење јединствене пријаве на обавезно социјално осигурање (члан 35. став 2), представља прекршај за који се изриче новчана казна прописана чланом 31. Закона о Централном регистру обавезног социјалног осигурања („Службени гласник РС”, бр. 30/10, 44/14 – др. закон и 116/14).

*Службени гласник РС, број 113/2017

ХХIII. ПРЕЛАЗНЕ И ЗАВРШНЕ ОДРЕДБЕ"""
        articles = parse(text)

        article1 = articles[0]

        assert len(articles) == 1
        assert len(article1.paragraphs) == 1
        assert article1.number == "276a"
        assert article1.paragraphs[0].text == "Propuštanje propisanog roka za podnošenje jedinstvene prijave na obavezno socijalno osiguranje (član 35. stav 2), predstavlja prekršaj za koji se izriče novčana kazna propisana članom 31. Zakona o Centralnom registru obaveznog socijalnog osiguranja („Službeni glasnik RS”, br. 30/10, 44/14 – dr. zakon i 116/14)."


    def test_parse_real_text_3(self):
        text = """Члан 11.

Ништавост одредаба уговора о раду утврђује се пред надлежним судом.

Право да се захтева утврђивање ништавости не застарева.

4. Основна права и обавезе

1) Права запослених

Члан 12.

Запослени има право на одговарајућу зараду, безбедност и здравље на раду, здравствену заштиту, заштиту личног интегритета, достојанство личности и друга права у случају болести, смањења или губитка радне способности и старости, материјално обезбеђење за време привремене незапослености, као и право на друге облике заштите, у складу са законом и општим актом, односно уговором о раду.

Запослена жена има право на посебну заштиту за време трудноће и порођаја.

Запослени има право на посебну заштиту ради неге детета, у складу са овим законом.

Запослени млађи од 18 година живота и запослена особа са инвалидитетом имају право на посебну заштиту, у складу са законом.

*Службени гласник РС, број 75/2014"""
        articles = parse(text)

        article1 = articles[0]
        article2 = articles[1]

        assert len(articles) == 2
        assert len(article1.paragraphs) == 2
        assert article1.paragraphs[1].text == "Pravo da se zahteva utvrđivanje ništavosti ne zastareva."

        assert len(article2.paragraphs) == 4
        assert article2.paragraphs[2].text == "Zaposleni ima pravo na posebnu zaštitu radi nege deteta, u skladu sa ovim zakonom."