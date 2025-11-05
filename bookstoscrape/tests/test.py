import unittest

from ..crawler.process import process_page


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
    page4_urls = [
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

    def test__process_page(self):
        with open("./bookstoscrape/tests/page1.html", "rb") as f1:
            page1 = f1.read()
        with open("./bookstoscrape/tests/page4.html", "rb") as f4:
            page4 = f4.read()

        self.assertEqual(process_page(page1, "https://books.toscrape.com/"), self.page1_urls)
        self.assertEqual(process_page(page4, "https://books.toscrape.com/catalogue/page-4.html"), self.page4_urls)


