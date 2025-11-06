import unittest

from ..crawler.models import Book
from ..crawler.process import process_page, process_book


class TestProcess(unittest.TestCase):

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

    def test__process_page_1(self):
        with open("./bookstoscrape/tests/page1.html", "rb") as f1:
            page1 = f1.read()
        self.assertEqual(process_page(page1, "https://books.toscrape.com/"), self.page1_urls)

    def test__process_page_2(self):
        with open("./bookstoscrape/tests/page2.html", "rb") as f2:
            page2 = f2.read()
        self.assertEqual(process_page(page2, "https://books.toscrape.com/catalogue/page-4.html"), self.page2_urls)

    def test__process_book_1(self):
        with open("./bookstoscrape/tests/book1.html", "rb") as f1:
            book1 = f1.read()
        self.assertEqual(
            process_book(book1, "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"),
            Book(
                id=1000,
                name="A Light in the Attic",
                description="It's hard to imagine a world without A Light in the Attic. This now-classic collection of poetry and drawings from Shel Silverstein celebrates its 20th anniversary with this special edition. Silverstein's humorous and creative verse can amuse the dowdiest of readers. Lemon-faced adults and fidgety kids sit still and read these rhythmic words and laugh and smile and love th It's hard to imagine a world without A Light in the Attic. This now-classic collection of poetry and drawings from Shel Silverstein celebrates its 20th anniversary with this special edition. Silverstein's humorous and creative verse can amuse the dowdiest of readers. Lemon-faced adults and fidgety kids sit still and read these rhythmic words and laugh and smile and love that Silverstein. Need proof of his genius? RockabyeRockabye baby, in the treetopDon't you know a treetopIs no safe place to rock?And who put you up there,And your cradle, too?Baby, I think someone down here'sGot it in for you. Shel, you never sounded so good. ...more",
                category="Poetry",
                price_including_tax=51.77,
                price_excluding_tax=51.77,
                in_stock=True,
                stock_count=22,
                review_count=0,
                cover_image_url="https://books.toscrape.com/media/cache/fe/72/fe72f0532301ec28892ae79a629a293c.jpg",
                rating=3
            )
        )
    
    def test__process_book_2(self):
        with open("./bookstoscrape/tests/book2.html", "rb") as f2:
            book2 = f2.read()
        self.assertEqual(
            process_book(book2, "https://books.toscrape.com/catalogue/angels-walking-angels-walking-1_662/index.html"),
            Book(
                id=662,
                name="Angels Walking (Angels Walking #1)",
                description="When former national baseball star Tyler Ames suffers a career-ending injury, all he can think about is putting his life back together the way it was before. He has lost everyone he loves on his way to the big leagues. Then just when things seem to be turning around, Tyler hits rock bottom. Across the country, Tyler’s one true love Sami Dawson has moved on. A series of sma When former national baseball star Tyler Ames suffers a career-ending injury, all he can think about is putting his life back together the way it was before. He has lost everyone he loves on his way to the big leagues. Then just when things seem to be turning around, Tyler hits rock bottom. Across the country, Tyler’s one true love Sami Dawson has moved on. A series of small miracles leads Tyler to a maintenance job at a retirement home and a friendship with Virginia Hutcheson, an old woman with Alzheimer’s who strangely might have the answers he so desperately seeks.A team of Angels Walking take on the mission to restore hope for Tyler, Sami, and Virginia. Can such small and seemingly insignificant actions of the unseen bring healing and redemption? And can the words of a stranger rekindle lost love? Every journey begins with a step.It is time for the mission to begin… ...more",
                category="Add a comment",
                price_including_tax=34.20,
                price_excluding_tax=34.20,
                in_stock=True,
                stock_count=14,
                review_count=0,
                cover_image_url="https://books.toscrape.com/media/cache/ba/d9/bad95369105e8e403bf1f2b9288c5e41.jpg",
                rating=2
            )
        )
    
    def test__process_book_3(self):
        with open("./bookstoscrape/tests/book3.html", "rb") as f3:
            book3 = f3.read()
        self.assertEqual(
            process_book(book3, "https://books.toscrape.com/catalogue/the-lonely-city-adventures-in-the-art-of-being-alone_639/index.html"),
            Book(
                id=639,
                name="The Lonely City: Adventures in the Art of Being Alone",
                description="An expertly crafted work of reportage, memoir and biography on the subject of loneliness told through the lives of iconic artists, by the acclaimed author of The Trip to Echo Spring What does it mean to be lonely? How do we live, if we're not intimately engaged with another human being? How do we connect with other people? Does technology draw us closer together or trap us An expertly crafted work of reportage, memoir and biography on the subject of loneliness told through the lives of iconic artists, by the acclaimed author of The Trip to Echo Spring What does it mean to be lonely? How do we live, if we're not intimately engaged with another human being? How do we connect with other people? Does technology draw us closer together or trap us behind screens?When Olivia Laing moved to New York City in her mid-thirties, she found herself inhabiting loneliness on a daily basis. Increasingly fascinated by this most shameful of experiences, she began to explore the lonely city by way of art. Moving fluidly between works and lives - from Edward Hopper's Nighthawks to Andy Warhol's Time Capsules, from Henry Darger's hoarding to the depredations of the AIDS crisis - Laing conducts an electric, dazzling investigation into what it means to be alone, illuminating not only the causes of loneliness but also how it might be resisted and redeemed.Humane, provocative and deeply moving, The Lonely City is about the spaces between people and the things that draw them together, about sexuality, mortality and the magical possibilities of art. It's a celebration of a strange and lovely state, adrift from the larger continent of human experience, but intrinsic to the very act of being alive. ...more",
                category="Nonfiction",
                price_including_tax=33.26,
                price_excluding_tax=33.26,
                in_stock=True,
                stock_count=12,
                review_count=0,
                cover_image_url="https://books.toscrape.com/media/cache/79/66/79660d2683a90670aa014cae6e02b2dc.jpg",
                rating=2
            )
        )        
