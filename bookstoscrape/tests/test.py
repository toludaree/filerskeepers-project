from bs4 import BeautifulSoup
import unittest

from ..crawler import process
from ..crawler.models import Book


class TestProcess(unittest.TestCase):

    with open("./bookstoscrape/tests/page1.html", "rb") as f1:
        page1 = f1.read()
    with open("./bookstoscrape/tests/page2.html", "rb") as f2:
        page2 = f2.read()
    page1_soup = BeautifulSoup(page1, "html.parser")
    page2_soup = BeautifulSoup(page2, "html.parser")
    page1_urls = [
        "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
        "https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html",
        "https://books.toscrape.com/catalogue/soumission_998/index.html",
        "https://books.toscrape.com/catalogue/sharp-objects_997/index.html",
        "https://books.toscrape.com/catalogue/sapiens-a-brief-history-of-humankind_996/index.html",
        "https://books.toscrape.com/catalogue/the-requiem-red_995/index.html",
        "https://books.toscrape.com/catalogue/the-dirty-little-secrets-of-getting-your-dream-job_994/index.html",
        "https://books.toscrape.com/catalogue/the-coming-woman-a-novel-based-on-the-life-of-the-infamous-feminist-victoria-woodhull_993/index.html",
        "https://books.toscrape.com/catalogue/the-boys-in-the-boat-nine-americans-and-their-epic-quest-for-gold-at-the-1936-berlin-olympics_992/index.html",
        "https://books.toscrape.com/catalogue/the-black-maria_991/index.html",
        "https://books.toscrape.com/catalogue/starving-hearts-triangular-trade-trilogy-1_990/index.html",
        "https://books.toscrape.com/catalogue/shakespeares-sonnets_989/index.html",
        "https://books.toscrape.com/catalogue/set-me-free_988/index.html",
        "https://books.toscrape.com/catalogue/scott-pilgrims-precious-little-life-scott-pilgrim-1_987/index.html",
        "https://books.toscrape.com/catalogue/rip-it-up-and-start-again_986/index.html",
        "https://books.toscrape.com/catalogue/our-band-could-be-your-life-scenes-from-the-american-indie-underground-1981-1991_985/index.html",
        "https://books.toscrape.com/catalogue/olio_984/index.html",
        "https://books.toscrape.com/catalogue/mesaerion-the-best-science-fiction-stories-1800-1849_983/index.html",
        "https://books.toscrape.com/catalogue/libertarianism-for-beginners_982/index.html",
        "https://books.toscrape.com/catalogue/its-only-the-himalayas_981/index.html"

    ]
    page2_urls = [
        "https://books.toscrape.com/catalogue/the-nameless-city-the-nameless-city-1_940/index.html",
        "https://books.toscrape.com/catalogue/the-murder-that-never-was-forensic-instincts-5_939/index.html",
        "https://books.toscrape.com/catalogue/the-most-perfect-thing-inside-and-outside-a-birds-egg_938/index.html",
        "https://books.toscrape.com/catalogue/the-mindfulness-and-acceptance-workbook-for-anxiety-a-guide-to-breaking-free-from-anxiety-phobias-and-worry-using-acceptance-and-commitment-therapy_937/index.html",
        "https://books.toscrape.com/catalogue/the-life-changing-magic-of-tidying-up-the-japanese-art-of-decluttering-and-organizing_936/index.html",
        "https://books.toscrape.com/catalogue/the-inefficiency-assassin-time-management-tactics-for-working-smarter-not-longer_935/index.html",
        "https://books.toscrape.com/catalogue/the-gutsy-girl-escapades-for-your-life-of-epic-adventure_934/index.html",
        "https://books.toscrape.com/catalogue/the-electric-pencil-drawings-from-inside-state-hospital-no-3_933/index.html",
        "https://books.toscrape.com/catalogue/the-death-of-humanity-and-the-case-for-life_932/index.html",
        "https://books.toscrape.com/catalogue/the-bulletproof-diet-lose-up-to-a-pound-a-day-reclaim-energy-and-focus-upgrade-your-life_931/index.html",
        "https://books.toscrape.com/catalogue/the-art-forger_930/index.html",
        "https://books.toscrape.com/catalogue/the-age-of-genius-the-seventeenth-century-and-the-birth-of-the-modern-mind_929/index.html",
        "https://books.toscrape.com/catalogue/the-activists-tao-te-ching-ancient-advice-for-a-modern-revolution_928/index.html",
        "https://books.toscrape.com/catalogue/spark-joy-an-illustrated-master-class-on-the-art-of-organizing-and-tidying-up_927/index.html",
        "https://books.toscrape.com/catalogue/soul-reader_926/index.html",
        "https://books.toscrape.com/catalogue/security_925/index.html",
        "https://books.toscrape.com/catalogue/saga-volume-6-saga-collected-editions-6_924/index.html",
        "https://books.toscrape.com/catalogue/saga-volume-5-saga-collected-editions-5_923/index.html",
        "https://books.toscrape.com/catalogue/reskilling-america-learning-to-labor-in-the-twenty-first-century_922/index.html",
        "https://books.toscrape.com/catalogue/rat-queens-vol-3-demons-rat-queens-collected-editions-11-15_921/index.html",
    ]

    with open("./bookstoscrape/tests/book1.html", "rb") as f1:
        book1 = f1.read()
    with open("./bookstoscrape/tests/book2.html", "rb") as f2:
        book2 = f2.read()
    with open("./bookstoscrape/tests/book3.html", "rb") as f3:
        book3 = f3.read()
    with open("./bookstoscrape/tests/book4.html", "rb") as f3:
        book4 = f3.read()
    book1_soup = BeautifulSoup(book1, "html.parser")
    book2_soup = BeautifulSoup(book2, "html.parser")
    book3_soup = BeautifulSoup(book3, "html.parser")
    book4_soup = BeautifulSoup(book4, "html.parser")
    book1_article_tag = book1_soup.find("article", class_="product_page")
    book2_article_tag = book2_soup.find("article", class_="product_page")
    book4_article_tag = book4_soup.find("article", class_="product_page")

    def test__process_page_1(self):
        self.assertEqual(
            process.process_page(self.page1, "https://books.toscrape.com/"),
            (1000, self.page1_urls)
        )

    def test__process_page_2(self):
        self.assertEqual(
            process.process_page(self.page2, "https://books.toscrape.com/catalogue/page-4.html"),
            (1000, self.page2_urls)
        )

    def test__extract_total_book_count_1(self):
        self.assertEqual(
            process.extract_total_book_count(self.page1_soup),
            1000
        )

    def test__extract_total_book_count_2(self):
        self.assertEqual(
            process.extract_total_book_count(self.page2_soup),
            1000
        )

    def test__extract_book_urls_1(self):
        self.assertEqual(
            process.extract_book_urls(self.page1_soup, "https://books.toscrape.com/"),
            self.page1_urls
        )

    def test__extract_book_urls_2(self):
        self.assertEqual(
            process.extract_book_urls(self.page2_soup, "https://books.toscrape.com/catalogue/page-4.html"),
            self.page2_urls
        )

    def test__process_book_1(self):
        self.assertEqual(
            process.process_book(self.book1, 1000, "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"),
            Book(
                bts_id=1000,
                name="A Light in the Attic",
                description="It's hard to imagine a world without A Light in the Attic. This now-classic collection of poetry and drawings from Shel Silverstein celebrates its 20th anniversary with this special edition. Silverstein's humorous and creative verse can amuse the dowdiest of readers. Lemon-faced adults and fidgety kids sit still and read these rhythmic words and laugh and smile and love th It's hard to imagine a world without A Light in the Attic. This now-classic collection of poetry and drawings from Shel Silverstein celebrates its 20th anniversary with this special edition. Silverstein's humorous and creative verse can amuse the dowdiest of readers. Lemon-faced adults and fidgety kids sit still and read these rhythmic words and laugh and smile and love that Silverstein. Need proof of his genius? RockabyeRockabye baby, in the treetopDon't you know a treetopIs no safe place to rock?And who put you up there,And your cradle, too?Baby, I think someone down here'sGot it in for you. Shel, you never sounded so good. ...more",
                url="https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
                category="Poetry",
                upc="a897fe39b1053632",
                price=51.77,
                tax=0.0,
                in_stock=True,
                stock_count=22,
                review_count=0,
                cover_image_url="https://books.toscrape.com/media/cache/fe/72/fe72f0532301ec28892ae79a629a293c.jpg",
                rating=3
            )
        )
    
    def test__process_book_2(self):
        self.assertEqual(
            process.process_book(self.book2, 662, "https://books.toscrape.com/catalogue/angels-walking-angels-walking-1_662/index.html"),
            Book(
                bts_id=662,
                name="Angels Walking (Angels Walking #1)",
                description="When former national baseball star Tyler Ames suffers a career-ending injury, all he can think about is putting his life back together the way it was before. He has lost everyone he loves on his way to the big leagues. Then just when things seem to be turning around, Tyler hits rock bottom. Across the country, Tyler’s one true love Sami Dawson has moved on. A series of sma When former national baseball star Tyler Ames suffers a career-ending injury, all he can think about is putting his life back together the way it was before. He has lost everyone he loves on his way to the big leagues. Then just when things seem to be turning around, Tyler hits rock bottom. Across the country, Tyler’s one true love Sami Dawson has moved on. A series of small miracles leads Tyler to a maintenance job at a retirement home and a friendship with Virginia Hutcheson, an old woman with Alzheimer’s who strangely might have the answers he so desperately seeks.A team of Angels Walking take on the mission to restore hope for Tyler, Sami, and Virginia. Can such small and seemingly insignificant actions of the unseen bring healing and redemption? And can the words of a stranger rekindle lost love? Every journey begins with a step.It is time for the mission to begin… ...more",
                url="https://books.toscrape.com/catalogue/angels-walking-angels-walking-1_662/index.html",
                category="Add a comment",
                upc="1fbb5f786e53a0ce",
                price=34.20,
                tax=0.0,
                in_stock=True,
                stock_count=14,
                review_count=0,
                cover_image_url="https://books.toscrape.com/media/cache/ba/d9/bad95369105e8e403bf1f2b9288c5e41.jpg",
                rating=2
            )
        )
    
    def test__process_book_3(self):
        self.assertEqual(
            process.process_book(self.book3, 639, "https://books.toscrape.com/catalogue/the-lonely-city-adventures-in-the-art-of-being-alone_639/index.html"),
            Book(
                bts_id=639,
                name="The Lonely City: Adventures in the Art of Being Alone",
                description="An expertly crafted work of reportage, memoir and biography on the subject of loneliness told through the lives of iconic artists, by the acclaimed author of The Trip to Echo Spring What does it mean to be lonely? How do we live, if we're not intimately engaged with another human being? How do we connect with other people? Does technology draw us closer together or trap us An expertly crafted work of reportage, memoir and biography on the subject of loneliness told through the lives of iconic artists, by the acclaimed author of The Trip to Echo Spring What does it mean to be lonely? How do we live, if we're not intimately engaged with another human being? How do we connect with other people? Does technology draw us closer together or trap us behind screens?When Olivia Laing moved to New York City in her mid-thirties, she found herself inhabiting loneliness on a daily basis. Increasingly fascinated by this most shameful of experiences, she began to explore the lonely city by way of art. Moving fluidly between works and lives - from Edward Hopper's Nighthawks to Andy Warhol's Time Capsules, from Henry Darger's hoarding to the depredations of the AIDS crisis - Laing conducts an electric, dazzling investigation into what it means to be alone, illuminating not only the causes of loneliness but also how it might be resisted and redeemed.Humane, provocative and deeply moving, The Lonely City is about the spaces between people and the things that draw them together, about sexuality, mortality and the magical possibilities of art. It's a celebration of a strange and lovely state, adrift from the larger continent of human experience, but intrinsic to the very act of being alive. ...more",
                url="https://books.toscrape.com/catalogue/the-lonely-city-adventures-in-the-art-of-being-alone_639/index.html",
                category="Nonfiction",
                upc="582a21a1dbbef3cf",
                price=33.26,
                tax=0.0,
                in_stock=True,
                stock_count=12,
                review_count=0,
                cover_image_url="https://books.toscrape.com/media/cache/79/66/79660d2683a90670aa014cae6e02b2dc.jpg",
                rating=2
            )
        )

    def test__process_book_4(self):
        self.assertEqual(
            process.process_book(self.book4, 5, "https://books.toscrape.com/catalogue/alice-in-wonderland-alices-adventures-in-wonderland-1_5/index.html"),
            Book(
                bts_id=5,
                name="Alice in Wonderland (Alice's Adventures in Wonderland #1)",
                description=None,
                url="https://books.toscrape.com/catalogue/alice-in-wonderland-alices-adventures-in-wonderland-1_5/index.html",
                category="Classics",
                upc="cd2a2a70dd5d176d",
                price=55.53,
                tax=0.0,
                in_stock=True,
                stock_count=1,
                review_count=0,
                cover_image_url="https://books.toscrape.com/media/cache/99/df/99df494c230127c3d5ff53153d1f23a3.jpg",
                rating=1
            )
        )

    def test__extract_book_name_1(self):
        self.assertEqual(
            process.extract_book_name(self.book1_article_tag),
            "A Light in the Attic"
        )

    def test__extract_book_name_2(self):
        self.assertEqual(
            process.extract_book_name(self.book2_article_tag),
            "Angels Walking (Angels Walking #1)"
        )

    def test__extract_book_description_1(self):
        self.assertEqual(
            process.extract_book_description(self.book1_article_tag),
            "It's hard to imagine a world without A Light in the Attic. This now-classic collection of poetry and drawings from Shel Silverstein celebrates its 20th anniversary with this special edition. Silverstein's humorous and creative verse can amuse the dowdiest of readers. Lemon-faced adults and fidgety kids sit still and read these rhythmic words and laugh and smile and love th It's hard to imagine a world without A Light in the Attic. This now-classic collection of poetry and drawings from Shel Silverstein celebrates its 20th anniversary with this special edition. Silverstein's humorous and creative verse can amuse the dowdiest of readers. Lemon-faced adults and fidgety kids sit still and read these rhythmic words and laugh and smile and love that Silverstein. Need proof of his genius? RockabyeRockabye baby, in the treetopDon't you know a treetopIs no safe place to rock?And who put you up there,And your cradle, too?Baby, I think someone down here'sGot it in for you. Shel, you never sounded so good. ...more"
        )

    def test__extract_book_description_2(self):
        self.assertEqual(
            process.extract_book_description(self.book2_article_tag),
            "When former national baseball star Tyler Ames suffers a career-ending injury, all he can think about is putting his life back together the way it was before. He has lost everyone he loves on his way to the big leagues. Then just when things seem to be turning around, Tyler hits rock bottom. Across the country, Tyler’s one true love Sami Dawson has moved on. A series of sma When former national baseball star Tyler Ames suffers a career-ending injury, all he can think about is putting his life back together the way it was before. He has lost everyone he loves on his way to the big leagues. Then just when things seem to be turning around, Tyler hits rock bottom. Across the country, Tyler’s one true love Sami Dawson has moved on. A series of small miracles leads Tyler to a maintenance job at a retirement home and a friendship with Virginia Hutcheson, an old woman with Alzheimer’s who strangely might have the answers he so desperately seeks.A team of Angels Walking take on the mission to restore hope for Tyler, Sami, and Virginia. Can such small and seemingly insignificant actions of the unseen bring healing and redemption? And can the words of a stranger rekindle lost love? Every journey begins with a step.It is time for the mission to begin… ...more"
        )

    def test__extract_book_description_3(self):
        self.assertEqual(
            process.extract_book_description(self.book4_article_tag),
            None
        )

    def test__extract_book_category_1(self):
        self.assertEqual(
            process.extract_book_category(self.book1_soup),
            "Poetry"
        )

    def test__extract_book_category_2(self):
        self.assertEqual(
            process.extract_book_category(self.book2_soup),
            "Add a comment"
        )

    def test__extract_td_given_th_1(self):
        self.assertEqual(
            process.extract_td_given_th(self.book1_article_tag.table, "Number of reviews"),
            "0"
        )
    
    def test__extract_td_given_th_2(self):
        self.assertEqual(
            process.extract_td_given_th(self.book1_article_tag.table, "Price (incl. tax)"),
            "£51.77"
        )

    def test__extract_upc_1(self):
        self.assertEqual(
            process.extract_upc(self.book1_article_tag.table),
            "a897fe39b1053632"
        )

    def test__extract_upc_2(self):
        self.assertEqual(
            process.extract_upc(self.book2_article_tag.table),
            "1fbb5f786e53a0ce"
        )

    def test__extract_price_1(self):
        self.assertEqual(
            process.extract_price(self.book1_article_tag.table),
            51.77
        )

    def test__extract_price_2(self):
        self.assertEqual(
            process.extract_price(self.book2_article_tag.table),
            34.20
        )

    def test__extract_tax_1(self):
        self.assertEqual(
            process.extract_tax(self.book1_article_tag.table),
            0.0
        )

    def test__extract_tax_2(self):
        self.assertEqual(
            process.extract_tax(self.book2_article_tag.table),
            0.0
        )

    def test__extract_availability_1(self):
        self.assertEqual(
            process.extract_availability(self.book1_article_tag.table),
            "In stock (22 available)"
        )

    def test__extract_availability_2(self):
        self.assertEqual(
            process.extract_availability(self.book2_article_tag.table),
            "In stock (14 available)"
        )

    def test__extract_review_count_1(self):
        self.assertEqual(
            process.extract_review_count(self.book1_article_tag.table),
            0
        )

    def test__extract_review_count_2(self):
        self.assertEqual(
            process.extract_review_count(self.book2_article_tag.table),
            0
        )

    def test__extract_cover_image_1(self):
        self.assertEqual(
            process.extract_cover_image(self.book1_article_tag, "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"),
            "https://books.toscrape.com/media/cache/fe/72/fe72f0532301ec28892ae79a629a293c.jpg"
        )

    def test__extract_cover_image_2(self):
        self.assertEqual(
            process.extract_cover_image(self.book2_article_tag, "https://books.toscrape.com/catalogue/angels-walking-angels-walking-1_662/index.html"),
            "https://books.toscrape.com/media/cache/ba/d9/bad95369105e8e403bf1f2b9288c5e41.jpg"
        )

    def test__extract_book_rating_1(self):
        self.assertEqual(
            process.extract_book_rating(self.book1_article_tag),
            "Three"
        )

    def test__extract_book_rating_2(self):
        self.assertEqual(
            process.extract_book_rating(self.book2_article_tag),
            "Two"
        )
